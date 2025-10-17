from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from graph.state import GraphState
from config import DATA_SOURCES, MAX_RETRIES, get_source_config, create_error_response
from tools.sql_tool import sql_db_tool, set_sql_connector
from tools.sql_connector import get_sql_connector_from_datasource


def expert_sql(state: GraphState):
    """SQL expert that can retry queries up to MAX_RETRIES times."""
    # Get the selected data source from state
    selected_source = state.get("selected_source", "")
    retry_count = state.get("retry_count", 0)

    # Find the source config
    source_config = get_source_config(selected_source, "sql")
    if not source_config:
        return create_error_response(
            f"No se encontró la fuente de datos SQL '{selected_source}' en datasources.yaml"
        )

    # Create connector using the helper function
    connector = get_sql_connector_from_datasource(selected_source, DATA_SOURCES)
    if connector is None:
        return create_error_response(f"No se pudo crear el conector para '{selected_source}'")

    # Set the connector globally for the db_tool
    set_sql_connector(connector)

    # Get database type and schema
    db_type: str = source_config["type"]
    db_schema: str = source_config.get("schema", connector.get_schema())

    # Add context about retries if this is a retry
    retry_context = ""
    if retry_count > 0:
        retry_context = f"\n\nNOTE: This is retry attempt {retry_count}/{MAX_RETRIES}. The previous query may have failed or returned no results. Try a different approach or query."

    instruction = f"""
    You are an expert tasked to query a {db_type.upper()} database given the following schema. You HAVE TO generate the query, based on this:

    {db_schema}

    IMPORTANT:
    - Generate a valid SQL query and call the tool to execute it.
    - Use {db_type.upper()} syntax for your queries.
    - Be precise and avoid syntax errors.{retry_context}
    """
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools([sql_db_tool])
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    # Increment retry count
    new_retry_count = retry_count + 1

    response = {"messages": [ai_msg], "retry_count": new_retry_count}

    if ai_msg.tool_calls:
        # Has tool calls, execute them
        response["route"] = "sql_db_tools"
    else:
        # No tool calls, go to evaluator
        response["route"] = "db_result_evaluator"

    return response
