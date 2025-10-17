from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import GraphState
from tools.rag_tool import rag_tool


def expert_rag(state: GraphState):
    """RAG expert that queries the ChromaDB knowledge base."""
    user_query = next(
        (msg for msg in state["messages"] if isinstance(msg, HumanMessage)), None
    )
    if user_query is None:
        clean_history = state["messages"]
    else:
        clean_history = [user_query]

    instruction = "You are a helpful assistant tasked to query the chromaDB database to find the answer"
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools([rag_tool])
    return {"messages": [llm_with_tools.invoke([sys_msg] + clean_history)]}
