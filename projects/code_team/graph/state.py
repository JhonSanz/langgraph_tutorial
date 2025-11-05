from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    backend_stack: str
    frontend_stack: str
    project_name: str
    # Paths compartidos entre nodos
    user_stories_dir: str
    sprint_planning_dir: str
    backend_output_dir: str
    frontend_output_dir: str
