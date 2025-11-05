"""
Backend Developer - Nodo orquestador que invoca el subgrafo backend.

Este nodo:
1. Prepara el estado con paths necesarios
2. Verifica que existan los archivos de entrada
3. Invoca el subgrafo backend que construye el código paso a paso
"""

from pathlib import Path
from langchain_core.messages import SystemMessage
from graph.state import GraphState
from .backend_subgraph import create_backend_subgraph


async def backend_developer_node_async(state: GraphState):
    """
    Nodo del Backend Developer - Orquesta la construcción del backend.

    Este nodo prepara el estado y delega al subgrafo backend para
    dividir el trabajo en 6 pasos especializados:
    1. Setup (estructura base)
    2. Models (SQLAlchemy)
    3. Schemas (Pydantic)
    4. CRUD (operaciones)
    5. API (endpoints)
    6. Tests (pytest)

    Retorna:
        dict: Update al state con messages y paths configurados
    """

    print("\n🔧 Backend Developer - Iniciando construcción del backend...")

    try:
        # Obtener configuración del estado
        project_name = state.get("project_name", "test_project")
        backend_stack = state.get("backend_stack", "FastAPI, PostgreSQL, SQLAlchemy")

        # Directorios de entrada - Deben existir en el estado
        user_stories_dir_str = state.get("user_stories_dir")
        sprint_planning_dir_str = state.get("sprint_planning_dir")

        if not user_stories_dir_str:
            error_msg = "Backend Developer - Error: user_stories_dir no encontrado en el estado. Ejecuta Product Manager primero."
            print(f"❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        if not sprint_planning_dir_str:
            error_msg = "Backend Developer - Error: sprint_planning_dir no encontrado en el estado. Ejecuta Scrum Master primero."
            print(f"❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        sprint_planning_absolute = Path(sprint_planning_dir_str)
        user_stories_absolute = Path(user_stories_dir_str)

        # Verificar que existan los archivos de entrada
        backend_tasks_file = sprint_planning_absolute / "backend_tasks.md"
        if not backend_tasks_file.exists():
            error_msg = f"Backend Developer - Error: {backend_tasks_file} no existe. Ejecuta Scrum Master primero."
            print(f"❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        # Directorio de salida para el código backend
        output_dir = Path("output/app/backend")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_dir_absolute = output_dir.resolve()

        print(f"   📖 Leyendo tareas de: {backend_tasks_file}")
        print(f"   📖 Leyendo contexto de: {user_stories_absolute}")
        print(f"   📁 Generando código en: {output_dir_absolute}")

        # Preparar estado para el subgrafo
        subgraph_state = {
            **state,
            "user_stories_dir": str(user_stories_absolute),
            "sprint_planning_dir": str(sprint_planning_absolute),
            "backend_output_dir": str(output_dir_absolute),
        }

        print("\n   🏗️  Ejecutando subgrafo backend (6 pasos)...")

        # Crear y ejecutar el subgrafo
        backend_subgraph = create_backend_subgraph()
        await backend_subgraph.ainvoke(subgraph_state)

        print("\n🔧 Backend Developer - Proceso completado.")

        # Verificar que se hayan creado archivos
        created_files = list(output_dir.rglob("*.py"))
        files_count = len(created_files)

        if files_count == 0:
            error_msg = (
                f"Backend Developer - Error: No se crearon archivos Python en {output_dir_absolute}\n"
                "El subgrafo no generó código. Verifica los prompts o intenta nuevamente."
            )
            print(f"\n❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        summary = (
            f"Backend Developer - Implementación completada exitosamente:\n"
            f"- Proyecto: {project_name}\n"
            f"- Archivos Python generados: {files_count}\n"
            f"- Directorio: {output_dir_absolute}\n"
            f"- Subgrafo ejecutado: setup → models → schemas → crud → api → tests\n"
            f"- Stack: {backend_stack}"
        )

        print(f"\n✅ {summary}")

        # Actualizar estado con paths para otros nodos
        return {
            "messages": [SystemMessage(content=summary)],
            "user_stories_dir": str(user_stories_absolute),
            "sprint_planning_dir": str(sprint_planning_absolute),
            "backend_output_dir": str(output_dir_absolute),
        }

    except Exception as e:
        error_msg = (
            f"Backend Developer - Error en la implementación:\n"
            f"Tipo: {type(e).__name__}\n"
            f"Detalle: {str(e)}\n"
            f"El proceso no pudo completarse correctamente."
        )

        print(f"\n❌ {error_msg}")

        return {"messages": [SystemMessage(content=error_msg)]}
