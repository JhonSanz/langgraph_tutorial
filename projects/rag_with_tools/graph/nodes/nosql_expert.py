from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from graph.state import GraphState
from config import get_source_config, get_retry_context, Routes, DEFAULT_LLM_MODEL
from tools.mongo_tool import mongo_tool


def expert_nosql(state: GraphState):
    """
    NoSQL (MongoDB) database expert node that generates and executes MongoDB queries.

    This node analyzes the user's query and generates appropriate MongoDB commands
    for the selected database. It uses the LLM to create syntactically correct
    queries based on the collection schemas and database metadata.

    Args:
        state (GraphState): Current graph state containing:
            - messages: Conversation history
            - selected_source: Name of the MongoDB data source to query
            - retry_count: Number of retry attempts made

    Returns:
        dict: Updated state with:
            - messages: List containing the AI message with tool calls
            - retry_count: Incremented retry counter
            - route: Next node to execute ("nosql_db_tools" or "db_result_evaluator")

    Raises:
        Returns error response if:
            - Source configuration not found in datasources.yaml
    """
    # Get the selected data source from state
    selected_source = state.get("selected_source", "")
    retry_count = state.get("retry_count", 0)

    # Find the source config
    source_config = get_source_config(selected_source, "mongodb")
    if not source_config:
        return {
            "messages": [
                SystemMessage(
                    content=f"❌ Error: No se encontró la fuente de datos NoSQL '{selected_source}' en datasources.yaml"
                )
            ],
            "route": Routes.EVALUATOR,
        }

    # Get MongoDB metadata
    database = source_config.get("database", "")
    collections = source_config.get("collections", [])
    schema_info = source_config.get("schema", "No schema provided")

    # Add context about retries if this is a retry
    retry_context = get_retry_context(retry_count)

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
    llm_with_tools = ChatOpenAI(model=DEFAULT_LLM_MODEL).bind_tools([mongo_tool])
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    response = {"messages": [ai_msg], "retry_count": retry_count + 1}

    if ai_msg.tool_calls:
        # Has tool calls, execute them
        response["route"] = Routes.NOSQL_TOOLS
    else:
        # No tool calls, go to evaluator
        response["route"] = Routes.EVALUATOR

    return response
