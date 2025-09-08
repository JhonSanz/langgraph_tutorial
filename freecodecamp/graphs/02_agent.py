from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    values: list[int]
    name: str
    result: str


def process_values(state: AgentState) -> AgentState:
    """This function handles multiple different values"""
    print(state)
    state["result"] = f"Hi there! {state['name']}. Your sum = {sum(state['values'])}"
    print(state)
    return state


graph = StateGraph(AgentState)
graph.add_node("processor", process_values)


graph.add_edge(START, "processor")
graph.add_edge("processor", END)
app = graph.compile()

# print(app.get_graph().draw_mermaid())

result = app.invoke({"values": [1,2,3,4], "name": "Alice"})
print(result)
