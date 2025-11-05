"""
Backend API Node - Crea endpoints FastAPI.

Lee CRUD y schemas para crear endpoints REST API.
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()


BACKEND_API_PROMPT = """Eres un Senior Backend Developer especializado en FastAPI.

Proyecto: {project_name}
Stack: {backend_tech_stack}

UBICACIÓN:
- Lee CRUD: {output_dir}/app/crud/
- Lee schemas: {output_dir}/app/schemas/
- Lee tareas: {sprint_planning_dir}/backend_tasks.md
- Escribe en: {output_dir}/app/api/v1/endpoints/

TAREA: Crear endpoints FastAPI para cada entidad

Para cada entidad, crea endpoints REST:
- POST /   → create (status 201)
- GET /    → list (con paginación)
- GET /{{id}} → read by id
- PUT /{{id}} → update
- DELETE /{{id}} → delete

Usa:
- APIRouter de FastAPI
- Depends() para inyección (get_db, get_current_user)
- Response models con schemas Pydantic
- Status codes apropiados
- HTTPException para errores
- Docstrings y OpenAPI tags
- Validaciones de seguridad (ownership, permisos)
- Query params para filtros/paginación

Estructura:
- Un archivo por entidad en app/api/v1/endpoints/
- Actualiza app/api/v1/router.py para incluir todos los routers
- Monta el router v1 en main.py si no está

NO uses placeholders. Código production-ready con validaciones y error handling.
"""


async def backend_api_node_async(state: GraphState):
    """
    Nodo Backend API - Crea endpoints FastAPI.
    """

    print("\n🚀 Backend API - Creando endpoints FastAPI...")

    try:
        project_name = state.get("project_name", "test_project")
        backend_tech_stack = state.get("backend_stack", "FastAPI, PostgreSQL, SQLAlchemy")
        sprint_planning_dir = state.get("sprint_planning_dir", "")
        output_dir = state.get("backend_output_dir", "")

        print(f"   📖 Leyendo CRUD y schemas...")

        prompt = BACKEND_API_PROMPT.format(
            project_name=project_name,
            backend_tech_stack=backend_tech_stack,
            sprint_planning_dir=sprint_planning_dir,
            output_dir=output_dir,
        )

        parent_dir = Path("output").resolve()
        client = MultiServerMCPClient({
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", str(parent_dir)],
                "transport": "stdio",
            }
        })

        tools = await client.get_tools()
        agent = create_react_agent("openai:gpt-4.1", tools)

        print("   🤖 Agente creando endpoints...")
        await agent.ainvoke({"messages": prompt})

        summary = "Backend API - Endpoints FastAPI creados en app/api/v1/endpoints/"
        print(f"✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = f"Backend API - Error: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"messages": [SystemMessage(content=error_msg)]}
