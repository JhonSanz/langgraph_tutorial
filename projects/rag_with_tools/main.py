from langgraph.prebuilt import tools_condition, ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tools.sql_tool import sql_db_tool, set_sql_connector
from tools.mongo_tool import mongo_tool
from tools.sql_connector import (
    SQLConnector,
    get_sql_connector_from_datasource,
)
from tools.rag_tool import rag_tool
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
import yaml
from pathlib import Path

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "datasources.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    DATA_SOURCES = yaml.safe_load(f)


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    route: str
    selected_source: str  # Track which data source was selected
    retry_count: int  # Track retry attempts for database queries


class RouteDecision(BaseModel):
    route: str = Field(description="Must be either 'expert_sql' or 'expert_nosql'")
    source: str = Field(description="Name of the selected data source")


sql_db_tools = [sql_db_tool]
nosql_db_tools = [mongo_tool]
rag_tools = [rag_tool]


def data_router(state: GraphState):
    user_query = next(
        (m for m in state["messages"] if isinstance(m, HumanMessage)), None
    )
    query_text = user_query.content if user_query else ""

    catalog_str = ""
    for engine, sources in DATA_SOURCES.items():
        for s in sources:
            catalog_str += (
                f"- {s['name']} ({engine}): {s.get('description', 'No description')}\n"
            )

    instruction = f"""
You are a routing agent for a data query system. Analyze the user's query and select the most appropriate data source.

User query: "{query_text}"

Available sources:
{catalog_str}

ROUTING RULES:
- If the best source uses SQL database → return route: "expert_sql"
- If the best source uses MongoDB/NoSQL database → return route: "expert_nosql"

You MUST respond with valid JSON containing:
- "route": the expert type (expert_sql or expert_nosql)
- "source": the exact name of the data source

Example response:
{{"route": "expert_sql", "source": "users_db"}}
"""

    # Opción 3: JSON mode
    llm = ChatOpenAI(
        model="gpt-4o-mini", model_kwargs={"response_format": {"type": "json_object"}}
    )

    # Opción 1: Structured output
    structured_llm = llm.with_structured_output(RouteDecision)

    # Invoca con el prompt mejorado
    result = structured_llm.invoke(
        [SystemMessage(content=instruction), HumanMessage(content=query_text)]
    )

    return {"route": result.route, "selected_source": result.source}


def expert_sql(state: GraphState):
    """SQL expert that can retry queries up to MAX_RETRIES times."""
    MAX_RETRIES = 2

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

    # Find the source config first
    source_config = None
    for source in DATA_SOURCES.get("sql", []):
        if source["name"] == selected_source:
            source_config = source
            break

    if not source_config:
        return {
            "messages": [
                SystemMessage(
                    content=f"❌ Error: No se encontró la fuente de datos SQL '{selected_source}' en datasources.yaml"
                )
            ],
            "route": "db_result_evaluator",
        }

    # Create connector using the helper function
    connector = get_sql_connector_from_datasource(selected_source, DATA_SOURCES)

    if connector is None:
        return {
            "messages": [
                SystemMessage(
                    content=f"❌ Error: No se pudo crear el conector para '{selected_source}'"
                )
            ],
            "route": "db_result_evaluator",
        }

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
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(sql_db_tools)
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


def expert_nosql(state: GraphState):
    """NoSQL expert that can retry queries up to MAX_RETRIES times."""
    MAX_RETRIES = 2

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
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(nosql_db_tools)
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


