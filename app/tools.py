from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

travily_tool = TavilySearch(max_results=2)
