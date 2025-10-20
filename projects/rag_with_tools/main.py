from langchain_core.messages import HumanMessage
from graph import build_graph

# Build the graph
graph = build_graph()

# Display the graph structure
mermaid_code = graph.get_graph().draw_mermaid()
print(mermaid_code)


result = graph.invoke(
    {"messages": [HumanMessage(content="How much we made with Product A sales?")]}
)

print("\n=== Resultados finales ===")
for msg in result["messages"]:
    msg.pretty_print()

# https://chatgpt.com/c/68dedacb-2ea0-8326-9a4c-8fb83315c530
