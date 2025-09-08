from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END
import random

class AgentState(TypedDict):
    name: str
    number: list[int]
    counter: int


def greeting_node(state: AgentState) -> AgentState:
    """Greeting Node which says hi to the person"""
    state["name"] = f"Hi, there {state['name']}"
    state['counter'] = 0
    return state

def random_node(state: AgentState) -> AgentState:
    """Generates a random number from 0 to 10"""
    state["number"].append(random.randint(0,10))
    state["counter"] += 1
    return state

def should_contine(state: AgentState) -> AgentState:
    """Function to decide what to do next"""
    if state["counter"] < 5:
        print("NETERING LOOP", state["counter"])
        return "loop"
    else:
        return "exit"
    
graph = StateGraph(AgentState)
graph.add_node("greeting", greeting_node)
graph.add_node("random", random_node)

graph.add_edge(START, "greeting")
graph.add_edge("greeting", "random")

graph.add_conditional_edges(
    "random",
    should_contine,
    {
        "loop": "random",
        "exit": END
    }
)


app = graph.compile()
r = app.invoke({"name": "John doe", "number": [], "counter": -1})
print(r)