"""
Backend Tests Node - Crea tests con pytest.

Lee todo el código y crea tests unitarios e integración.
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()


BACKEND_TESTS_PROMPT = """Eres un Senior Backend Developer especializado en Testing con pytest.

Proyecto: {project_name}
Stack: {backend_tech_stack}

UBICACIÓN:
- Lee código: {output_dir}/app/
- Lee tareas: {sprint_planning_dir}/backend_tasks.md
- Escribe en: {output_dir}/app/tests/

TAREA: Crear tests completos (objetivo: >80% coverage)

Crea:
1. conftest.py: fixtures reutilizables
   - client fixture (TestClient)
   - db fixture (SQLite in-memory para tests)
   - test_user fixture
   - auth_headers fixture

2. Para cada endpoint/feature:
   - test_[feature].py con casos:
     * Happy path
     * Validaciones (400)
     * Autenticación (401)
     * Permisos (403)
     * No encontrado (404)
     * Edge cases

3. Tests unitarios para:
   - CRUD operations
   - Security functions
   - Validaciones

Usa:
- pytest, pytest-asyncio
- TestClient de FastAPI
- Fixtures para DRY
- Parametrize para múltiples casos
- Markers (@pytest.mark.asyncio)
- Assertions claros
- Docstrings explicando qué se testea

NO uses placeholders. Tests completos y ejecutables.
"""


async def backend_tests_node_async(state: GraphState):
    """
    Nodo Backend Tests - Crea tests con pytest.
    """

    print("\n🧪 Backend Tests - Creando tests...")

    try:
        project_name = state.get("project_name", "test_project")
        backend_tech_stack = state.get("backend_stack", "FastAPI, PostgreSQL, SQLAlchemy")
        sprint_planning_dir = state.get("sprint_planning_dir", "")
        output_dir = state.get("backend_output_dir", "")

        print(f"   📖 Leyendo código a testear...")

        prompt = BACKEND_TESTS_PROMPT.format(
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

        print("   🤖 Agente creando tests...")
        await agent.ainvoke({"messages": prompt})

        summary = "Backend Tests - Tests con pytest creados en app/tests/"
        print(f"✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = f"Backend Tests - Error: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"messages": [SystemMessage(content=error_msg)]}
