"""
Backend Schemas Node - Crea schemas Pydantic.

Lee los modelos creados y las tareas para crear schemas de validación.
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()


BACKEND_SCHEMAS_PROMPT = """Eres un Senior Backend Developer especializado en Pydantic.

Proyecto: {project_name}
Stack: {backend_tech_stack}

UBICACIÓN:
- Lee modelos de: {output_dir}/app/models/
- Lee tareas: {sprint_planning_dir}/backend_tasks.md
- Lee contexto: {user_stories_dir}/
- Escribe en: {output_dir}/app/schemas/

TAREA: Crear schemas Pydantic basándote en los modelos SQLAlchemy

Para cada modelo, crea schemas:
- Base: campos comunes
- Create: campos para creación (sin id, sin timestamps)
- Update: campos opcionales para actualización
- InDB: todos los campos (con id, timestamps)
- Response: lo que retorna la API

Usa:
- Pydantic v2 (from pydantic import BaseModel, ConfigDict)
- ConfigDict(from_attributes=True) para ORM mode
- Field(...) para validaciones y metadatos
- EmailStr, HttpUrl, etc. para validaciones específicas
- Validators personalizados si necesario
- Docstrings

Crea archivos individuales por entidad en app/schemas/ y actualiza app/schemas/__init__.py

NO uses placeholders. Código production-ready con validaciones completas.
"""


async def backend_schemas_node_async(state: GraphState):
    """
    Nodo Backend Schemas - Crea schemas Pydantic.
    """

    print("\n📋 Backend Schemas - Creando schemas Pydantic...")

    project_name = state.get("project_name", "test_project")
    backend_tech_stack = state.get("backend_stack", "FastAPI, PostgreSQL, SQLAlchemy")
    sprint_planning_dir = state.get("sprint_planning_dir", "")
    user_stories_dir = state.get("user_stories_dir", "")
    output_dir = state.get("backend_output_dir", "")
    main_output = state.get("main_output")

    print(f"   📖 Leyendo modelos de: {output_dir}/app/models/")

    prompt = BACKEND_SCHEMAS_PROMPT.format(
        project_name=project_name,
        backend_tech_stack=backend_tech_stack,
        user_stories_dir=user_stories_dir,
        sprint_planning_dir=sprint_planning_dir,
        output_dir=output_dir,
    )

    parent_dir = Path(main_output).resolve()
    client = MultiServerMCPClient({
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(parent_dir)],
            "transport": "stdio",
        }
    })

    try:
        tools = await client.get_tools()
        agent = create_react_agent("openai:gpt-4.1", tools)

        print("   🤖 Agente creando schemas...")
        await agent.ainvoke({"messages": prompt})

        summary = "Backend Schemas - Schemas Pydantic creados en app/schemas/"
        print(f"✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = f"Backend Schemas - Error: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"messages": [SystemMessage(content=error_msg)]}
