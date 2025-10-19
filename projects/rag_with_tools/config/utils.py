from typing import Optional, Dict, Any, List
from config.settings import DATA_SOURCES, MAX_RETRIES
from langchain_core.messages import HumanMessage, AnyMessage


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


def get_user_query(messages: List[AnyMessage]) -> Optional[HumanMessage]:
    """
    Extract the user's query from the message history.

    Args:
        messages: List of messages from the conversation

    Returns:
        First HumanMessage found, or None if not found
    """
    return next((m for m in messages if isinstance(m, HumanMessage)), None)


def is_result_empty(content: str) -> bool:
    """
    Check if database result is empty.

    Args:
        content: Tool result content as string

    Returns:
        True if result is empty, False otherwise
    """
    if not content:
        return True

    content_lower = content.lower()
    empty_indicators = ["[]", "{}", "()", "none"]

    return content in empty_indicators or content_lower == "none"


def has_error(content: str) -> bool:
    """
    Check if database result contains an error.

    Args:
        content: Tool result content as string

    Returns:
        True if content indicates an error, False otherwise
    """
    content_lower = content.lower()
    error_indicators = ["error", "no results", "empty", "no rows"]

    return any(indicator in content_lower for indicator in error_indicators)
