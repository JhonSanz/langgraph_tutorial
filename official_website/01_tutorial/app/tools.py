from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from langgraph.types import interrupt
from langchain_core.tools import tool

load_dotenv()

travily_tool = TavilySearch(max_results=2)


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]
