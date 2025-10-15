from langchain_core.tools import tool
from projects.rag_with_tools.tools.sql_connector import SQLConnector
from typing import Optional

# Global variable to hold the current connector instance
_current_connector: Optional[SQLConnector] = None


def set_sql_connector(connector: SQLConnector):
    """Set the global SQL connector instance."""
    global _current_connector
    _current_connector = connector


def get_sql_connector() -> Optional[SQLConnector]:
    """Get the current SQL connector instance."""
    return _current_connector


@tool
def db_tool(query: str) -> str:
    """
    Queries SQL database (SQLite, PostgreSQL, or MySQL) given a SQL query as string.

    This tool supports multiple database types and will use the currently configured connector.

    Parameters:
        - query: str - A SELECT SQL query to execute

    Returns:
        - str - Query results as string representation
    """
    connector = get_sql_connector()

    if connector is None:
        return "❌ Error: No hay conexión a base de datos configurada."

    results = connector.execute_query(query)

    # Check for errors in results
    if results and "error" in results[0]:
        return results[0]["error"]

    # Check for messages
    if results and "message" in results[0]:
        return results[0]["message"]

    # Return successful results
    return str(results)
