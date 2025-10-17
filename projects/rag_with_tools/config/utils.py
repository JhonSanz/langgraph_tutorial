from typing import Optional, Dict, Any
from config.settings import DATA_SOURCES


def get_source_config(selected_source: str, db_type: str) -> Optional[Dict[str, Any]]:
    """
    Find and return the configuration for a given data source.

    Args:
        selected_source: Name of the data source to find
        db_type: Type of database ("sql" or "mongodb")

    Returns:
        Source configuration dict if found, None otherwise
    """
    sources = DATA_SOURCES.get(db_type, [])
    for source in sources:
        if source["name"] == selected_source:
            return source
    return None
