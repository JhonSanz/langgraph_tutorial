"""
Backend Setup Node - Crea estructura base del proyecto FastAPI.

Crea:
- Estructura de directorios
- main.py, __init__.py
- core/ (config.py, database.py, security.py)
- requirements.txt, .env.example, README.md
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()


BACKEND_SETUP_PROMPT = """Eres un Senior Backend Developer. Crea la estructura base de un proyecto FastAPI.

Proyecto: {project_name}
Stack: {backend_tech_stack}

UBICACIÓN:
- Lee contexto de: {user_stories_dir}/ y {sprint_planning_dir}/
- Escribe código en: {output_dir}/

TAREA: Crear estructura base del proyecto FastAPI

ESTRUCTURA A CREAR:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app con CORS, middleware básico
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings con pydantic-settings
│   │   ├── security.py      # JWT utils, password hashing
│   │   └── database.py      # SQLAlchemy engine, SessionLocal, Base
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── crud/
│   │   └── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # get_db, get_current_user
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           └── __init__.py
│   └── tests/
│       └── __init__.py
├── requirements.txt         # FastAPI, SQLAlchemy, psycopg2, etc.
├── .env.example            # Variables de entorno
├── alembic.ini
└── README.md
```

Implementa:
- config.py con pydantic-settings (DATABASE_URL, SECRET_KEY, etc.)
- database.py con engine SQLAlchemy, SessionLocal, Base
- security.py con funciones para JWT y bcrypt
- main.py con FastAPI app básica, CORS, health check
- deps.py con dependency injection (get_db, get_current_user)
- requirements.txt con todas las dependencias
- .env.example con variables necesarias
- README.md con instrucciones de setup

Usa type hints, docstrings y mejores prácticas. NO uses placeholders.
"""


async def backend_setup_node_async(state: GraphState):
    """
    Nodo Backend Setup - Crea estructura base del proyecto.
    """

    print("\n🏗️  Backend Setup - Creando estructura base...")

    try:
        project_name = state.get("project_name", "test_project")
        backend_tech_stack = state.get("backend_stack", "FastAPI, PostgreSQL, SQLAlchemy")
        user_stories_dir = state.get("user_stories_dir", "")
        sprint_planning_dir = state.get("sprint_planning_dir", "")
        output_dir = state.get("backend_output_dir", "")

        print(f"   📁 Generando estructura en: {output_dir}")

        # Crear prompt
        prompt = BACKEND_SETUP_PROMPT.format(
            project_name=project_name,
            backend_tech_stack=backend_tech_stack,
            user_stories_dir=user_stories_dir,
            sprint_planning_dir=sprint_planning_dir,
            output_dir=output_dir,
        )

        # MCP client
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

        print("   🤖 Agente creando estructura base...")
        await agent.ainvoke({"messages": prompt})

        summary = "Backend Setup - Estructura base creada: main.py, core/, deps.py, requirements.txt"
        print(f"✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = f"Backend Setup - Error: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {"messages": [SystemMessage(content=error_msg)]}
