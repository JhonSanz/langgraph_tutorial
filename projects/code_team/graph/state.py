from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
