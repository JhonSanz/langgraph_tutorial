from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    backend_stack: str = ""
    frontend_stack: str = "React, TailwindCSS, Zustand"
    project_name: str = "FastAPI, PostgreSQL, SQLAlchemy"
