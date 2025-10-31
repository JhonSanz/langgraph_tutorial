"""
Product Manager - Nodo que usa Claude Agent SDK para crear user stories.

Este nodo:
1. Lee el requerimiento del usuario
2. Analiza y descompone en user stories
3. Define acceptance criteria
4. Prioriza las historias
"""

import asyncio
import json
import os
from typing import List

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

# from src.state import DevelopmentState, UserStory

from typing import TypedDict, List, Dict, Optional, Literal
from datetime import datetime
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
"""


# async def product_manager_node_async(state: DevelopmentState) -> DevelopmentState:
async def product_manager_node_async():
    """
    Nodo del Product Manager - Crea user stories desde el requerimiento.
    """

    print("\n👔 Product Manager - Analizando requerimiento...")

    user_requirement = "Crear una aplicación web para gestión de tareas con autenticación de usuarios, CRUD de tareas, y una interfaz intuitiva."
    project_name = "test_project"
    backend_tech_stack = "FastAPI, PostgreSQL, SQLAlchemy"
    frontend_tech_stack = "React, TailwindCSS, Redux"

    # Preparar contexto
    context = f"""
Proyecto: {project_name}

Requerimiento del usuario:
{user_requirement}

Tech Stack Backend: {backend_tech_stack}
Tech Stack Frontend: {frontend_tech_stack}
"""

    # Configurar Claude Agent
    options = ClaudeAgentOptions(
        system_prompt=PRODUCT_MANAGER_PROMPT,
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        max_tokens=4096,
    )

    query = f"""{context}

Por favor, analiza este requerimiento y crea un product backlog con user stories.

Tareas:
1. Descomponer el requerimiento en user stories manejables
2. Escribir cada user story en formato estándar
3. Definir acceptance criteria claros para cada historia
4. Asignar prioridad (high/medium/low)
5. Estimar story points (1-13)

Considera:
- Backend: FastAPI, PostgreSQL, SQLAlchemy
- Frontend: React, TailwindCSS, Redux
- Necesitamos un MVP funcional

Responde en JSON con este formato:
{{
  "user_stories": [
    {{
      "id": "US-001",
      "title": "Setup inicial del proyecto backend",
      "description": "Como desarrollador, quiero tener la estructura inicial del proyecto FastAPI, para poder comenzar a desarrollar features",
      "acceptance_criteria": [
        "Proyecto FastAPI creado con estructura de directorios",
        "Base de datos PostgreSQL configurada",
        "SQLAlchemy modelos base creados",
        "Servidor corre en localhost"
      ],
      "priority": "high",
      "estimated_points": 3
    }}
  ],
  "total_points": 0,
  "mvp_scope": "descripción breve del MVP"
}}

IMPORTANTE: Responde SOLO con el JSON, sin texto adicional.
"""

    try:
        async with ClaudeSDKClient(options=options) as client:
            print("   🤖 Analizando y creando user stories...")

            await client.query(query)

            full_response = ""
            async for message in client.receive_response():
                if hasattr(message, "text"):
                    full_response += message.text
                else:
                    full_response += str(message)

            # Parsear JSON
            try:
                # Buscar el JSON en la respuesta
                start = full_response.find("{")
                end = full_response.rfind("}") + 1

                if start == -1 or end <= start:
                    raise ValueError("No JSON found in response")

                json_str = full_response[start:end]
                data = json.loads(json_str)

                user_stories: List[UserStory] = data.get("user_stories", [])

                print(f"\n   ✅ Product Backlog creado:")
                print(f"      📋 {len(user_stories)} user stories")
                print(f"      🎯 {data.get('total_points', 0)} story points totales")
                print(f"      🚀 MVP: {data.get('mvp_scope', 'N/A')[:80]}...")

                # Mostrar las historias
                for story in user_stories[:3]:  # Mostrar las primeras 3
                    print(f"\n      [{story['id']}] {story['title']}")
                    print(
                        f"         Prioridad: {story['priority'].upper()} | Points: {story['estimated_points']}"
                    )

                if len(user_stories) > 3:
                    print(f"\n      ... y {len(user_stories) - 3} historias más")

                return {
                    # **state,
                    "user_stories": user_stories,
                    "product_backlog_created": True,
                    "updated_at": str(asyncio.get_event_loop().time()),
                }

            except json.JSONDecodeError as e:
                print(f"   ❌ Error parseando JSON: {e}")
                print(f"   Respuesta recibida: {full_response[:200]}...")

                return {
                    # **state,
                    "product_backlog_created": False,
                    # "errors": state["errors"]
                    # + [f"Product Manager: JSON parse error - {e}"],
                }

    except Exception as e:
        print(f"   ❌ Error en Product Manager: {e}")

        return {
            # **state,
            "product_backlog_created": False,
            # "errors": state["errors"] + [f"Product Manager failed: {e}"],
        }


# def product_manager_node(state: DevelopmentState) -> DevelopmentState:
#     """Wrapper sincrónico para el nodo async"""
#     return asyncio.run(product_manager_node_async(state))
