from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from utils.inspect_schema_db import get_schema_from_sqlite
from utils.db_tool import db_tool
from utils.rag_tool import rag_tool
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    route: str

db_tools = [db_tool]
rag_tools = [rag_tool]


def expert_database(state: MessagesState):
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
        response["route"] = "check_tools"
    else:
        response["route"] = "done"
    
    return response

def expert_rag(state: MessagesState):
   instruction = "You are a helpful assistant tasked to query the chromaDB database to find the answer"
   sys_msg = SystemMessage(content=instruction)
   llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(rag_tools)
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


def database_condition(state: MessagesState):
    route = state.get("route", "done")

    if route == "expert_rag":
        return "expert_rag"
    elif route == "done":
        return "__end__"
    return "check_tools"


builder = StateGraph(GraphState)

builder.add_node("expert_database", expert_database)
builder.add_node("expert_rag", expert_rag)

builder.add_node("database_tools", ToolNode(db_tools))
builder.add_node("rag_tools", ToolNode(rag_tools))


builder.add_conditional_edges(
    "expert_database",
    database_condition,
    {
        "check_tools": "database_tools", 
        "expert_rag": "expert_rag",      
        "__end__": END,                  
    },
)
builder.add_conditional_edges(
    "expert_rag",
    tools_condition,
    {"tools": "rag_tools", "__end__": END},
)

builder.add_edge("database_tools", "expert_database")
builder.add_edge("rag_tools", "expert_rag")

builder.set_entry_point("expert_database")

graph = builder.compile()


# mermaid_code = graph.get_graph().draw_mermaid()
# print(mermaid_code)


result = graph.invoke(
    {"messages": [HumanMessage(content="How much we made with product A sales?")]}
)

print("\n=== Resultados finales ===")
for msg in result["messages"]:
    msg.pretty_print()