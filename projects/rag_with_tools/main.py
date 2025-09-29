from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from utils.inspect_schema_db import get_schema_from_sqlite
from utils.db_tool import db_tool
from utils.rag_tool import rag_tool

load_dotenv()


class GraphState(MessagesState):
    route: str

db_tools = [db_tool]
rag_tools = [rag_tool]

llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(db_tools + rag_tools)


def expert_database(state: MessagesState):
    db_schema = get_schema_from_sqlite()
    instruction  = f"""
    You are an expert tasked to query a database given the following schema
    {db_schema}

    IMPORTANT if you don't find useful data or it's empty answer as output 'expert_rag', to delegate
    the task to other agent.
    """
    sys_msg = SystemMessage(content=instruction)
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    if "expert_rag" in ai_msg.content.lower():        
        return {"messages": [ai_msg], "route": "expert_rag"}

    return {"messages": [ai_msg], "route": "done"}

def expert_rag(state: MessagesState):
   instruction = "You are a helpful assistant tasked to query the chromaDB database to find the answer"
   sys_msg = SystemMessage(content=instruction)
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


def human_call(state: MessagesState):
   return


def database_condition(state: MessagesState):
    route = state.get("route", "done")
    return route


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
mermaid_code = graph.get_graph().draw_mermaid()
print(mermaid_code)