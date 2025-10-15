from langgraph.prebuilt import tools_condition, ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tools.sqlite_tool import get_schema_from_sqlite
from projects.rag_with_tools.tools.sqlite_tool import db_tool
from projects.rag_with_tools.tools.rag_tool import rag_tool
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


class RouteDecision(BaseModel):
    route: str = Field(description="Must be either 'expert_sql' or 'expert_nosql'")
    source: str = Field(description="Name of the selected data source")


db_tools = [db_tool]
rag_tools = [rag_tool]


def data_router(state: GraphState):
    user_query = next((m for m in state["messages"] if isinstance(m, HumanMessage)), None)
    query_text = user_query.content if user_query else ""

    catalog_str = ""
    for engine, sources in DATA_SOURCES.items():
        for s in sources:
            catalog_str += f"- {s['name']} ({engine}): {s.get('description', 'No description')}\n"

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
        model="gpt-4o-mini",
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    # Opción 1: Structured output
    structured_llm = llm.with_structured_output(RouteDecision)
    
    # Invoca con el prompt mejorado
    result = structured_llm.invoke([
        SystemMessage(content=instruction),
        HumanMessage(content=query_text)
    ])

    return {
        "route": result.route,
        "selected_source": result.source
    }

def expert_sql(state: GraphState):
    db_schema = get_schema_from_sqlite()
    instruction  = f"""
    You are an expert tasked to query a database given the following schema. You HAVE TO generate the query, based on this:

    {db_schema}

    IMPORTANT:
    - If you don't find useful data or it's empty, output the text 'expert_rag' (to delegate).
    - If you generate a valid SQL query, call the tool.
    - If you have the answer, output it directly and end (route 'done').
    """
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(db_tools)
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    response = {
        "messages": [ai_msg] 
    }
    if "expert_rag" in ai_msg.content.lower():
        response["route"] = "expert_rag"
    elif ai_msg.tool_calls:
        response["route"] = "database_tools"
    else:
        response["route"] = END
    return response

def expert_nosql(state: GraphState):
    pass

def expert_rag(state: GraphState):
    user_query = next((msg for msg in state["messages"] if isinstance(msg, HumanMessage)), None)
    if user_query is None:
        clean_history = state["messages"] 
    else:
        clean_history = [user_query]

    instruction = "You are a helpful assistant tasked to query the chromaDB database to find the answer"
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(rag_tools)
    return {"messages": [llm_with_tools.invoke([sys_msg] + clean_history)]}


def database_condition(state: GraphState):
    route = state.get("route", END)
    return route


builder = StateGraph(GraphState)

builder.add_node("expert_sql", expert_sql)
builder.add_node("expert_nosql", expert_nosql)
builder.add_node("expert_rag", expert_rag)

builder.add_node("database_tools", ToolNode(db_tools))
builder.add_node("rag_tools", ToolNode(rag_tools))


builder.add_conditional_edges(
    "expert_sql",
    database_condition,
)
builder.add_conditional_edges(
    "expert_rag",
    tools_condition,
    {"tools": "rag_tools", "__end__": END},
)

builder.add_edge("database_tools", "expert_sql")
builder.add_edge("rag_tools", "expert_rag")

builder.set_entry_point("expert_sql")

graph = builder.compile()


# mermaid_code = graph.get_graph().draw_mermaid()
# print(mermaid_code)


result = graph.invoke(
    {"messages": [HumanMessage(content="How much we made with product A sales?")]}
)

print("\n=== Resultados finales ===")
for msg in result["messages"]:
    msg.pretty_print()

# https://chatgpt.com/c/68dedacb-2ea0-8326-9a4c-8fb83315c530