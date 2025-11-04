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
import asyncio
from dotenv import load_dotenv

load_dotenv()

# from src.state import DevelopmentState, UserStory


PRODUCT_MANAGER_PROMPT = """Eres un Product Manager experimentado. Creas user stories detalladas con contexto técnico completo.

FORMATO USER STORY:
# [ID] - [Título]
**Epic:** [Epic_ID - Nombre]

## Descripción
Como [rol], quiero [acción], para [beneficio].

## Contexto Técnico
- **Stack:** [Backend/Frontend/Both]
- **Componentes:** [lista]
- **APIs:** [METHOD /endpoint - descripción]
- **Modelos:** [Tabla: campos]

## Acceptance Criteria
### [Escenario]
- **DADO** [contexto]
- **CUANDO** [acción]
- **ENTONCES** [resultado]

## Definition of Done
- [ ] Código + tests (>80% coverage)
- [ ] Code review aprobado
- [ ] Documentación actualizada
- [ ] Sin vulnerabilidades
- [ ] Performance validada

## Escenarios de Prueba
1. **Happy Path:** [descripción]
2. **Edge Cases:** [casos límite]
3. **Errors:** [manejo de errores]

## Dependencias
- **Requiere:** [IDs]
- **Bloquea:** [IDs]

## Riesgos
- [Descripción] - Impacto: [H/M/L] - Mitigación: [plan]

## Notas Técnicas
- Implementación: [patrones, librerías]
- Seguridad: [consideraciones OWASP]
- Performance: <[X]ms

## Prioridad
**[HIGH/MEDIUM/LOW]** - Justificación: [razón]

## Story Points
**[1-13]** - Complejidad: [L/M/H], Esfuerzo: [X]h

---

FORMATO ÉPICA:
# Epic [ID]: [Nombre]
## Business Objective
[Objetivo medible]

## User Stories
- [US_XX] - [Título] ([N] pts)
Total: [X] points

## Success Metrics
- [KPI]: [Target]

## Riesgos
- [Descripción]

---

INSTRUCCIONES:
1. Enfócate en MVP funcional
2. Considera seguridad (OWASP), edge cases, performance
3. Identifica dependencias claras
4. Agrupa en épicas lógicas
5. Usa filesystem tools para guardar archivos
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

    output_dir = Path("output/user_stories")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir_absolute = output_dir.resolve()

    print(f"   📁 Directorio de salida: {output_dir_absolute}")

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

RUTA BASE: {output_dir_absolute}
Usa rutas completas: {output_dir_absolute}/archivo.md

MISIÓN: Crear product backlog completo y profesional.

PROCESO (5 FASES):

1. ANÁLISIS
   - Identifica épicas (ej: Autenticación, Gestión Tareas, UI)
   - Identifica dependencias técnicas
   - Identifica riesgos (técnicos, negocio, seguridad OWASP)
   - Define roadmap: MVP → Mejoras → Optimización

2. ÉPICAS
   Archivos: {output_dir_absolute}/epic_01_nombre.md, epic_02_*.md, etc.
   Usa formato ÉPICA del prompt.
   Incluye: Business Objective, User Stories, Success Metrics, Riesgos

3. USER STORIES
   Archivos: {output_dir_absolute}/user_story_01.md, user_story_02.md, etc.
   Usa formato USER STORY del prompt.

   TODAS las secciones obligatorias:
   ✅ Descripción + Contexto Técnico (stack, componentes, APIs, modelos)
   ✅ Acceptance Criteria (DADO-CUANDO-ENTONCES)
   ✅ Definition of Done + Escenarios de Prueba
   ✅ Dependencias + Riesgos + Notas Técnicas
   ✅ Prioridad justificada + Story Points

   Tech Stack:
   Backend: FastAPI, PostgreSQL, SQLAlchemy, JWT, Alembic, Pydantic
   Frontend: React, TailwindCSS, Redux, React Router, axios
   Seguridad: CSRF, XSS, SQL Injection prevention, bcrypt, rate limiting

4. BACKLOG MAESTRO
   Archivo: {output_dir_absolute}/backlog.md

   Estructura:
   - 📋 Resumen Ejecutivo (visión, objetivos, métricas, stack)
   - 🗺️ Roadmap por Fases (MVP/Mejoras/Optimización con puntos y DoD)
   - 📚 Épicas (objetivo, stories, puntos, prioridad)
   - 📊 User Stories por Prioridad (HIGH/MEDIUM/LOW con resumen)
   - 🔗 Matriz Dependencias (grafo mermaid + ruta crítica)
   - ⚠️ Riesgos (tabla: ID, riesgo, impacto, probabilidad, mitigación)
   - 📈 Estimaciones (total puntos, desglose, timeline, velocity)
   - ✅ Definition of Done Global
   - 📖 Convenciones (naming, docs, testing)

5. DOCS ADICIONALES
   - {output_dir_absolute}/dependencies_graph.md: Grafo mermaid + ruta crítica
   - {output_dir_absolute}/technical_architecture.md: Diagrama + stack + patrones

CRÍTICO:
✅ Usa filesystem MCP tools (write_file)
✅ RUTAS COMPLETAS: {output_dir_absolute}/
✅ Crea TODOS los archivos
✅ NO omitas secciones
✅ Sé exhaustivo

¡COMIENZA AHORA! NO TE DETENGAS HASTA COMPLETAR TODAS LAS TAREAS.
"""

    tools = await client.get_tools()
    agent = create_react_agent("openai:gpt-4.1", tools)
    math_response = await agent.ainvoke({"messages": query})
    print(math_response)


asyncio.run(product_manager_node_async())
