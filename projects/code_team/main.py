import asyncio
from langchain_core.messages import HumanMessage
from graph import build_graph


async def main():
    """
    Punto de entrada principal para ejecutar el grafo del equipo de desarrollo.
    """

    # Build the graph
    graph = build_graph()

    # Display the graph structure
    print("\n📊 Estructura del grafo:")
    mermaid_code = graph.get_graph().draw_mermaid()
    print(mermaid_code)

    # Estado inicial con valores por defecto
    initial_state = {
        "messages": [
            HumanMessage(
                content="Crear una aplicación web para gestión de tareas con "
                        "autenticación de usuarios, CRUD de tareas, y una interfaz intuitiva."
            )
        ],
        # Configuración del proyecto
        "project_name": "test_project",
        "backend_stack": "FastAPI, PostgreSQL, SQLAlchemy",
        "frontend_stack": "React, TailwindCSS, Zustand",
    }

    print("\n🚀 Iniciando ejecución del grafo con configuración:")
    print(f"   📦 Proyecto: {initial_state['project_name']}")
    print(f"   🔧 Backend: {initial_state['backend_stack']}")
    print(f"   🎨 Frontend: {initial_state['frontend_stack']}")
    print("\n" + "="*80 + "\n")

    # Ejecutar el grafo
    result = await graph.ainvoke(initial_state)

    print("\n" + "="*80)
    print("\n✅ Ejecución completada. Resumen de mensajes:")
    print("="*80 + "\n")

    for i, msg in enumerate(result["messages"], 1):
        print(f"\n--- Mensaje {i} ---")
        msg.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())