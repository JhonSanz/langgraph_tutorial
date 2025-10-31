"""
Frontend Developer - Nodo que implementa el código frontend con React.

Este nodo:
1. Lee las tareas asignadas a frontend
2. Crea la estructura del proyecto React
3. Implementa componentes, páginas, state management
4. Integra con el backend API
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from src.state import DevelopmentState, Task, CodeFile


FRONTEND_DEVELOPER_PROMPT = """Eres un Senior Frontend Developer especializado en React y TypeScript.

Expertise:
- React 18+: hooks, context, custom hooks, performance optimization
- TypeScript: tipos avanzados, generics, utility types
- TailwindCSS: utility classes, responsive design, custom themes
- Redux Toolkit: slices, async thunks, RTK Query
- React Router: routing, navigation, protected routes
- Axios: API integration, interceptors, error handling

Tech Stack:
- React 18+ con TypeScript
- TailwindCSS para styling
- Redux Toolkit para state management
- React Router para routing
- Axios para HTTP requests
- Vite como build tool

Estructura de proyecto estándar:
```
frontend/
├── src/
│   ├── main.tsx             # Entry point
│   ├── App.tsx              # Root component
│   ├── components/          # Reusable components
│   │   └── common/
│   ├── pages/               # Page components
│   ├── features/            # Feature-based modules
│   │   └── users/
│   │       ├── usersSlice.ts
│   │       ├── usersAPI.ts
│   │       └── Users.tsx
│   ├── store/               # Redux store
│   │   └── index.ts
│   ├── api/                 # API configuration
│   │   └── axios.ts
│   ├── hooks/               # Custom hooks
│   ├── types/               # TypeScript types
│   └── utils/               # Utility functions
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

Principios de código:
- TypeScript estricto
- Componentes funcionales con hooks
- Props typing completo
- Code splitting cuando sea apropiado
- Responsive design (mobile-first)
- Accesibilidad (a11y)
- Error boundaries
- Loading states
- Código limpio y mantenible

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


async def frontend_developer_node_async(state: DevelopmentState) -> DevelopmentState:
    """
    Nodo del Frontend Developer - Implementa código React.
    """
    
    print("\n🎨 Frontend Developer - Implementando UI...")
    
    # Filtrar tareas de frontend
    all_tasks = state['tasks']
    frontend_tasks = [t for t in all_tasks if t['assigned_to'] == 'frontend']
    
    if not frontend_tasks:
        print("   ℹ️  No hay tareas de frontend asignadas")
        return {
            **state,
            'frontend_completed': True
        }
    
    workspace = Path(state['workspace_path'])
    frontend_dir = workspace / state['project_name'] / 'frontend'
    
    # Preparar contexto de tareas
    tasks_summary = "\n".join([
        f"[{task['id']}] {task['title']}\n  Descripción: {task['description']}\n  Dependencias: {task['dependencies']}"
        for task in frontend_tasks
    ])
    
    # Información del backend (para integración API)
    backend_info = ""
    if state.get('backend_files'):
        backend_info = f"""
Backend API disponible:
- Archivos backend: {len(state['backend_files'])} archivos creados
- Integra con estos endpoints al crear componentes
"""
    
    context = f"""
Proyecto: {state['project_name']}
Workspace: {frontend_dir}

Tareas asignadas a Frontend:
{tasks_summary}

{backend_info}

User Stories de referencia:
{json.dumps(state['user_stories'], indent=2)}
"""
    
    # Configurar Claude Agent con filesystem MCP
    mcp_servers = load_mcp_config()
    mcp_servers["filesystem"]["args"][-1] = str(workspace)
    
    options = ClaudeAgentOptions(
        mcp_servers=mcp_servers,
        system_prompt=FRONTEND_DEVELOPER_PROMPT,
        allowed_tools=["mcp__filesystem__*"],
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        max_tokens=8000,
    )
    
    query = f"""{context}

Por favor, implementa el frontend completo del proyecto usando React + TypeScript.

Pasos:
1. Crea la estructura de directorios estándar en: {frontend_dir}
2. Implementa los archivos necesarios para cada tarea:
   - main.tsx como entry point
   - App.tsx con routing
   - components/ con componentes reutilizables
   - pages/ con páginas principales
   - features/ con features Redux
   - store/ con configuración Redux
   - api/ con configuración Axios
   - types/ con tipos TypeScript

3. El código debe:
   - Usar TypeScript estricto
   - Implementar state management con Redux Toolkit
   - Integrar con backend API usando Axios
   - Ser responsive con TailwindCSS
   - Incluir loading states y error handling
   - Tener componentes reutilizables

4. Configuración:
   - package.json con todas las dependencias
   - tsconfig.json con configuración strict
   - tailwind.config.js
   - vite.config.ts

5. Features importantes:
   - Routing con React Router
   - Forms con validación
   - API integration con error handling
   - Loading spinners
   - Toast notifications (si es necesario)

Usa el filesystem MCP para crear todos los archivos necesarios.

Al final, responde con un JSON:
{{
  "files_created": ["path/to/Component.tsx", "path/to/page.tsx", ...],
  "summary": "Resumen de lo implementado",
  "pages": [
    {{"name": "Home", "route": "/", "description": "..."}}
  ],
  "components": ["Header", "Footer", "UserCard", ...]
}}

¡Adelante! Crea el frontend completo.
"""
    
    try:
        async with ClaudeSDKClient(options=options) as client:
            print("   🤖 Escribiendo código frontend...")
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
            
            print("\n   ✅ Código frontend generado")
            
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
                    pages = data.get('pages', [])
                    components = data.get('components', [])
                    
                    print(f"\n   📄 Archivos creados: {len(files_created)}")
                    print(f"   📱 Páginas: {len(pages)}")
                    print(f"   🧩 Componentes: {len(components)}")
                    
                    # Mostrar algunas páginas
                    if pages:
                        print("\n   Páginas principales:")
                        for page in pages[:5]:
                            print(f"      {page.get('route', 'N/A')} - {page.get('name', 'N/A')}")
                    
                    print(f"\n   📝 {summary[:150]}...")
                    
            except json.JSONDecodeError:
                # Si no hay JSON válido, buscar archivos mencionados
                if "App.tsx" in full_response:
                    files_created.append("frontend/src/App.tsx")
                if "main.tsx" in full_response:
                    files_created.append("frontend/src/main.tsx")
            
            # Crear lista de CodeFile
            frontend_files: List[CodeFile] = []
            for file_path in files_created:
                # Determinar el lenguaje
                ext = Path(file_path).suffix
                language = "typescript" if ext in ['.ts', '.tsx'] else "javascript"
                
                frontend_files.append(CodeFile(
                    path=file_path,
                    content="[Generated by Claude Agent]",
                    language=language,
                    created_by="frontend_developer"
                ))
            
            return {
                **state,
                'frontend_files': frontend_files,
                'frontend_completed': True,
                'updated_at': str(asyncio.get_event_loop().time())
            }
            
    except Exception as e:
        print(f"   ❌ Error en Frontend Developer: {e}")
        
        return {
            **state,
            'frontend_completed': False,
            'errors': state['errors'] + [f"Frontend Developer failed: {e}"]
        }


def frontend_developer_node(state: DevelopmentState) -> DevelopmentState:
    """Wrapper sincrónico"""
    return asyncio.run(frontend_developer_node_async(state))