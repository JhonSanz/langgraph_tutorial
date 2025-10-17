from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, Field


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    route: str
    selected_source: str  # Track which data source was selected
    retry_count: int  # Track retry attempts for database queries


class RouteDecision(BaseModel):
    route: str = Field(description="Must be either 'expert_sql' or 'expert_nosql'")
    source: str = Field(description="Name of the selected data source")
