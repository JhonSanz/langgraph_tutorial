from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from graph.state import GraphState
from config import DATA_SOURCES, get_source_config, get_retry_context, DEFAULT_LLM_MODEL
from tools.sql_tool import sql_db_tool, set_sql_connector
from tools.sql_connector import get_sql_connector_from_datasource


def expert_sql(state: GraphState):
    """
    SQL database expert node that generates and executes SQL queries.

    This node analyzes the user's query and generates appropriate SQL commands
    for the selected database (PostgreSQL, MySQL, or SQLite). It uses the LLM
    to create syntactically correct queries based on the database schema.

    Args:
        state (GraphState): Current graph state containing:
            - messages: Conversation history
            - selected_source: Name of the SQL data source to query
            - retry_count: Number of retry attempts made

    Returns:
        dict: Updated state with:
            - messages: List containing the AI message with tool calls
            - retry_count: Incremented retry counter
            - route: Next node to execute ("sql_db_tools" or "db_result_evaluator")

    Raises:
        Returns error response if:
            - Source configuration not found in datasources.yaml
            - Database connector creation fails
    """
    # Get the selected data source from state
    selected_source = state.get("selected_source", "")
    retry_count = state.get("retry_count", 0)

    # Find the source config
    source_config = get_source_config(selected_source, "sql")
    if not source_config:
        return {
            "messages": [
                SystemMessage(
                    content=f"Error: No se encontró la fuente de datos SQL '{selected_source}' en datasources.yaml"
                )
            ],
        }

    # Create connector using the helper function
    connector = get_sql_connector_from_datasource(selected_source, DATA_SOURCES)
    if connector is None:
        return {
            "messages": [
                SystemMessage(content=f"Error: No se pudo crear el conector para '{selected_source}'")
            ],
        }

    # Set the connector globally for the db_tool
    set_sql_connector(connector)

    # Get database type and schema
    db_type: str = source_config["type"]
    db_schema: str = source_config.get("schema", connector.get_schema())

    # Add context about retries if this is a retry
    retry_context = get_retry_context(retry_count)

    instruction = f"""
    You are an expert tasked to query a {db_type.upper()} database given the following schema. You HAVE TO generate the query, based on this:

    {db_schema}

    IMPORTANT:
    - Generate a valid SQL query and call the tool to execute it.
    - Use {db_type.upper()} syntax for your queries.
    - Be precise and avoid syntax errors.{retry_context}
    """
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model=DEFAULT_LLM_MODEL).bind_tools([sql_db_tool])
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    return {"messages": [ai_msg], "retry_count": retry_count + 1}
