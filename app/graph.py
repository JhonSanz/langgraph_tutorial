from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from app.tools import travily_tool
from app.utils import BasicToolNode
from app.schemas import State
from app.edges import route_tools

graph_builder = StateGraph(State)
tools = [travily_tool]

llm = init_chat_model("openai:gpt-4.1")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", BasicToolNode(tools=tools))

graph_builder.add_edge(START, "chatbot")       # entrada → chatbot
graph_builder.add_edge("tools", "chatbot")     # al terminar tool → chatbot
graph_builder.add_edge("chatbot", END)         # chatbot puede terminar

graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {"tools": "tools", END: END},  # Mapa de resoluciones
)

graph = graph_builder.compile()
