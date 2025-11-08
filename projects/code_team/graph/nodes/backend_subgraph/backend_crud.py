"""
Backend CRUD Node - Crea operaciones CRUD.

Lee modelos y schemas para crear funciones CRUD.
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()


BACKEND_CRUD_PROMPT = """Eres un Senior Backend Developer especializado en SQLAlchemy CRUD operations.

Proyecto: {project_name}
Stack: {backend_tech_stack}

UBICACIÓN:
- Lee modelos: {output_dir}/app/models/
- Lee schemas: {output_dir}/app/schemas/
- Lee tareas: {sprint_planning_dir}/backend_tasks.md
- Lee contexto: {user_stories_dir}/
- Escribe en: {output_dir}/app/crud/

TAREA: Crear funciones CRUD para cada modelo

Para cada entidad, crea funciones:
- get(db, id) → obtener por ID
- get_multi(db, skip, limit) → listar con paginación
- get_by_field(db, field_value) → buscar por campo específico (ej: email)
- create(db, obj_in) → crear nuevo
- update(db, db_obj, obj_in) → actualizar existente
- delete(db, id) → eliminar (soft o hard según caso)

Usa:
- SQLAlchemy 2.0 style (select, where, etc.)
- Type hints correctos
- Async operations donde apropiado
- Error handling (raise exceptions si no existe)
- Docstrings detallados
- Security checks donde necesario (ej: validar ownership)

Crea archivos individuales por entidad en app/crud/ y actualiza app/crud/__init__.py

NO uses placeholders. Código production-ready con manejo de errores.
"""


async def backend_crud_node_async(state: GraphState):
    """
    Nodo Backend CRUD - Crea operaciones CRUD.
    """

    print("\n⚙️  Backend CRUD - Creando operaciones CRUD...")

    project_name = state.get("project_name", "test_project")
    backend_tech_stack = state.get("backend_stack", "FastAPI, PostgreSQL, SQLAlchemy")
    sprint_planning_dir = state.get("sprint_planning_dir", "")
    user_stories_dir = state.get("user_stories_dir", "")
    output_dir = state.get("backend_output_dir", "")
    main_output = state.get("main_output")

    print(f"   📖 Leyendo modelos y schemas...")

    prompt = BACKEND_CRUD_PROMPT.format(
        project_name=project_name,
        backend_tech_stack=backend_tech_stack,
        user_stories_dir=user_stories_dir,
        sprint_planning_dir=sprint_planning_dir,
        output_dir=output_dir,
    )

    parent_dir = Path(main_output).resolve()
    client = MultiServerMCPClient(
        {
            "filesystem": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    str(parent_dir),
                ],
                "transport": "stdio",
            }
        }
    )

    try:
        tools = await client.get_tools()
        agent = create_react_agent("openai:gpt-4.1", tools)

        print("   🤖 Agente creando funciones CRUD...")
        await agent.ainvoke({"messages": prompt}, {"recursion_limit": 100})

        summary = "Backend CRUD - Operaciones CRUD creadas en app/crud/"
        print(f"✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = f"Backend CRUD - Error: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"messages": [SystemMessage(content=error_msg)]}
