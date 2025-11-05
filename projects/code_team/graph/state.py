from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict, Annotated, NotRequired
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """
    Estado global del grafo que se comparte entre todos los nodos.

    Los campos marcados como NotRequired son opcionales y se van
    poblando a medida que los nodos se ejecutan.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    backend_stack: NotRequired[str]
    frontend_stack: NotRequired[str]
    project_name: NotRequired[str]
    # Paths compartidos entre nodos (se populan durante la ejecución)
    user_stories_dir: NotRequired[str]
    sprint_planning_dir: NotRequired[str]
    backend_output_dir: NotRequired[str]
    frontend_output_dir: NotRequired[str]
