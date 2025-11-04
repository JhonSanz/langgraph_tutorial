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
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from graph.state import GraphState

load_dotenv()

# from src.state import DevelopmentState, UserStory


QUERY = """
Product Manager experimentado. Creas user stories con contexto técnico completo.

USER STORY - Secciones obligatorias:
# [ID] - [Título] | Epic: [Epic_ID]
Descripción: Como [rol], quiero [acción], para [beneficio]
Contexto Técnico: Stack, Componentes, APIs, Modelos
Acceptance Criteria: DADO-CUANDO-ENTONCES (múltiples escenarios)
DoD: Código+tests>80%, review, docs, seguridad, performance
Escenarios: Happy path, edge cases, errors
Dependencias: Requiere [IDs], Bloquea [IDs]
Riesgos: [desc] - Impacto H/M/L - Mitigación [plan]
Notas: Implementación, Seguridad OWASP, Performance <Xms
Prioridad: H/M/L + justificación
Story Points: 1-13 + desglose

ÉPICA - Secciones:
# Epic [ID]: [Nombre]
Business Objective, User Stories (IDs+pts), Success Metrics, Riesgos


Proyecto: {project_name}

Requerimiento del usuario:
{user_requirement}

Tech Stack Backend: {backend_tech_stack}
Tech Stack Frontend: {frontend_tech_stack}

RUTA: {output_dir_absolute}/ (usar rutas completas)

BACKLOG COMPLETO - 5 FASES:
1. ANÁLISIS: épicas, dependencias, riesgos OWASP, roadmap MVP→Mejoras→Optimización
2. ÉPICAS: epic_01_*.md (formato ÉPICA)
3. USER STORIES: user_story_01.md (formato USER STORY con TODAS secciones)
   Stack: FastAPI, PostgreSQL, SQLAlchemy, JWT | React, TailwindCSS, Redux
4. BACKLOG: backlog.md (resumen ejecutivo, roadmap, épicas, stories HIGH/MED/LOW, grafo mermaid dependencias, riesgos, estimaciones, DoD, convenciones)
5. DOCS: dependencies_graph.md + technical_architecture.md

Se lo mas descriptivo posible. Usa write_file con rutas completas. Crea TODOS archivos. NO omitas secciones.
COMIENZA AHORA. NO TERMINES HASTA COMPLETAR TODO.
"""


async def product_manager_node_async(state: GraphState):
    """
    Nodo del Product Manager - Crea user stories desde el requerimiento.
    """

    print("\n👔 Product Manager - Analizando requerimiento...")

    user_requirement = "Crear una aplicación web para gestión de tareas con autenticación de usuarios, CRUD de tareas, y una interfaz intuitiva."
    project_name = "test_project"
    backend_tech_stack = "FastAPI, PostgreSQL, SQLAlchemy"
    frontend_tech_stack = "React, TailwindCSS, Zustand"

    output_dir = Path("output/user_stories")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir_absolute = output_dir.resolve()

    print(f"   📁 Directorio de salida: {output_dir_absolute}")

    prompt = QUERY.format(
        project_name=project_name,
        user_requirement=user_requirement,
        backend_tech_stack=backend_tech_stack,
        frontend_tech_stack=frontend_tech_stack,
        output_dir_absolute=output_dir_absolute,
    )

    client = MultiServerMCPClient(
        {
            "filesystem": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    str(output_dir),
                ],
                "transport": "stdio",
            }
        }
    )

    tools = await client.get_tools()
    agent = create_react_agent("openai:gpt-4.1", tools)

    response = await agent.ainvoke({"messages": prompt})
    print("👔 Product Manager - Proceso completado.")
    print(response)


asyncio.run(product_manager_node_async())
