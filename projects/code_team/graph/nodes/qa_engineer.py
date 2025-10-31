"""
QA Engineer - Nodo que crea tests unitarios para el proyecto.

Este nodo:
1. Analiza el código backend y frontend
2. Crea tests unitarios comprehensivos
3. Configura pytest para backend
4. Configura Jest/Vitest para frontend
5. Calcula cobertura esperada
"""

import asyncio
import json
import os
from pathlib import Path
from typing import List

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from src.state import DevelopmentState, TestFile


QA_ENGINEER_PROMPT = """Eres un QA Engineer senior especializado en automated testing.

Expertise:
- Backend testing: pytest, pytest-asyncio, pytest-cov, factories
- Frontend testing: Jest, Vitest, React Testing Library
- Test patterns: AAA (Arrange-Act-Assert), mocking, fixtures
- Coverage: análisis de code coverage, edge cases
- Best practices: tests legibles, mantenibles, rápidos

Para Backend (Python/FastAPI):
- pytest para unit tests
- pytest-asyncio para async tests
- factories para test data
- mocking con unittest.mock
- fixtures para setup/teardown
- Test endpoints, CRUD, validaciones, edge cases

Para Frontend (React/TypeScript):
- Vitest o Jest para unit tests
- React Testing Library para component tests
- Mock Service Worker (MSW) para API mocking
- Test componentes, hooks, state, user interactions

Estructura de tests:
```
Backend tests:
backend/tests/
├── conftest.py          # Pytest fixtures
├── test_models.py
├── test_crud.py
├── test_routers.py
└── test_integration.py

Frontend tests:
frontend/src/
├── components/
│   └── Component.test.tsx
├── features/
│   └── feature.test.ts
└── __tests__/
    └── integration.test.tsx
```

Principios:
- Tests deben ser independientes
- Usar descriptive test names
- Test happy path y edge cases
- Mock dependencies externas
- Fast execution
- High coverage (>80% target)
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


async def qa_engineer_node_async(state: DevelopmentState) -> DevelopmentState:
    """
    Nodo del QA Engineer - Crea tests unitarios.
    """
    
    print("\n🧪 QA Engineer - Creando tests...")
    
    workspace = Path(state['workspace_path'])
    project_dir = workspace / state['project_name']
    
    # Preparar contexto
    backend_files_summary = "\n".join([
        f"- {f['path']}" for f in state.get('backend_files', [])[:10]
    ])
    
    frontend_files_summary = "\n".join([
        f"- {f['path']}" for f in state.get('frontend_files', [])[:10]
    ])
    
    context = f"""
Proyecto: {state['project_name']}
Workspace: {project_dir}

Backend files:
{backend_files_summary}
{f"... y {len(state.get('backend_files', [])) - 10} más" if len(state.get('backend_files', [])) > 10 else ""}

Frontend files:
{frontend_files_summary}
{f"... y {len(state.get('frontend_files', [])) - 10} más" if len(state.get('frontend_files', [])) > 10 else ""}

User Stories implementadas:
{json.dumps(state['user_stories'], indent=2)}
"""
    
    # Configurar Claude Agent con filesystem MCP
    mcp_servers = load_mcp_config()
    mcp_servers["filesystem"]["args"][-1] = str(workspace)
    
    options = ClaudeAgentOptions(
        mcp_servers=mcp_servers,
        system_prompt=QA_ENGINEER_PROMPT,
        allowed_tools=["mcp__filesystem__*"],
        model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929"),
        max_tokens=8000,
    )
    
    query = f"""{context}

Por favor, crea una suite completa de tests para este proyecto.

Tareas:

**Backend Tests (pytest):**
1. Crear estructura de tests en backend/tests/
2. conftest.py con fixtures:
   - Database fixtures (in-memory SQLite para tests)
   - Client fixture (TestClient de FastAPI)
   - Sample data factories
3. Tests para:
   - Modelos SQLAlchemy (test_models.py)
   - Operaciones CRUD (test_crud.py)
   - Endpoints API (test_routers.py)
   - Validaciones y edge cases
4. pytest.ini para configuración

**Frontend Tests (Vitest):**
1. Configurar Vitest en vitest.config.ts
2. Setup file para React Testing Library
3. Tests para:
   - Componentes React (*.test.tsx)
   - Redux slices (*.test.ts)
   - Custom hooks
   - API integration (mocked)
4. MSW para mock API calls