def db_result_evaluator(state: GraphState):
    """Evaluates database query results and decides whether to retry, go to RAG, or end."""
    MAX_RETRIES = 2

    messages = state["messages"]
    retry_count = state.get("retry_count", 0)

    # Find the last tool message (database result)
    last_tool_msg = None
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'tool':
            last_tool_msg = msg
            break

    # If no tool message found, check if there's an error message
    if not last_tool_msg:
        # Check if the last message is an error from expert_sql
        last_msg = messages[-1] if messages else None
        if last_msg and isinstance(last_msg, SystemMessage) and "Error" in last_msg.content:
            # Database connection or config error, go to RAG as fallback
            return {"route": "expert_rag"}
        # No tool was called, go to end
        return {"route": END}

    tool_content = str(last_tool_msg.content).strip()

    # Criteria for unsatisfactory results
    is_empty = (
        not tool_content
        or tool_content == "[]"
        or tool_content == "{}"
        or tool_content == "()"
        or tool_content.lower() == "none"
    )
    is_error = "error" in tool_content.lower()
    is_no_results = (
        "no results" in tool_content.lower()
        or "empty" in tool_content.lower()
        or "no rows" in tool_content.lower()
    )

    # If results are clearly unsatisfactory
    if is_empty or is_error or is_no_results:
        # Check if we can retry
        if retry_count < MAX_RETRIES:
            # Retry: go back to the appropriate expert based on selected_source
            source_type = state.get("route", "expert_sql")
            # Extract the expert type from route (could be expert_sql or expert_nosql)
            if "nosql" in source_type:
                return {"route": "expert_nosql"}
            else:
                return {"route": "expert_sql"}
        else:
            # Max retries reached, fallback to RAG
            return {"route": "expert_rag"}

    # Results look good, use LLM to make final evaluation
    user_query = next(
        (m for m in messages if isinstance(m, HumanMessage)), None
    )
    user_question = user_query.content if user_query else "the user's question"

    eval_prompt = f"""You are evaluating database query results.

User's question: {user_question}

Database results: {tool_content}

Determine if these results adequately answer the user's question.
Respond with ONLY one word: "satisfactory" or "unsatisfactory".

If the results contain relevant data that could answer the question, say "satisfactory".
If the results are empty, irrelevant, or don't help answer the question, say "unsatisfactory".
"""

    llm = ChatOpenAI(model="gpt-4o-mini")
    eval_result = llm.invoke([HumanMessage(content=eval_prompt)])

    if "unsatisfactory" in eval_result.content.lower():
        # Check if we can retry
        if retry_count < MAX_RETRIES:
            # Retry
            source_type = state.get("route", "expert_sql")
            if "nosql" in source_type:
                return {"route": "expert_nosql"}
            else:
                return {"route": "expert_sql"}
        else:
            # Max retries reached, fallback to RAG
            return {"route": "expert_rag"}

    # Results are satisfactory, generate final response
    return {"route": "response_generator"}


def expert_rag(state: GraphState):
    user_query = next(
        (msg for msg in state["messages"] if isinstance(msg, HumanMessage)), None
    )
    if user_query is None:
        clean_history = state["messages"]
    else:
        clean_history = [user_query]

    instruction = "You are a helpful assistant tasked to query the chromaDB database to find the answer"
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(rag_tools)
    return {"messages": [llm_with_tools.invoke([sys_msg] + clean_history)]}


