"""
Backend Developer - Nodo que implementa el código backend con FastAPI.

Este nodo:
1. Lee las tareas asignadas a backend
2. Crea la estructura del proyecto FastAPI
3. Implementa modelos, schemas, CRUD, endpoints
4. Escribe código siguiendo best practices
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from src.state import DevelopmentState, Task, CodeFile


BACKEND_DEVELOPER_PROMPT = """Eres un Senior Backend Developer especializado en Python y FastAPI.

Expertise:
- FastAPI: routing, dependency injection, middleware, Pydantic models
- SQLAlchemy: ORM, relationships, migrations
- PostgreSQL: diseño de schemas, queries eficientes
- Best practices: código limpio, SOLID, DRY, testing

Tech Stack:
- FastAPI 0.109+
- SQLAlchemy 2.0+
- PostgreSQL 15+
- Pydantic 2.0+
- Python 3.11+

Estructura de proyecto estándar:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuración
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   │   └── __init__.py
│   ├── schemas/             # Pydantic schemas
│   │   └── __init__.py
│   ├── crud/                # CRUD operations
│   │   └── __init__.py
│   └── routers/             # API routers
│       └── __init__.py
├── requirements.txt
└── .env.example
```

Principios de código:
- Type hints siempre
- Docstrings para funciones públicas
- Validación con Pydantic
- Error handling apropiado
- Async/await donde sea apropiado
- Código limpio y legible

Tu trabajo es escribir código production-ready, no prototipos.
"""


def load_mcp_config():
    """Carga configuración de MCPs"""
    return {
        "filesystem": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
        }
    }


async def backend_developer_node_async(state: DevelopmentState) -> DevelopmentState:
    """
    Nodo del Backend Developer - Implementa código FastAPI.
    """
    
    print("\n🔧 Backend Developer - Implementando código...")
    
    # Filtrar tareas de backend
    all_tasks = state['tasks']
    backend_tasks = [t for t in all_tasks if t['assigned_to'] == 'backend']
    
    if not backend_tasks:
        print("   ℹ️  No hay tareas de backend asignadas")
        return {
            **state,
            'backend_completed': True
        }
    
    workspace = Path(state['workspace_path'])
    backend_dir = workspace / state['project_name'] / 'backend'
    
    # Preparar contexto de tareas
    tasks_summary = "\n".join([
        f"[{task['id']}] {task['title']}\n  Descripción: {task['description']}\n  Dependencias: {task['dependencies']}"
        for task in backend_tasks
    ])
    
    context = f"""
Proyecto: {state['project_name']}
Workspace: {backend_dir}

Tareas asignadas a Backend:
{tasks_summary}

User Stories de referencia:
{json.dumps(state['user_stories'], indent=2)}
"""
    
    # Configurar Claude Agent con filesystem MCP
    mcp_servers = load_mcp_config()
    mcp_servers["filesystem"]["args"][-1] = str(workspace)
    
    options = ClaudeAgentOptions(
        mcp_servers=mcp_servers,
        system_prompt=BACKEND_DEVELOPER_PROMPT,
        allowed_tools=["mcp__filesystem__*"],
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        max_tokens=8000,
    )
    
    query = f"""{context}

Por favor, implementa el backend completo del proyecto usando FastAPI.

Pasos:
1. Crea la estructura de directorios estándar en: {backend_dir}
2. Implementa los archivos necesarios para cada tarea:
   - main.py con FastAPI app
   - database.py con SQLAlchemy setup
   - models/ con modelos SQLAlchemy
   - schemas/ con schemas Pydantic
   - crud/ con operaciones CRUD
   - routers/ con endpoints API
   - requirements.txt con dependencias
   - .env.example con variables de entorno

3. El código debe:
   - Seguir best practices de FastAPI
   - Incluir type hints completos
   - Tener error handling apropiado
   - Ser production-ready
   - Incluir comentarios donde sea necesario

4. Asegúrate de:
   - Usar async/await correctamente
   - Implementar validación con Pydantic
   - Configurar CORS si es necesario
   - Incluir health check endpoint
   - Documentar API con docstrings

Usa el filesystem MCP para crear todos los archivos necesarios.

Al final, responde con un JSON:
{{
  "files_created": ["path/to/file1.py", "path/to/file2.py", ...],
  "summary": "Resumen de lo implementado",
  "endpoints": [
    {{"method": "GET", "path": "/api/users", "description": "..."}}
  ]
}}

¡Adelante! Crea el backend completo.
"""
    
    try:
        async with ClaudeSDKClient(options=options) as client:
            print("   🤖 Escribiendo código backend...")
            print("   ⏳ Esto puede tomar varios minutos...")
            
            await client.query(query)
            
            full_response = ""
            async for message in client.receive_response():
                if hasattr(message, 'text'):
                    text = message.text
                    full_response += text
                    # Mostrar progreso
                    if "Creating" in text or "created" in text:
                        preview = text[:60].replace('\n', ' ')
                        print(f"      {preview}...", end='\r')
                else:
                    full_response += str(message)
            
            print("\n   ✅ Código backend generado")
            
            # Parsear respuesta
            files_created = []
            try:
                start = full_response.find('{')
                end = full_response.rfind('}') + 1
                
                if start != -1 and end > start:
                    json_str = full_response[start:end]
                    data = json.loads(json_str)
                    
                    files_created = data.get('files_created', [])
                    summary = data.get('summary', '')
                    endpoints = data.get('endpoints', [])
                    
                    print(f"\n   📄 Archivos creados: {len(files_created)}")
                    print(f"   🔌 Endpoints: {len(endpoints)}")
                    
                    # Mostrar algunos endpoints
                    if endpoints:
                        print("\n   API Endpoints:")
                        for ep in endpoints[:5]:
                            print(f"      {ep.get('method', 'GET')} {ep.get('path', 'N/A')}")
                    
                    print(f"\n   📝 {summary[:150]}...")
                    
            except json.JSONDecodeError:
                # Si no hay JSON válido, buscar archivos mencionados
                if "main.py" in full_response:
                    files_created.append("backend/app/main.py")
                if "database.py" in full_response:
                    files_created.append("backend/app/database.py")
            
            # Crear lista de CodeFile
            backend_files: List[CodeFile] = []
            for file_path in files_created:
                backend_files.append(CodeFile(
                    path=file_path,
                    content="[Generated by Claude Agent]",
                    language="python",
                    created_by="backend_developer"
                ))
            
            return {
                **state,
                'backend_files': backend_files,
                'backend_completed': True,
                'updated_at': str(asyncio.get_event_loop().time())
            }
            
    except Exception as e:
        print(f"   ❌ Error en Backend Developer: {e}")
        
        return {
            **state,
            'backend_completed': False,
            'errors': state['errors'] + [f"Backend Developer failed: {e}"]
        }


def backend_developer_node(state: DevelopmentState) -> DevelopmentState:
    """Wrapper sincrónico"""
    return asyncio.run(backend_developer_node_async(state))