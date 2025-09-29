from langchain_core.tools import tool


@tool
def rag_tool(self, query: str) -> str:
    answer = "There were sold 40 products. We made 50 bucks last month"
    return answer