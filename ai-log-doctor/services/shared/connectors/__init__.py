"""SIEM connectors package."""
from .base import BaseSIEMConnector
from .elastic import ElasticConnector
from .wazuh import WazuhConnector
from .splunk import SplunkConnector
from .qradar import QRadarConnector
from typing import Dict, Any


CONNECTOR_MAP = {
    "elastic": ElasticConnector,
    "wazuh": WazuhConnector,
    "splunk": SplunkConnector,
    "qradar": QRadarConnector,
}


def get_connector(platform: str, config: Dict[str, Any]) -> BaseSIEMConnector:
    """Factory function to get appropriate connector."""
    connector_class = CONNECTOR_MAP.get(platform.lower())
    if not connector_class:
        raise ValueError(f"Unsupported platform: {platform}")
    return connector_class(config)


__all__ = [
    "BaseSIEMConnector",
    "ElasticConnector",
    "WazuhConnector",
    "SplunkConnector",
    "QRadarConnector",
    "get_connector",
    "CONNECTOR_MAP",
]
