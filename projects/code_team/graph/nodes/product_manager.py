"""
Product Manager - Nodo para crear user stories.

Este nodo:
1. Lee el requerimiento del usuario
2. Analiza y descompone en user stories
3. Define acceptance criteria
4. Prioriza las historias
"""

import asyncio
from pathlib import Path
from typing import List
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import asyncio
from dotenv import load_dotenv

load_dotenv()

# from src.state import DevelopmentState, UserStory

from typing import TypedDict, List, Literal


class UserStory(TypedDict):
    """Una historia de usuario"""

    id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    priority: Literal["high", "medium", "low"]
    estimated_points: int


PRODUCT_MANAGER_PROMPT = """Eres un Product Manager experimentado con expertise en:
- Análisis de requerimientos
- Escribir user stories claras y accionables
- Definir acceptance criteria específicos
- Priorizar features basándose en valor de negocio

Tu responsabilidad es tomar requerimientos del usuario y convertirlos en user stories bien definidas.

Formato de user stories:
- Título claro y conciso
- Descripción en formato: "Como [rol], quiero [acción], para [beneficio]"
- Acceptance criteria específicos y verificables
- Prioridad basada en valor (high, medium, low)
- Story points estimados (1-13 usando Fibonacci)

Sé exhaustivo pero pragmático. Enfócate en crear un MVP funcional primero.

IMPORTANTE: Usa las herramientas de filesystem disponibles para guardar archivos.
"""


async def product_manager_node_async():
    """
    Nodo del Product Manager - Crea user stories desde el requerimiento.
    """

    print("\n👔 Product Manager - Analizando requerimiento...")

    user_requirement = "Crear una aplicación web para gestión de tareas con autenticación de usuarios, CRUD de tareas, y una interfaz intuitiva."
    project_name = "test_project"
    backend_tech_stack = "FastAPI, PostgreSQL, SQLAlchemy"
    frontend_tech_stack = "React, TailwindCSS, Redux"

    # Crear directorio de salida para user stories
    output_dir = Path("output/user_stories")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir_absolute = output_dir.resolve()

    print(f"   📁 Directorio de salida: {output_dir_absolute}")

    # Preparar contexto
    context = f"""
Proyecto: {project_name}

Requerimiento del usuario:
{user_requirement}

Tech Stack Backend: {backend_tech_stack}
Tech Stack Frontend: {frontend_tech_stack}
"""

    client = MultiServerMCPClient(
        {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", str(output_dir)],
                "transport": "stdio",
            }
        }
    )
    query = f"""{context}

DIRECTORIO DE GUARDADO: {output_dir_absolute}

Por favor, analiza este requerimiento y crea un product backlog con user stories.

Tareas:
1. Descomponer el requerimiento en user stories manejables
2. Escribir cada user story en formato estándar
3. Definir acceptance criteria claros para cada historia
4. Asignar prioridad (high/medium/low)
5. Estimar story points (1-13)
6. GUARDAR cada user story en un archivo .md separado

Considera:
- Backend: FastAPI, PostgreSQL, SQLAlchemy
- Frontend: React, TailwindCSS, Redux
- Necesitamos un MVP funcional

CRÍTICO - INSTRUCCIONES DE GUARDADO:
- Usa las herramientas de filesystem MCP disponibles (write_file o similar)
- Guarda cada archivo con la RUTA COMPLETA: {output_dir_absolute}/user_story_[número].md
- Ejemplo de ruta: {output_dir_absolute}/user_story_01.md
- Crea archivos numerados: user_story_01.md, user_story_02.md, etc.

Formato de cada archivo .md:

# [Título de la historia]

## Descripción
Como [rol], quiero [acción], para [beneficio]

## Acceptance Criteria
- Criterio 1
- Criterio 2
- Criterio 3

## Prioridad
[high/medium/low]

## Story Points
[número de 1-13]

---

Después de crear todos los archivos de user stories, crea también un archivo "backlog.md" 
en la misma ubicación ({output_dir_absolute}/backlog.md) con el resumen del product backlog completo,
incluyendo todas las historias numeradas y ordenadas por prioridad.
"""

    tools = await client.get_tools()
    agent = create_react_agent("openai:gpt-4.1", tools)
    math_response = await agent.ainvoke({"messages": query})
    print(math_response)


asyncio.run(product_manager_node_async())
