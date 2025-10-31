"""
Scrum Master - Nodo que planifica el sprint y asigna tareas.

Este nodo:
1. Lee las user stories del Product Manager
2. Descompone cada user story en tareas técnicas
3. Asigna tareas a backend o frontend
4. Identifica dependencias entre tareas
"""

import asyncio
import json
import os
from typing import List

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from src.state import DevelopmentState, Task, UserStory


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


async def scrum_master_node_async(state: DevelopmentState) -> DevelopmentState:
    """
    Nodo del Scrum Master - Planifica sprint y asigna tareas.
    """
    
    print("\n🏃 Scrum Master - Planificando sprint...")
    
    user_stories = state['user_stories']
    project_name = state['project_name']
    
    if not user_stories:
        print("   ⚠️  No hay user stories para planificar")
        return {
            **state,
            'sprint_planned': False,
            'errors': state['errors'] + ["Scrum Master: No user stories available"]
        }
    
    # Preparar contexto
    stories_summary = "\n".join([
        f"[{story['id']}] {story['title']} (Prioridad: {story['priority']}, Points: {story['estimated_points']})"
        for story in user_stories
    ])
    
    context = f"""
Proyecto: {project_name}
Sprint: {state['current_sprint']}

User Stories en el backlog:
{stories_summary}

Tech Stack:
- Backend: FastAPI, PostgreSQL, SQLAlchemy
- Frontend: React, TailwindCSS, Redux
"""
    
    # Configurar Claude Agent
    options = ClaudeAgentOptions(
        system_prompt=SCRUM_MASTER_PROMPT,
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        max_tokens=4096,
    )
    
    query = f"""{context}

Por favor, planifica el sprint descomponiendo cada user story en tareas técnicas.

Para cada user story:
1. Identifica las tareas necesarias
2. Asigna cada tarea a "backend" o "frontend"
3. Define dependencias entre tareas
4. Ordena las tareas para que las dependencias se respeten

Guía de tareas típicas:

Backend (FastAPI):
- Crear modelos SQLAlchemy
- Crear schemas Pydantic
- Implementar CRUD operations
- Crear endpoints API
- Agregar validaciones
- Configurar base de datos

Frontend (React):
- Crear componentes UI
- Crear páginas/vistas
- Implementar state management
- Integrar con API backend
- Agregar estilos con TailwindCSS
- Manejar formularios

Responde en JSON con este formato:
{{
  "tasks": [
    {{
      "id": "TASK-001",
      "user_story_id": "US-001",
      "title": "Crear modelos SQLAlchemy para usuarios",
      "description": "Definir modelo User con campos: id, email, name, created_at",
      "assigned_to": "backend",
      "status": "pending",
      "dependencies": []
    }},
    {{
      "id": "TASK-002",
      "user_story_id": "US-001",
      "title": "Crear endpoint POST /users",
      "description": "Implementar endpoint para crear usuarios con validación",
      "assigned_to": "backend",
      "status": "pending",
      "dependencies": ["TASK-001"]
    }}
  ],
  "sprint_summary": "Resumen del sprint",
  "backend_tasks_count": 0,
  "frontend_tasks_count": 0
}}

IMPORTANTE: Responde SOLO con el JSON, sin texto adicional.
"""
    
    try:
        async with ClaudeSDKClient(options=options) as client:
            print("   🤖 Descomponiendo user stories en tareas...")
            
            await client.query(query)
            
            full_response = ""
            async for message in client.receive_response():
                if hasattr(message, 'text'):
                    full_response += message.text
                else:
                    full_response += str(message)
            
            # Parsear JSON
            try:
                start = full_response.find('{')
                end = full_response.rfind('}') + 1
                
                if start == -1 or end <= start:
                    raise ValueError("No JSON found in response")
                
                json_str = full_response[start:end]
                data = json.loads(json_str)
                
                tasks: List[Task] = data.get('tasks', [])
                backend_count = len([t for t in tasks if t['assigned_to'] == 'backend'])
                frontend_count = len([t for t in tasks if t['assigned_to'] == 'frontend'])
                
                print(f"\n   ✅ Sprint {state['current_sprint']} planificado:")
                print(f"      📋 {len(tasks)} tareas totales")
                print(f"      🔧 {backend_count} tareas backend")
                print(f"      🎨 {frontend_count} tareas frontend")
                print(f"      📝 {data.get('sprint_summary', 'N/A')[:80]}...")
                
                # Mostrar algunas tareas
                print("\n   📋 Primeras tareas:")
                for task in tasks[:3]:
                    deps = f" (depende de: {', '.join(task['dependencies'])})" if task['dependencies'] else ""
                    print(f"      [{task['id']}] {task['title']}")
                    print(f"         Asignado a: {task['assigned_to'].upper()}{deps}")
                
                if len(tasks) > 3:
                    print(f"\n      ... y {len(tasks) - 3} tareas más")
                
                return {
                    **state,
                    'tasks': tasks,
                    'sprint_planned': True,
                    'updated_at': str(asyncio.get_event_loop().time())
                }
                
            except json.JSONDecodeError as e:
                print(f"   ❌ Error parseando JSON: {e}")
                print(f"   Respuesta recibida: {full_response[:200]}...")
                
                return {
                    **state,
                    'sprint_planned': False,
                    'errors': state['errors'] + [f"Scrum Master: JSON parse error - {e}"]
                }
        
    except Exception as e:
        print(f"   ❌ Error en Scrum Master: {e}")
        
        return {
            **state,
            'sprint_planned': False,
            'errors': state['errors'] + [f"Scrum Master failed: {e}"]
        }


def scrum_master_node(state: DevelopmentState) -> DevelopmentState:
    """Wrapper sincrónico"""
    return asyncio.run(scrum_master_node_async(state))