from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from graph.state import GraphState
from tools.rag_tool import rag_tool
from config import DEFAULT_LLM_MODEL, get_user_query


def expert_rag(state: GraphState):
    """
    RAG (Retrieval-Augmented Generation) expert node that queries ChromaDB.

    This node uses a vector database (ChromaDB) to retrieve relevant documents
    based on the user's query. It's used as a fallback when database queries fail
    or when the question requires knowledge from unstructured documents.

    Args:
        state (GraphState): Current graph state containing:
            - messages: Conversation history

    Returns:
        dict: Updated state with:
            - messages: List containing the AI message with tool calls

    Note:
        This node only uses the user's query (not full history) to avoid
        context pollution when searching the vector database.
    """
    # Extract only the user query for cleaner vector search
    user_query = get_user_query(state["messages"])
    if user_query is None:
        clean_history = state["messages"]
    else:
        clean_history = [user_query]

    instruction = """You are a helpful assistant tasked to query the ChromaDB vector database to find relevant information.

    IMPORTANT:
    - Use the rag_tool to search for documents related to the user's query.
    - The tool will return the most relevant documents from the knowledge base.
    - Be precise in your search query to get the best results."""

    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model=DEFAULT_LLM_MODEL).bind_tools([rag_tool])
    ai_msg = llm_with_tools.invoke([sys_msg] + clean_history)

    return {"messages": [ai_msg]}
