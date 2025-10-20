from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from pathlib import Path

# Global ChromaDB client
_vectorstore = None


def get_vectorstore():
    """Get or create the ChromaDB vectorstore instance."""
    global _vectorstore
    if _vectorstore is None:
        # Define persistent directory
        persist_directory = Path(__file__).parent.parent / "populate/chroma_db"
        persist_directory.mkdir(exist_ok=True)

        # Initialize embeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Create/load vectorstore
        _vectorstore = Chroma(
            collection_name="knowledge_base",
            embedding_function=embeddings,
            persist_directory=str(persist_directory),
        )
    return _vectorstore


@tool
def rag_tool(query: str) -> str:
    """
    Searches the ChromaDB vector database for relevant documents.

    This tool performs semantic search over the knowledge base using
    the provided query. It returns the most relevant documents found.

    Parameters:
        query: The search query to find relevant documents

    Returns:
        Formatted string with relevant documents and their content
    """
    try:
        vectorstore = get_vectorstore()

        # Perform similarity search
        results = vectorstore.similarity_search(query, k=3)

        if not results:
            return "No relevant documents found in the knowledge base."

        # Format results
        formatted_results = []
        for i, doc in enumerate(results, 1):
            metadata = doc.metadata
            content = doc.page_content
            formatted_results.append(
                f"Document {i}:\n"
                f"Content: {content}\n"
                f"Metadata: {metadata}\n"
            )

        return "\n".join(formatted_results)

    except Exception as e:
        return f"Error querying ChromaDB: {str(e)}"
