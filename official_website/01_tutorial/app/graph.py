from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from app.tools import travily_tool, human_assistance
from app.utils import BasicToolNode
from app.schemas import State
from app.edges import route_tools
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

memory = InMemorySaver()
graph_builder = StateGraph(State)
tools = [travily_tool, human_assistance]

llm = init_chat_model("openai:gpt-4.1")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # Because we will be interrupting during tool execution,
    # we disable parallel tool calling to avoid repeating any
    # tool invocations when we resume.

    # Aqui se tiene un nodo con 2 tools, lo cual puede causar problemas con el paralelismo.
    # se recomienda hacer el HITL (Human In The Loop) en un nodo separado.
    # algo así como un grafo de expertos por nodo
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", BasicToolNode(tools=tools))

graph_builder.add_edge(START, "chatbot")  # entrada → chatbot
graph_builder.add_edge("tools", "chatbot")  # al terminar tool → chatbot
graph_builder.add_edge("chatbot", END)  # chatbot puede terminar

graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {"tools": "tools", END: END},  # Mapa de resoluciones
)

graph = graph_builder.compile(checkpointer=memory)
