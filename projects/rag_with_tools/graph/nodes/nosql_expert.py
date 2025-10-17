from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from graph.state import GraphState
from config import DATA_SOURCES, MAX_RETRIES
from tools.mongo_tool import mongo_tool


def expert_nosql(state: GraphState):
    """NoSQL expert that can retry queries up to MAX_RETRIES times."""
    # Get the selected data source from state
    selected_source = state.get("selected_source", "")
    retry_count = state.get("retry_count", 0)

    if not selected_source:
        return {
            "messages": [
                SystemMessage(
                    content="❌ Error: No se especificó una fuente de datos en el state"
                )
            ],
            "route": "db_result_evaluator",
        }

    # Find the source config
    source_config = None
    for source in DATA_SOURCES.get("mongodb", []):
        if source["name"] == selected_source:
            source_config = source
            break

    if not source_config:
        return {
            "messages": [
                SystemMessage(
                    content=f"❌ Error: No se encontró la fuente de datos NoSQL '{selected_source}' en datasources.yaml"
                )
            ],
            "route": "db_result_evaluator",
        }

    # Get MongoDB metadata
    database = source_config.get("database", "")
    collections = source_config.get("collections", [])
    schema_info = source_config.get("schema", "No schema provided")

    # Add context about retries if this is a retry
    retry_context = ""
    if retry_count > 0:
        retry_context = f"\n\nNOTE: This is retry attempt {retry_count}/{MAX_RETRIES}. The previous query may have failed or returned no results. Try a different approach or query."

    instruction = f"""
    You are an expert tasked to query a MongoDB database.

    Database: {database}
    Available collections: {', '.join(collections)}
    Schema information: {schema_info}

    IMPORTANT:
    - Generate a valid MongoDB query and call the mongo_tool to execute it.
    - The mongo_tool requires: database name, collection name, and query as JSON string.
    - Use proper MongoDB query syntax (e.g., {{"field": "value"}}).
    - Be precise and avoid syntax errors.{retry_context}
    """
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools([mongo_tool])
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    # Increment retry count
    new_retry_count = retry_count + 1

    response = {"messages": [ai_msg], "retry_count": new_retry_count}

    if ai_msg.tool_calls:
        # Has tool calls, execute them
        response["route"] = "nosql_db_tools"
    else:
        # No tool calls, go to evaluator
        response["route"] = "db_result_evaluator"

    return response
