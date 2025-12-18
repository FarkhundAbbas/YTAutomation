"""Base connector interface for SIEM platforms."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaseSIEMConnector(ABC):
    """Abstract base class for SIEM connectors."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize connector with configuration."""
        self.config = config
        self.base_url = config.get("base_url", "")
        self.credentials = config.get("credentials", {})
        
    @abstractmethod
    async def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the SIEM platform."""
        pass
    
    @abstractmethod
    async def fetch_logs(
        self,
        query: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch logs from the SIEM platform."""
        pass
    
    @abstractmethod
    async def apply_parser(self, parser_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a parser/decoder to the SIEM platform."""
        pass
    
    @abstractmethod
    async def validate_parser(
        self,
        parser_config: Dict[str, Any],
        test_logs: List[str]
    ) -> Dict[str, Any]:
        """Validate a parser against test logs (dry-run)."""
        pass
    
    @abstractmethod
    async def rollback_parser(self, parser_id: str) -> Dict[str, Any]:
        """Rollback a parser to a previous version."""
        pass
