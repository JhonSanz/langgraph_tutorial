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
    # Get the selected data source from state
    selected_source = state.get("selected_source", "")

    if not selected_source:
        return {
            "messages": [
                SystemMessage(
                    content="❌ Error: No se especificó una fuente de datos en el state"
                )
            ],
            "route": END,
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
            "route": END,
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
            "route": END,
        }

    # Set the connector globally for the db_tool
    set_sql_connector(connector)

    # Get database type and schema
    db_type: str = source_config["type"]
    db_schema: str = source_config.get("schema", connector.get_schema())

    instruction = f"""
    You are an expert tasked to query a {db_type.upper()} database given the following schema. You HAVE TO generate the query, based on this:

    {db_schema}

    IMPORTANT:
    - If you don't find useful data or it's empty, output the text 'expert_rag' (to delegate).
    - If you generate a valid SQL query, call the tool.
    - If you have the answer, output it directly and end (route 'done').
    - Use {db_type.upper()} syntax for your queries.
    """
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(sql_db_tools)
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    response = {"messages": [ai_msg]}
    if "expert_rag" in ai_msg.content.lower():
        response["route"] = "expert_rag"
    elif ai_msg.tool_calls:
        response["route"] = "sql_db_tools"
    else:
        response["route"] = END
    return response


def expert_nosql(state: GraphState):
    pass


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


builder = StateGraph(GraphState)

# NODES
builder.add_node("data_router", data_router)
builder.add_node("expert_sql", expert_sql)
builder.add_node("expert_nosql", expert_nosql)
builder.add_node("expert_rag", expert_rag)

# TOOLS
builder.add_node("sql_db_tools", ToolNode(sql_db_tools))
builder.add_node("nosql_db_tools", ToolNode(nosql_db_tools))
builder.add_node("rag_tools", ToolNode(rag_tools))


builder.add_conditional_edges(
    "data_router",
    lambda state: state.get("route", END),
    {
        "expert_sql": "expert_sql",
        "expert_nosql": "expert_nosql",
    }
)
builder.add_conditional_edges(
    "expert_sql",
    tools_condition,
    {"tools": "sql_db_tools", "__end__": END},
)
builder.add_conditional_edges(
    "expert_nosql",
    tools_condition,
    {"tools": "nosql_db_tools", "__end__": END},
)
builder.add_conditional_edges(
    "expert_rag",
    tools_condition,
    {"tools": "rag_tools", "__end__": END},
)

builder.add_edge("sql_db_tools", "expert_sql")
builder.add_edge("nosql_db_tools", "expert_nosql")
builder.add_edge("rag_tools", "expert_rag")

builder.set_entry_point("data_router")

graph = builder.compile()


# mermaid_code = graph.get_graph().draw_mermaid()
# print(mermaid_code)


# result = graph.invoke(
#     {"messages": [HumanMessage(content="How much we made with product A sales?")]}
# )

# print("\n=== Resultados finales ===")
# for msg in result["messages"]:
#     msg.pretty_print()

# https://chatgpt.com/c/68dedacb-2ea0-8326-9a4c-8fb83315c530
