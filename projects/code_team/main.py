from langchain_core.messages import HumanMessage
from graph import build_graph

# Build the graph
graph = build_graph()

# Display the graph structure
mermaid_code = graph.get_graph().draw_mermaid()
print(mermaid_code)


# result = graph.invoke(
#     {"messages": [HumanMessage(content="Crear una aplicación web para gestión de tareas con autenticación de usuarios, CRUD de tareas, y una interfaz intuitiva.")]}
# )

# print("\n=== Resultados finales ===")
# for msg in result["messages"]:
#     msg.pretty_print()