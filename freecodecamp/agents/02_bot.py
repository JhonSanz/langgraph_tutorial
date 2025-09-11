from langchain_ollama import OllamaLLM
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage


class AgentState(TypedDict):
    messages: list[HumanMessage | AIMessage]


llm = OllamaLLM(
    model="deepseek-r1:8b",
    base_url="http://localhost:11434"
)

def process(state: AgentState) -> AgentState:
    """This node will the request you input"""
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response))
    print(f"\nAI: {response}")
    return state

graph = StateGraph(AgentState)
graph.add_node("process", process)

graph.add_edge(START, "process")
graph.add_edge("process", END)

agent = graph.compile()
conversation_history = []

user_input = input("Enter: ")
while  user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": conversation_history})
    print(result["messages"])
    conversation_history = result["messages"]

    user_input = input("Enter: ")


with open("logging.txt", "w") as file:
    file.write("Your Conversation Log:\n")
    
    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"You: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n\n")
    file.write("End of Conversation")

print("Conversation saved to logging.txt")