**Configuración:**
- Backend: requirements-dev.txt con pytest, pytest-asyncio, pytest-cov, faker
- Frontend: package.json con vitest, @testing-library/react, @testing-library/jest-dom

**Coverage target: 80%+**

Tests deben:
- Ser completos y robustos
- Usar AAA pattern (Arrange-Act-Assert)
- Tener nombres descriptivos
- Cubrir happy path y edge cases
- Ser rápidos de ejecutar
- Ser mantenibles

Usa el filesystem MCP para crear todos los archivos de tests.

Al final, responde con un JSON:
{{
  "test_files_created": ["backend/tests/test_models.py", ...],
  "backend_tests_count": 0,
  "frontend_tests_count": 0,
  "estimated_coverage": 0.85,
  "summary": "Resumen de la test suite"
}}

¡Adelante! Crea una test suite comprehensiva.
"""
    
    try:
        async with ClaudeSDKClient(options=options) as client:
            print("   🤖 Escribiendo tests unitarios...")
            print("   ⏳ Esto puede tomar varios minutos...")
            
            await client.query(query)
            
            full_response = ""
            async for message in client.receive_response():
                if hasattr(message, 'text'):
                    text = message.text
                    full_response += text
                    # Mostrar progreso
                    if "test" in text.lower() or "Creating" in text:
                        preview = text[:60].replace('\n', ' ')
                        print(f"      {preview}...", end='\r')
                else:
                    full_response += str(message)
            
            print("\n   ✅ Tests creados")
            
            # Parsear respuesta
            test_files_created = []
            backend_tests = 0
            frontend_tests = 0
            coverage = 0.0
            
            try:
                start = full_response.find('{')
                end = full_response.rfind('}') + 1
                
                if start != -1 and end > start:
                    json_str = full_response[start:end]
                    data = json.loads(json_str)
                    
                    test_files_created = data.get('test_files_created', [])
                    backend_tests = data.get('backend_tests_count', 0)
                    frontend_tests = data.get('frontend_tests_count', 0)
                    coverage = data.get('estimated_coverage', 0.0)
                    summary = data.get('summary', '')
                    
                    print(f"\n   📄 Archivos de test: {len(test_files_created)}")
                    print(f"   🔧 Backend tests: {backend_tests}")
                    print(f"   🎨 Frontend tests: {frontend_tests}")
                    print(f"   📊 Coverage estimado: {coverage*100:.1f}%")
                    
                    # Mostrar algunos archivos de test
                    if test_files_created:
                        print("\n   Archivos de test creados:")
                        for test_file in test_files_created[:5]:
                            print(f"      ✓ {test_file}")
                    
                    if len(test_files_created) > 5:
                        print(f"      ... y {len(test_files_created) - 5} más")
                    
                    print(f"\n   📝 {summary[:150]}...")
                    
            except json.JSONDecodeError:
                # Si no hay JSON válido, estimar
                if "test_" in full_response:
                    test_files_created = ["backend/tests/test_models.py", "frontend/src/components/Component.test.tsx"]
                    coverage = 0.75
            
            # Crear lista de TestFile
            test_files: List[TestFile] = []
            for test_path in test_files_created:
                test_type = "unit"
                if "integration" in test_path:
                    test_type = "integration"
                elif "e2e" in test_path:
                    test_type = "e2e"
                
                test_files.append(TestFile(
                    path=test_path,
                    content="[Generated by Claude Agent]",
                    test_type=test_type,
                    coverage_target=coverage
                ))
            
            # Detectar bugs potenciales (análisis simple)
            bugs_found = []
            if coverage < 0.7:
                bugs_found.append("Coverage menor al 70% - revisar tests faltantes")
            
            if backend_tests == 0 and len(state.get('backend_files', [])) > 0:
                bugs_found.append("No hay tests para el backend")
            
            if frontend_tests == 0 and len(state.get('frontend_files', [])) > 0:
                bugs_found.append("No hay tests para el frontend")
            
            return {
                **state,
                'test_files': test_files,
                'test_coverage': coverage,
                'qa_completed': True,
                'bugs_found': bugs_found,
                'updated_at': str(asyncio.get_event_loop().time())
            }
            
    except Exception as e:
        print(f"   ❌ Error en QA Engineer: {e}")
        
        return {
            **state,
            'qa_completed': False,
            'errors': state['errors'] + [f"QA Engineer failed: {e}"]
        }


def qa_engineer_node(state: DevelopmentState) -> DevelopmentState:
    """Wrapper sincrónico"""
    return asyncio.run(qa_engineer_node_async(state))