def response_generator(state: GraphState):
    """
    Generates a comprehensive final response to the user based on all collected information.
    This node synthesizes data from database queries or RAG results into a clear, complete answer.
    """
    messages = state["messages"]

    # Find the user's original question
    user_query = next(
        (msg for msg in messages if isinstance(msg, HumanMessage)), None
    )
    user_question = user_query.content if user_query else "your question"

    # Collect all relevant information from the conversation
    db_results = []
    rag_results = []
    errors = []

    for msg in messages:
        # Collect database tool results
        if hasattr(msg, 'type') and msg.type == 'tool':
            tool_name = getattr(msg, 'name', 'unknown')
            if 'sql' in tool_name.lower() or 'mongo' in tool_name.lower():
                db_results.append(str(msg.content))
            elif 'rag' in tool_name.lower():
                rag_results.append(str(msg.content))
        # Collect error messages
        elif isinstance(msg, SystemMessage) and "Error" in msg.content:
            errors.append(msg.content)

    # Determine which sources were used
    sources_used = []
    if db_results:
        source_name = state.get("selected_source", "database")
        sources_used.append(f"Database: {source_name}")
    if rag_results:
        sources_used.append("Knowledge base (RAG)")

    # Build context for the LLM
    context_parts = []

    if db_results:
        context_parts.append(f"Database Query Results:\n{chr(10).join(db_results)}")

    if rag_results:
        context_parts.append(f"Knowledge Base Information:\n{chr(10).join(rag_results)}")

    if errors:
        context_parts.append(f"Encountered Issues:\n{chr(10).join(errors)}")

    context = "\n\n".join(context_parts)

    # Generate the final response
    instruction = f"""You are a helpful assistant providing a final answer to the user.

User's Question: {user_question}

Available Information:
{context}

Sources Used: {', '.join(sources_used) if sources_used else 'None'}

Your task:
1. Synthesize all the information provided above
2. Answer the user's question clearly and completely
3. If data came from databases, present it in a readable format (tables, lists, summaries)
4. If the information is insufficient, acknowledge what's missing
5. Be professional and concise
6. At the end, briefly mention which sources were consulted

Provide a complete, well-formatted response."""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    final_response = llm.invoke([
        SystemMessage(content=instruction),
        HumanMessage(content=user_question)
    ])

    return {"messages": [final_response], "route": END}


builder = StateGraph(GraphState)

# NODES
builder.add_node("data_router", data_router)
builder.add_node("expert_sql", expert_sql)
builder.add_node("expert_nosql", expert_nosql)
builder.add_node("expert_rag", expert_rag)
builder.add_node("db_result_evaluator", db_result_evaluator)
builder.add_node("response_generator", response_generator)

# TOOLS
builder.add_node("sql_db_tools", ToolNode(sql_db_tools))
builder.add_node("nosql_db_tools", ToolNode(nosql_db_tools))
builder.add_node("rag_tools", ToolNode(rag_tools))


# EDGES
# Entry point: data_router decides which expert to use
builder.add_conditional_edges(
    "data_router",
    lambda state: state.get("route", END),
    {
        "expert_sql": "expert_sql",
        "expert_nosql": "expert_nosql",
    }
)

# expert_sql can either call tools or go to evaluator
builder.add_conditional_edges(
    "expert_sql",
    lambda state: state.get("route", END),
    {
        "sql_db_tools": "sql_db_tools",
        "db_result_evaluator": "db_result_evaluator",
    }
)

# expert_nosql can either call tools or go to evaluator
builder.add_conditional_edges(
    "expert_nosql",
    lambda state: state.get("route", END),
    {
        "nosql_db_tools": "nosql_db_tools",
        "db_result_evaluator": "db_result_evaluator",
    }
)

# After tools execute, go to evaluator
builder.add_edge("sql_db_tools", "db_result_evaluator")
builder.add_edge("nosql_db_tools", "db_result_evaluator")

# Evaluator decides: retry (go back to expert), fallback to RAG, or go to response generator
builder.add_conditional_edges(
    "db_result_evaluator",
    lambda state: state.get("route", END),
    {
        "expert_sql": "expert_sql",
        "expert_nosql": "expert_nosql",
        "expert_rag": "expert_rag",
        "response_generator": "response_generator",
        "__end__": END,
    }
)

# expert_rag calls RAG tools
builder.add_conditional_edges(
    "expert_rag",
    tools_condition,
    {"tools": "rag_tools", "__end__": END},
)

# After RAG tools, go to response generator to synthesize final answer
builder.add_edge("rag_tools", "response_generator")

# response_generator always ends the graph
builder.add_edge("response_generator", END)

builder.set_entry_point("data_router")

graph = builder.compile()


mermaid_code = graph.get_graph().draw_mermaid()
print(mermaid_code)


# result = graph.invoke(
#     {"messages": [HumanMessage(content="How much we made with product A sales?")]}
# )

# print("\n=== Resultados finales ===")
# for msg in result["messages"]:
#     msg.pretty_print()

# https://chatgpt.com/c/68dedacb-2ea0-8326-9a4c-8fb83315c530
