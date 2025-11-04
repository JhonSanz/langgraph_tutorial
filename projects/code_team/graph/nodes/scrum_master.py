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


SCRUM_MASTER_PROMPT = """Eres un Scrum Master experimentado con profundo conocimiento técnico.

Tu misión es LEER las user stories generadas por el Product Manager y crear un plan de sprints detallado.

CONTEXTO TÉCNICO:
- Backend: {backend_tech_stack}
- Frontend: {frontend_tech_stack}

UBICACIÓN DE ARCHIVOS:
- User Stories: {input_dir_absolute}/
- Archivos a leer: user_story_01.md, user_story_02.md, etc.
- Backlog: {input_dir_absolute}/backlog.md

PROCESO (5 FASES):

1. LECTURA DE USER STORIES:
   - Lee TODOS los archivos user_story_*.md usando read_file
   - Extrae: ID, Título, Epic, Prioridad (HIGH/MEDIUM/LOW), Story Points, Dependencias
   - Lee backlog.md para ver el grafo de dependencias completo

2. ORGANIZACIÓN EN SPRINTS:
   - Sprint típico: 10-15 story points
   - Respetar dependencias (no asignar una story si depende de otra en sprint futuro)
   - Priorizar: HIGH primero, luego MEDIUM, luego LOW
   - Sprint 1: Stories de alta prioridad sin dependencias bloqueantes

3. DESCOMPOSICIÓN EN TAREAS TÉCNICAS:
   Para cada user story, crear tareas específicas:

   BACKEND (si aplica):
   - [STORY_ID]_BE_01: Crear modelo SQLAlchemy (2h)
   - [STORY_ID]_BE_02: Crear schemas Pydantic (1h)
   - [STORY_ID]_BE_03: Implementar CRUD/servicios (3h)
   - [STORY_ID]_BE_04: Crear endpoints FastAPI (2h)
   - [STORY_ID]_BE_05: Tests backend >80% (2h)

   FRONTEND (si aplica):
   - [STORY_ID]_FE_01: Crear componentes React + TailwindCSS (3h)
   - [STORY_ID]_FE_02: Implementar state management Zustand (2h)
   - [STORY_ID]_FE_03: Integrar con API backend (2h) - DEPENDE DE BE_04
   - [STORY_ID]_FE_04: Tests frontend con testing-library (2h)

4. IDENTIFICACIÓN DE DEPENDENCIAS ENTRE TAREAS:
   - Frontend API integration requiere Backend API endpoints
   - Tests requieren implementación completa
   - Marcar claramente: "DEPENDE DE: [task_id]"

5. CREAR ARCHIVOS DE SALIDA:
   Usar write_file con rutas completas {output_dir_absolute}/:

   a) sprint_plan.md:
      ```markdown
      # Sprint Planning - {project_name}

      ## Sprint 1 (15 pts) - Semanas 1-2
      ### User Stories:
      - user_story_01: Registro y Login (8 pts) - HIGH
      - user_story_02: CRUD Tareas (5 pts) - HIGH

      ### Tareas Backend:
      - user_story_01_BE_01: Crear modelo User (2h)
      - user_story_01_BE_02: Schemas Pydantic User (1h)
      ...

      ### Tareas Frontend:
      - user_story_01_FE_01: Componente Login (3h)
      ...

      ### Dependencias Críticas:
      - user_story_01_FE_03 DEPENDE DE user_story_01_BE_04

      ## Sprint 2 (12 pts) - Semanas 3-4
      ...
      ```

   b) backend_tasks.md:
      ```markdown
      # Tareas Backend - {project_name}

      ## Sprint 1
      ### user_story_01 - Registro y Login
      - [ ] user_story_01_BE_01: Crear modelo User SQLAlchemy (2h)
           Descripción: Modelo con id, username, email, password_hash
           Campos: timestamps, constraints, indexes
      - [ ] user_story_01_BE_02: Schemas Pydantic (1h)
           Request/Response schemas con validación
      ...
      ```

   c) frontend_tasks.md:
      ```markdown
      # Tareas Frontend - {project_name}

      ## Sprint 1
      ### user_story_01 - Registro y Login
      - [ ] user_story_01_FE_01: Componentes Login/Register (3h)
           Formularios con validación, TailwindCSS styling
      - [ ] user_story_01_FE_02: Store Zustand auth (2h)
           Estado: user, token, isAuthenticated
           Acciones: login, register, logout
      ...
      ```

   d) dependencies_map.md:
      ```markdown
      # Mapa de Dependencias - Tareas Técnicas

      ```mermaid
      graph TD
        user_story_01_BE_01 --> user_story_01_BE_02
        user_story_01_BE_02 --> user_story_01_BE_03
        user_story_01_BE_03 --> user_story_01_BE_04
        user_story_01_BE_04 --> user_story_01_BE_05
        user_story_01_BE_04 --> user_story_01_FE_03
        user_story_01_FE_01 --> user_story_01_FE_02
        user_story_01_FE_02 --> user_story_01_FE_03
      ```
      ```

FORMATO:
- Usar markdown profesional
- Checkboxes para tareas: - [ ]
- Estimaciones en horas
- Dependencias explícitas
- Rutas completas en write_file

NO TERMINES HASTA CREAR TODOS LOS ARCHIVOS (sprint_plan.md, backend_tasks.md, frontend_tasks.md, dependencies_map.md).
COMIENZA AHORA.
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
        project_name = "test_project"
        backend_tech_stack = state.backend_stack
        frontend_tech_stack = state.frontend_stack

        # Directorio donde el Product Manager creó las user stories
        input_dir = Path("output/user_stories")
        input_dir_absolute = input_dir.resolve()

        if not input_dir.exists():
            error_msg = f"Scrum Master - Error: Directorio {input_dir_absolute} no encontrado. Ejecuta Product Manager primero."
            print(f"❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        # Directorio de salida para el plan de sprints
        output_dir = Path("output/sprint_planning")
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
                "filesystem_read": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(input_dir),
                    ],
                    "transport": "stdio",
                },
                "filesystem_write": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(output_dir),
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

        # Verificar archivos creados
        created_files = list(output_dir.rglob("*.md"))
        files_count = len(created_files)

        summary = (
            f"Scrum Master - Planificación completada exitosamente:\n"
            f"- Proyecto: {project_name}\n"
            f"- User stories analizadas: {len(list(input_dir.glob('user_story_*.md')))}\n"
            f"- Archivos de planificación generados: {files_count}\n"
            f"- Directorio: {output_dir_absolute}\n"
            f"- Sprint plan, tareas backend/frontend y mapa de dependencias creados"
        )

        print(f"\n✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = (
            f"Scrum Master - Error en la planificación:\n"
            f"Tipo: {type(e).__name__}\n"
            f"Detalle: {str(e)}\n"
            f"El proceso no pudo completarse correctamente."
        )

        print(f"\n❌ {error_msg}")

        return {"messages": [SystemMessage(content=error_msg)]}
