"""
Backend Developer - Nodo que implementa el código backend con FastAPI.

Este nodo:
1. Lee las tareas asignadas a backend del Scrum Master
2. Lee las user stories del Product Manager para contexto
3. Crea estructura completa del proyecto FastAPI
4. Implementa modelos, schemas, CRUD, endpoints y tests
"""

from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv
# from graph.state import GraphState

load_dotenv()


BACKEND_DEVELOPER_PROMPT = """Eres un Senior Backend Developer especializado en FastAPI y SQLAlchemy.

Proyecto: {project_name}
Stack: {backend_tech_stack}

UBICACIÓN:
- Lee tareas de: {sprint_planning_dir}/backend_tasks.md
- Lee contexto de: {user_stories_dir}/
- Escribe código en: {output_dir}/

TAREAS:

1. Lee backend_tasks.md para ver TODAS las tareas asignadas
2. Lee user stories relevantes para entender contexto técnico y criterios de aceptación
3. Crea estructura de proyecto FastAPI profesional siguiendo mejores prácticas Python

ESTRUCTURA REQUERIDA:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # Settings con pydantic-settings
│   │   ├── security.py      # JWT, passwords, auth
│   │   └── database.py      # SQLAlchemy engine y session
│   ├── models/              # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── [modelo].py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   └── [schema].py
│   ├── crud/                # CRUD operations
│   │   ├── __init__.py
│   │   └── [crud].py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py          # Dependencies (get_db, get_current_user)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   └── [endpoint].py
│   │       └── router.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py      # Fixtures
│       └── test_[feature].py
├── alembic/                 # Migrations
│   └── versions/
├── requirements.txt
├── .env.example
├── alembic.ini
└── README.md
```

MEJORES PRÁCTICAS:

- Type hints en todo el código
- Docstrings en funciones y clases públicas
- Async/await para operaciones I/O
- Dependency injection de FastAPI
- Validación exhaustiva con Pydantic
- Error handling con HTTPException
- Seguridad: hash passwords (bcrypt), JWT tokens, validación ownership
- Tests: pytest, >80% coverage, fixtures reutilizables
- CORS configurado correctamente
- Logging estructurado
- Variables de entorno para configuración sensible

IMPLEMENTACIÓN:

Para cada tarea en backend_tasks.md:
- Crea los archivos necesarios con código production-ready
- Sigue el patrón: modelo → schema → CRUD → endpoint → test
- Implementa validaciones de seguridad (OWASP)
- Crea tests unitarios e integración
- Documenta endpoints con docstrings y OpenAPI

Usa write_file con rutas completas. Crea TODOS los archivos necesarios.
NO uses placeholders ni TODOs en el código. Implementa código completo y funcional.
"""


# async def backend_developer_node_async(state: GraphState):
async def backend_developer_node_async():
    """
    Nodo del Backend Developer - Implementa código FastAPI.

    Retorna:
        dict: Update al state con messages conteniendo:
            - SystemMessage con resumen de implementación si todo va bien
            - SystemMessage con error si algo falla
    """

    print("\n🔧 Backend Developer - Implementando código backend...")

    try:
        project_name = "test_project"
        backend_tech_stack = "FastAPI, PostgreSQL, SQLAlchemy" # state.backend_stack

        # Directorios de entrada
        sprint_planning_dir = Path("output/sprint_planning")
        user_stories_dir = Path("output/user_stories")

        sprint_planning_absolute = sprint_planning_dir.resolve()
        user_stories_absolute = user_stories_dir.resolve()

        # Verificar que existan los archivos de entrada
        backend_tasks_file = sprint_planning_dir / "backend_tasks.md"
        if not backend_tasks_file.exists():
            error_msg = f"Backend Developer - Error: {backend_tasks_file} no encontrado. Ejecuta Scrum Master primero."
            print(f"❌ {error_msg}")
            return {"messages": [SystemMessage(content=error_msg)]}

        # Directorio de salida para el código backend
        output_dir = Path("output/app/backend")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_dir_absolute = output_dir.resolve()

        print(f"   📖 Leyendo tareas de: {backend_tasks_file}")
        print(f"   📖 Leyendo contexto de: {user_stories_absolute}")
        print(f"   📁 Generando código en: {output_dir_absolute}")

        # Crear prompt con variables
        prompt = BACKEND_DEVELOPER_PROMPT.format(
            project_name=project_name,
            backend_tech_stack=backend_tech_stack,
            sprint_planning_dir=sprint_planning_absolute,
            user_stories_dir=user_stories_absolute,
            output_dir=output_dir_absolute,
        )

        # Configurar MCP client con acceso a todos los directorios necesarios
        parent_dir = Path("output")
        parent_dir_absolute = parent_dir.resolve()

        client = MultiServerMCPClient(
            {
                "filesystem": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        str(parent_dir_absolute),
                    ],
                    "transport": "stdio",
                }
            }
        )

        # Obtener tools y crear agente
        tools = await client.get_tools()
        agent = create_react_agent("openai:gpt-4.1", tools)

        print("   🤖 Agente Backend Developer implementando código...")

        # Invocar agente
        await agent.ainvoke({"messages": prompt})

        print("🔧 Backend Developer - Proceso completado.")

        # Verificar archivos creados
        created_files = list(output_dir.rglob("*.py"))
        files_count = len(created_files)

        summary = (
            f"Backend Developer - Implementación completada exitosamente:\n"
            f"- Proyecto: {project_name}\n"
            f"- Archivos Python generados: {files_count}\n"
            f"- Directorio: {output_dir_absolute}\n"
            f"- Estructura FastAPI, modelos, schemas, endpoints y tests creados\n"
            f"- Stack: {backend_tech_stack}"
        )

        print(f"\n✅ {summary}")

        return {"messages": [SystemMessage(content=summary)]}

    except Exception as e:
        error_msg = (
            f"Backend Developer - Error en la implementación:\n"
            f"Tipo: {type(e).__name__}\n"
            f"Detalle: {str(e)}\n"
            f"El proceso no pudo completarse correctamente."
        )

        print(f"\n❌ {error_msg}")

        return {"messages": [SystemMessage(content=error_msg)]}

import asyncio
if __name__ == "__main__":
    asyncio.run(backend_developer_node_async())