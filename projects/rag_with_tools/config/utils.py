from typing import Optional, Dict, Any
from langchain_core.messages import SystemMessage
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


def create_error_response(error_message: str, route: str = "db_result_evaluator") -> Dict[str, Any]:
    """
    Create a standardized error response for the graph.

    Args:
        error_message: The error message to include
        route: The route to go to after the error (default: db_result_evaluator)

    Returns:
        Dictionary with messages and route
    """
    return {
        "messages": [SystemMessage(content=f"❌ Error: {error_message}")],
        "route": route,
    }
