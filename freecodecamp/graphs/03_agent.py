from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    name: str
    age: str
    final: str

def first_node(state: AgentState) -> AgentState:
    """First node in the state graph."""
    state["final"] = f"Hi {state['name']}"
    return state


def second_node(state: AgentState) -> AgentState:
    """Second node in the state graph."""
    state["final"] = state["final"] + f" You are {state['age']} years old."
    return state



graph = StateGraph(AgentState)
graph.add_node("first", first_node)
graph.add_node("second", second_node)

graph.add_edge(START, "first")
graph.add_edge("first", "second")
graph.add_edge("second", END)
app = graph.compile()

# print(app.get_graph().draw_mermaid())

result = app.invoke({"name": "Alice", "age": "30"})
print(result)
