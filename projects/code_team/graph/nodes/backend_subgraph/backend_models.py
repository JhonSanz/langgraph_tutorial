"""
Backend Models Node - Crea modelos SQLAlchemy.

Lee las tareas y user stories para crear los modelos necesarios.
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()


BACKEND_MODELS_PROMPT = """Eres un Senior Backend Developer especializado en SQLAlchemy.

Proyecto: {project_name}
Stack: {backend_tech_stack}

UBICACIÓN:
- Lee tareas: {sprint_planning_dir}/backend_tasks.md
- Lee contexto: {user_stories_dir}/
- Escribe en: {output_dir}/app/models/

TAREA: Crear modelos SQLAlchemy basándote en las user stories y tareas

Lee backend_tasks.md y user stories para identificar qué modelos crear.

Para cada modelo:
- Hereda de Base (from app.core.database import Base)
- Usa type hints correctos
- Campos con tipos SQLAlchemy apropiados
- Constraints (unique, nullable, default)
- Relationships si hay FK
- Timestamps (created_at, updated_at) donde corresponda
- __repr__ para debugging
- Docstring explicando el modelo

Ejemplos de campos comunes:
- id: Mapped[int] = mapped_column(primary_key=True)
- created_at: Mapped[datetime] = mapped_column(server_default=func.now())
- Relationships con back_populates

Crea archivos individuales por modelo en app/models/ y actualiza app/models/__init__.py

NO uses placeholders. Código production-ready.
"""


async def backend_models_node_async(state: GraphState):
    """
    Nodo Backend Models - Crea modelos SQLAlchemy.
    """

    print("\n📦 Backend Models - Creando modelos SQLAlchemy...")

    try:
        project_name = state["project_name"]
        backend_tech_stack = state["backend_stack"]
        user_stories_dir = state["user_stories_dir"]
        sprint_planning_dir = state["sprint_planning_dir"]
        output_dir = state["backend_output_dir"]

        print(f"   📖 Leyendo tareas de: {sprint_planning_dir}/backend_tasks.md")

        prompt = BACKEND_MODELS_PROMPT.format(
            project_name=project_name,
            backend_tech_stack=backend_tech_stack,
            user_stories_dir=user_stories_dir,
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

        print("   🤖 Agente creando modelos...")
        await agent.ainvoke({"messages": prompt})

        summary = "Backend Models - Modelos SQLAlchemy creados en app/models/"
        print(f"✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = f"Backend Models - Error: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"messages": [SystemMessage(content=error_msg)]}
