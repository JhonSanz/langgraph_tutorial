from typing import Optional, Dict, Any
from config.settings import DATA_SOURCES, MAX_RETRIES


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


def get_retry_context(retry_count: int) -> str:
    """
    Generate retry context message for LLM prompt.

    Args:
        retry_count: Current retry attempt number

    Returns:
        Context message string for retries, or empty string if first attempt
    """
    if retry_count > 0:
        return f"\n\nNOTE: This is retry attempt {retry_count}/{MAX_RETRIES}. The previous query may have failed or returned no results. Try a different approach or query."
    return ""
