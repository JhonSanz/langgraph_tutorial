from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    number1: int
    number2: int
    operation: str
    result: int


def adder(state: AgentState) -> AgentState:
    """This node adds 2 numbers"""
    state["result"] = state["number1"] + state["number2"]
    return state


def subtractor(state: AgentState) -> AgentState:
    """This node subtracts 2 numbers"""
    state["result"] = state["number1"] - state["number2"]
    return state


def decide_next_node(state: AgentState) -> str:
    """Decides the next node based on the operation.

    Aqui se retorna el nombre de un edge, no un nodo
    """
    if state["operation"] == "+":
        return "addition_operation"
    elif state["operation"] == "-":
        return "subtraction_operation"
    return "first"


graph = StateGraph(AgentState)
graph.add_node("add_node", adder)
graph.add_node("substract_node", subtractor)
graph.add_node("router", lambda state: state)

graph.add_edge(START, "router")
graph.add_conditional_edges(
    "router",
    decide_next_node,
    # Edge: Node
    {"addition_operation": "add_node", "subtraction_operation": "substract_node"},
)
graph.add_edge("add_node", END)
graph.add_edge("substract_node", END)
app = graph.compile()
# print(app.get_graph().draw_mermaid())

initial_state = AgentState(number1=5, number2=3, operation="+", result=0)
result = app.invoke(initial_state)
print(result)
