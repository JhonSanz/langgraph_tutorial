from langchain_ollama import OllamaLLM
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage


class AgentState(TypedDict):
    messages: list[HumanMessage]


llm = OllamaLLM(
    model="deepseek-r1:8b",
    base_url="http://192.168.1.14:11434"
)


def process(state: AgentState) -> AgentState:
    """"""
    response = llm.invoke(state["messages"])
    print(f"AI: {response}")
    return state


graph = StateGraph(AgentState)
graph.add_node("process", process)

graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()


user_input = input("Enter: ")
agent.invoke({"messages": [HumanMessage(content=user_input)]})