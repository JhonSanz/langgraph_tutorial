from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    message: str


def greeting_node(state: AgentState) -> AgentState:
    """Simple node that adds a greeting message to the state."""
    state["message"] = "Hey " + state["message"] + ", welcome to the agent!"
    return state


graph = StateGraph(AgentState)
graph.add_node("greeting", greeting_node)


graph.add_edge(START, "greeting")
graph.add_edge("greeting", END)
app = graph.compile()

# print(app.get_graph().draw_mermaid())

result = app.invoke({"message": "Alice"})
print(result["message"])