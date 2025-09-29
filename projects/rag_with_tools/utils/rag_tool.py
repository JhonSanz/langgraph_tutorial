from langchain_core.tools import tool


@tool
def rag_tool(prompt: str) -> str:
    """
    Queries products vector database given a prompt as string

    Parameters:
        - prompt: str
    """
    answer = "There were sold 40 products. We made 50 bucks last month"
    return answer
