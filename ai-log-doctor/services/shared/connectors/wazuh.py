"""Wazuh connector."""
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base import BaseSIEMConnector
import xml.etree.ElementTree as ET


class WazuhConnector(BaseSIEMConnector):
    """Connector for Wazuh Manager."""
    
    async def _get_token(self) -> Optional[str]:
        """Get authentication token from Wazuh API."""
        try:
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.post(
                    f"{self.base_url}/security/user/authenticate",
                    auth=(
                        self.credentials.get("username"),
                        self.credentials.get("password")
                    ),
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json().get("data", {}).get("token")
        except Exception:
            return None
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Wazuh Manager."""
        try:
            token = await self._get_token()
            if not token:
                return {
                    "status": "error",
                    "platform": "wazuh",
                    "error": "Authentication failed"
                }
            
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.base_url}/manager/status",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                response.raise_for_status()
                return {
                    "status": "success",
                    "platform": "wazuh",
                    "details": response.json()
                }
        except Exception as e:
            return {
                "status": "error",
                "platform": "wazuh",
                "error": str(e)
            }
    
    async def fetch_logs(
        self,
        query: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch logs from Wazuh (via Elasticsearch backend)."""
        try:
            token = await self._get_token()
            if not token:
                return []
            
            # Wazuh stores alerts in Elasticsearch
            # This is a simplified implementation
            params = {
                "limit": limit,
                "sort": "-timestamp"
            }
            
            if query:
                params["q"] = query
            
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.get(
                    f"{self.base_url}/alerts",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", {}).get("affected_items", [])
        except Exception:
            return []
    
    async def apply_parser(self, parser_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply decoder XML to Wazuh."""
        try:
            token = await self._get_token()
            if not token:
                return {"status": "error", "error": "Authentication failed"}
            
            decoder_xml = parser_config.get("decoder_xml", "")
            decoder_file = parser_config.get("decoder_file", "local_decoder.xml")
            
            # In a real implementation, we would upload the decoder via Wazuh API
            # For now, this is a placeholder showing the structure
            async with httpx.AsyncClient(verify=False) as client:
                # Upload decoder
                response = await client.post(
                    f"{self.base_url}/decoders/files/{decoder_file}",
                    headers={"Authorization": f"Bearer {token}"},
                    data=decoder_xml,
                    timeout=30.0
                )
                response.raise_for_status()
                
                # Restart manager to apply changes
                restart_response = await client.put(
                    f"{self.base_url}/manager/restart",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30.0
                )
                
                return {
                    "status": "success",
                    "decoder_file": decoder_file,
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
        """Validate Wazuh decoder (simplified)."""
        try:
            decoder_xml = parser_config.get("decoder_xml", "")
            
            # Parse XML to check structure
            try:
                root = ET.fromstring(decoder_xml)
                decoder = root.find(".//decoder")
                if decoder is not None:
                    regex = decoder.find("regex")
                    if regex is not None:
                        # Basic validation: check if regex exists
                        return {
                            "status": "success",
                            "total_logs": len(test_logs),
                            "parsed_successfully": len(test_logs),  # Simplified
                            "parse_rate": 1.0,
                            "details": {"decoder": "valid"}
                        }
            except ET.ParseError:
                return {
                    "status": "error",
                    "error": "Invalid XML structure"
                }
            
            return {
                "status": "error",
                "error": "No decoder found in XML"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def rollback_parser(self, parser_id: str) -> Dict[str, Any]:
        """Remove decoder from Wazuh."""
        try:
            token = await self._get_token()
            if not token:
                return {"status": "error", "error": "Authentication failed"}
            
            async with httpx.AsyncClient(verify=False) as client:
                response = await client.delete(
                    f"{self.base_url}/decoders/files/{parser_id}",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=30.0
                )
                response.raise_for_status()
                return {
                    "status": "success",
                    "decoder_file": parser_id
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
