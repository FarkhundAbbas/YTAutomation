"""Elastic Stack connector."""
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseSIEMConnector
import json


class ElasticConnector(BaseSIEMConnector):
    """Connector for Elastic Stack (Elasticsearch)."""
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Elasticsearch."""
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.base_url}/_cluster/health",
                    auth=(
                        self.credentials.get("username"),
                        self.credentials.get("password")
                    ),
                    timeout=10.0
                )
                response.raise_for_status()
                return {
                    "status": "success",
                    "platform": "elastic",
                    "details": response.json()
                }
        except Exception as e:
            return {
                "status": "error",
                "platform": "elastic",
                "error": str(e)
            }
    
    async def fetch_logs(
        self,
        query: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch logs from Elasticsearch."""
        try:
            # Build query
            search_query = {
                "query": {
                    "bool": {
                        "must": []
                    }
                },
                "size": limit,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
            
            if query:
                search_query["query"]["bool"]["must"].append({
                    "query_string": {"query": query}
                })
            
            if start_time or end_time:
                time_range = {}
                if start_time:
                    time_range["gte"] = start_time.isoformat()
                if end_time:
                    time_range["lte"] = end_time.isoformat()
                search_query["query"]["bool"]["must"].append({
                    "range": {"@timestamp": time_range}
                })
            
            async with httpx.AsyncClient(verify=False) as client:
                index_pattern = self.config.get("index_pattern", "*")
                response = await client.post(
                    f"{self.base_url}/{index_pattern}/_search",
                    json=search_query,
                    auth=(
                        self.credentials.get("username"),
                        self.credentials.get("password")
                    ),
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return [hit["_source"] for hit in data.get("hits", {}).get("hits", [])]
        except Exception as e:
            return []
    
    async def apply_parser(self, parser_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an ingest pipeline to Elasticsearch."""
        try:
            pipeline_id = parser_config.get("pipeline_id", f"logdoctor-{datetime.now().timestamp()}")
            pipeline_def = parser_config.get("pipeline", {})
            
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.put(
                    f"{self.base_url}/_ingest/pipeline/{pipeline_id}",
                    json=pipeline_def,
                    auth=(
                        self.credentials.get("username"),
                        self.credentials.get("password")
                    ),
                    timeout=30.0
                )
                response.raise_for_status()
                return {
                    "status": "success",
                    "pipeline_id": pipeline_id,
                    "details": response.json()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def validate_parser(
        self,
        parser_config: Dict[str, Any],
        test_logs: List[str]
    ) -> Dict[str, Any]:
        """Validate parser using Elasticsearch _simulate API."""
        try:
            pipeline_def = parser_config.get("pipeline", {})
            
            # Prepare simulation request
            docs = [{"_source": {"message": log}} for log in test_logs]
            simulate_request = {
                "pipeline": pipeline_def,
                "docs": docs
            }
            
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    f"{self.base_url}/_ingest/pipeline/_simulate",
                    json=simulate_request,
                    auth=(
                        self.credentials.get("username"),
                        self.credentials.get("password")
                    ),
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()
                
                # Analyze results
                total = len(test_logs)
                parsed = sum(1 for doc in result.get("docs", []) if not doc.get("error"))
                
                return {
                    "status": "success",
                    "total_logs": total,
                    "parsed_successfully": parsed,
                    "parse_rate": parsed / total if total > 0 else 0,
                    "details": result
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def rollback_parser(self, parser_id: str) -> Dict[str, Any]:
        """Delete an ingest pipeline."""
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.delete(
                    f"{self.base_url}/_ingest/pipeline/{parser_id}",
                    auth=(
                        self.credentials.get("username"),
                        self.credentials.get("password")
                    ),
                    timeout=30.0
                )
                response.raise_for_status()
                return {
                    "status": "success",
                    "pipeline_id": parser_id
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
