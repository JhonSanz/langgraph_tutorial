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
import re
import traceback
from pathlib import Path
from typing import List

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, McpServerConfig

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

    # Configurar Claude Agent con MCP filesystem
    options = ClaudeAgentOptions(
        system_prompt=PRODUCT_MANAGER_PROMPT,
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        mcp_servers={
            "filesystem": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem"],
                "env": {"ALLOWED_PATHS": "/Users/me/projects"},
            }
        },
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "MultiEdit",
            "Grep",
            "Glob",
            "mcp__filesystem__list_files",
            "mcp__filesystem__list_files",
            "mcp__filesystem__read_file",
            "mcp__filesystem__write_file",
        ],
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

    try:
        async with ClaudeSDKClient(options=options) as client:
            print("   🤖 Iniciando agente Claude...")

            # Verificar herramientas disponibles (opcional, para debugging)
            # print(f"   🔧 Tools disponibles: {client.available_tools if hasattr(client, 'available_tools') else 'N/A'}")

            print("   💭 Analizando y creando user stories...")

            await client.query(query)

            full_response = ""
            files_created = []
            tool_calls = 0

            async for message in client.receive_response():
                # Manejar diferentes tipos de mensajes
                if hasattr(message, "text") and message.text:
                    full_response += message.text
                    # Mostrar progreso del agente (más conciso)
                    if message.text.strip() and len(message.text) > 20:
                        preview = message.text.strip()[:80].replace("\n", " ")
                        print(f"   💭 {preview}...")

                # Detectar cuando se usan tools
                if hasattr(message, "tool_use"):
                    tool_calls += 1
                    tool_name = getattr(message.tool_use, "name", "unknown")
                    print(f"   🔧 Usando herramienta: {tool_name}")

                    if "write" in tool_name.lower() or "create" in tool_name.lower():
                        print(f"   📝 Creando archivo...")

                # Capturar resultados de tools
                if hasattr(message, "content"):
                    content_str = str(message.content)
                    if ".md" in content_str:
                        # Extraer nombres de archivos mencionados
                        found_files = re.findall(
                            r"user_story_\d+\.md|backlog\.md", content_str
                        )
                        files_created.extend(found_files)

            print(f"\n   ✅ Proceso completado.")
            print(f"   🔧 Total de llamadas a herramientas: {tool_calls}")

            # Verificar archivos creados
            created_files = list(output_dir.glob("*.md"))

            if created_files:
                print(f"\n   📁 Archivos creados en {output_dir}:")
                for file in sorted(created_files):
                    file_size = file.stat().st_size
                    print(f"      ✓ {file.name} ({file_size} bytes)")
            else:
                print(f"\n   ⚠️  No se encontraron archivos .md en {output_dir}")
                print(
                    f"   💡 Verifica que el servidor MCP filesystem esté correctamente configurado"
                )
                print(f"   💡 Ruta permitida: {output_dir_absolute}")

            # Mostrar resumen de la respuesta del agente
            if full_response:
                print("\n--- Resumen del Agente ---")
                summary = (
                    full_response[:500] + "..."
                    if len(full_response) > 500
                    else full_response
                )
                print(summary)
                print("--- Fin del Resumen ---\n")

            # Si se crearon archivos, mostrar el contenido del backlog
            backlog_file = output_dir / "backlog.md"
            if backlog_file.exists():
                print("\n📋 Contenido del Product Backlog:")
                print("-" * 60)
                with open(backlog_file, "r", encoding="utf-8") as f:
                    print(f.read())
                print("-" * 60)

    except Exception as e:
        print(f"\n   ❌ Error al crear user stories: {e}")
        print("\n   Traceback completo:")
        traceback.print_exc()

        # Sugerencias de debugging
        print("\n   💡 Sugerencias:")
        print("      - Verifica que npx esté instalado: npx --version")
        print(
            "      - Verifica el paquete MCP: npx @modelcontextprotocol/server-filesystem --help"
        )
        print(f"      - Verifica permisos en: {output_dir_absolute}")
        print("      - Revisa la variable CLAUDE_API_KEY en tu entorno")


# from claude_agent_sdk import query
# import asyncio


# def basic_mcp():
#     """
#     Función básica para probar MCP filesystem.
#     """

#     async def run_test():
#         async for message in query(
#             prompt="List all Python files in my project",
#             options=ClaudeAgentOptions(
#                 mcp_servers={
#                     "filesystem": {
#                         "command": "npx",
#                         "args": ["@modelcontextprotocol/server-filesystem"],
#                         "env": {"ALLOWED_PATHS": "/Users/me/projects"},
#                     }
#                 },
#                 allowed_tools=[
#                     "Read",
#                     "Write",
#                     "Edit",
#                     "MultiEdit",
#                     "Grep",
#                     "Glob",
#                     "mcp__filesystem__list_files",
#                 ],
#             ),
#         ):
#             print(message)

#     asyncio.run(run_test())


if __name__ == "__main__":
    print("=" * 60)
    print("  Product Manager - Generador de User Stories")
    print("=" * 60)
    asyncio.run(product_manager_node_async())
    print("\n" + "=" * 60)
    print("  Proceso finalizado")
    print("=" * 60)
