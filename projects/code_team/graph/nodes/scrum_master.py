"""
Scrum Master - Nodo que planifica el sprint y asigna tareas.

Este nodo:
1. Lee las user stories del Product Manager
2. Descompone cada user story en tareas técnicas
3. Asigna tareas a backend o frontend
4. Identifica dependencias entre tareas
"""

from graph.state import GraphState


SCRUM_MASTER_PROMPT = """Eres un Scrum Master experimentado con profundo conocimiento técnico en:
- Planificación de sprints
- Descomposición de user stories en tareas técnicas
- Identificación de dependencias
- Asignación de tareas basada en skills (backend vs frontend)

Tu responsabilidad es:
1. Tomar las user stories del product backlog
2. Descomponerlas en tareas técnicas específicas
3. Asignar cada tarea a backend o frontend
4. Identificar dependencias entre tareas

Conocimiento técnico:
- Backend: FastAPI, PostgreSQL, SQLAlchemy, Pydantic
- Frontend: React, TypeScript, TailwindCSS, Redux

Principios:
- Tareas deben ser pequeñas y manejables (máximo 1-2 días)
- Backend normalmente incluye: modelos, schemas, CRUD, endpoints
- Frontend normalmente incluye: components, pages, state management, API integration
- Identifica claramente las dependencias (ej: frontend necesita que backend esté listo)
"""


async def scrum_master_node_async(state: GraphState):
    """
    Nodo del Scrum Master - Planifica sprint y asigna tareas.
    """
    pass
