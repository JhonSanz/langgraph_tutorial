"""
Scrum Master - Nodo que planifica el sprint y asigna tareas.

Este nodo:
1. Lee las user stories del Product Manager
2. Descompone cada user story en tareas técnicas
3. Asigna tareas a backend o frontend
4. Identifica dependencias entre tareas
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()


SCRUM_MASTER_PROMPT = """Eres un Scrum Master experimentado. Planifica sprints y descompón user stories en tareas técnicas.

Proyecto: {project_name}
Stack Backend: {backend_tech_stack}
Stack Frontend: {frontend_tech_stack}

UBICACIÓN:
- Lee user stories de: {input_dir_absolute}/
- Lee backlog.md para dependencias
- Escribe archivos en: {output_dir_absolute}/

TAREAS:

1. Lee TODAS las user stories (user_story_*.md) y backlog.md
2. Organiza en sprints (10-15 pts cada uno, respetando prioridades y dependencias)
3. Descompón cada user story en tareas técnicas backend/frontend con ID único
4. Identifica dependencias entre tareas (ej: FE integración requiere BE endpoints)

ARCHIVOS A CREAR:

1. sprint_plan.md: Plan de sprints con user stories y tareas organizadas por sprint
2. backend_tasks.md: Lista detallada de tareas backend (modelos, schemas, CRUD, endpoints, tests)
3. frontend_tasks.md: Lista detallada de tareas frontend (componentes, state, API, tests)
4. dependencies_map.md: Diagrama mermaid mostrando dependencias entre tareas

Usa checkboxes, estimaciones en horas, IDs únicos tipo [STORY_ID]_BE_01, y marca dependencias claramente.
Usa write_file con rutas completas. Crea TODOS los archivos.
"""


async def scrum_master_node_async(state: GraphState):
    """
    Nodo del Scrum Master - Planifica sprint y asigna tareas.

    Retorna:
        dict: Update al state con messages conteniendo:
            - SystemMessage con resumen de planificación si todo va bien
            - SystemMessage con error si algo falla
    """

    print("\n📋 Scrum Master - Planificando sprints y asignando tareas...")

    try:
        project_name = state.get("project_name", "test_project")
        backend_tech_stack = state.get("backend_stack", "FastAPI, PostgreSQL, SQLAlchemy")
        frontend_tech_stack = state.get("frontend_stack", "React, TailwindCSS, Zustand")
        main_output = state.get("main_output")

        # Directorio donde el Product Manager creó las user stories - Leer del estado
        user_stories_dir_str = state.get("user_stories_dir")

        if not user_stories_dir_str:
            error_msg = "Scrum Master - Error: user_stories_dir no encontrado en el estado. Ejecuta Product Manager primero."
            print(f"❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        input_dir_absolute = Path(user_stories_dir_str)

        if not input_dir_absolute.exists():
            error_msg = f"Scrum Master - Error: Directorio {input_dir_absolute} no existe. Ejecuta Product Manager primero."
            print(f"❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        # Directorio de salida para el plan de sprints
        output_dir = Path(main_output) / "sprint_planning"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_dir_absolute = output_dir.resolve()

        print(f"   📖 Leyendo user stories de: {input_dir_absolute}")
        print(f"   📁 Salida de planificación: {output_dir_absolute}")

        # Crear prompt con variables
        prompt = SCRUM_MASTER_PROMPT.format(
            project_name=project_name,
            backend_tech_stack=backend_tech_stack,
            frontend_tech_stack=frontend_tech_stack,
            input_dir_absolute=input_dir_absolute,
            output_dir_absolute=output_dir_absolute,
        )

        # Configurar MCP client con acceso a ambos directorios
        # El agente necesita leer de input_dir y escribir en output_dir
        client = MultiServerMCPClient(
            {
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(main_output),
                    ],
                    "transport": "stdio",
                }
            }
        )

        # Obtener tools y crear agente
        tools = await client.get_tools()
        agent = create_react_agent("openai:gpt-4.1", tools)

        print("   🤖 Agente Scrum Master ejecutando planificación...")

        # Invocar agente
        await agent.ainvoke({"messages": prompt})

        print("📋 Scrum Master - Proceso completado.")

        # Verificar que se hayan creado archivos
        created_files = list(output_dir.rglob("*.md"))
        files_count = len(created_files)

        if files_count == 0:
            error_msg = (
                f"Scrum Master - Error: No se crearon archivos en {output_dir_absolute}\n"
                "El agente no generó la planificación. Verifica el prompt o intenta nuevamente."
            )
            print(f"\n❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        summary = (
            f"Scrum Master - Planificación completada exitosamente:\n"
            f"- Proyecto: {project_name}\n"
            f"- User stories analizadas: {len(list(input_dir_absolute.glob('user_story_*.md')))}\n"
            f"- Archivos de planificación generados: {files_count}\n"
            f"- Directorio: {output_dir_absolute}\n"
            f"- Sprint plan, tareas backend/frontend y mapa de dependencias creados"
        )

        print(f"\n✅ {summary}")

        return {
            "messages": [SystemMessage(content=summary)],
            "sprint_planning_dir": str(output_dir_absolute),
        }

    except Exception as e:
        error_msg = (
            f"Scrum Master - Error en la planificación:\n"
            f"Tipo: {type(e).__name__}\n"
            f"Detalle: {str(e)}\n"
            f"El proceso no pudo completarse correctamente."
        )

        print(f"\n❌ {error_msg}")

        return {"messages": [SystemMessage(content=error_msg)]}
