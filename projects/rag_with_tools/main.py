from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from rag_with_tools.utils.inspect_schema_db import get_schema_from_sqlite
from rag_with_tools.utils.db_tool import db_tool
from rag_with_tools.utils.rag_tool import rag_tool

load_dotenv()


tools = [db_tool, rag_tool]


llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)


def expert_database(state: MessagesState):
    db_schema = get_schema_from_sqlite()
    instruction  = f"""
    You are an expert tasked to query a database given the following schema
    {db_schema}
    """
    sys_msg = SystemMessage(content=instruction)
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

def expert_rag(state: MessagesState):
   instruction = "You are a helpful assistant tasked to query the chromaDB database to find the answer"
   sys_msg = SystemMessage(content=instruction)
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

def human_call(state: MessagesState):
   return

class GraphState(MessagesState):
    pass

builder = StateGraph(GraphState)

builder.add_node("expert_database", expert_database)
builder.add_node("expert_rag", expert_rag)
builder.add_node("database_tools", ToolNode(tools))
builder.add_node("rag_tools", ToolNode(tools))

builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

builder.set_entry_point("assistant")

graph = builder.compile()

for event in graph.stream(
    {"messages": [{"role": "user", "content": "suma 3 + 5"}]},
    stream_mode="updates"
):
    print(event["messages"][0].pretty_print())
