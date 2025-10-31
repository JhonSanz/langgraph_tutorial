from langchain_core.messages import HumanMessage
from graph import build_graph

# Build the graph
graph = build_graph()

# Display the graph structure
mermaid_code = graph.get_graph().draw_mermaid()
print(mermaid_code)


# result = graph.invoke(
#     {"messages": [HumanMessage(content="Encontrar los ultimos 10 errores criticos")]}
# )
# print("\n=== Resultados finales ===")
# for msg in result["messages"]:
#     msg.pretty_print()

# result = graph.invoke(
#     {"messages": [HumanMessage(content="Cuanto dinero gané vendiendo el "Product A"?")]}
# )
# print("\n=== Resultados finales ===")
# for msg in result["messages"]:
#     msg.pretty_print()



# result = graph.invoke(
#     {"messages": [HumanMessage(content="Cuál es el horario de atención al cliente?")]}
# )

# print("\n=== Resultados finales ===")
# for msg in result["messages"]:
#     msg.pretty_print()

# https://chatgpt.com/c/68dedacb-2ea0-8326-9a4c-8fb83315c530
