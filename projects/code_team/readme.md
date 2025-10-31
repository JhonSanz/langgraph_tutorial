# 🤖 AI Dev Team

**Equipo de desarrollo de software automatizado usando LangGraph + Claude Agent SDK**

Un sistema completo que simula un equipo de desarrollo de software, donde cada rol (Product Manager, Scrum Master, Backend Dev, Frontend Dev, QA) es un agente de Claude que trabaja en conjunto para crear aplicaciones completas.

## 🎯 ¿Qué hace?

Dale un requerimiento en lenguaje natural y el equipo AI creará una aplicación completa:

```bash
python -m src.main "Crear una aplicación de gestión de tareas con autenticación"
```

El sistema automáticamente:
1. 👔 **Product Manager** → Crea user stories detalladas
2. 🏃 **Scrum Master** → Planifica el sprint y asigna tareas
3. 🔧 **Backend Dev** → Implementa el código FastAPI
4. 🎨 **Frontend Dev** → Implementa el código React
5. 🧪 **QA Engineer** → Crea tests unitarios completos
6. 📋 **Review** → Genera resumen ejecutivo

## 🏗️ Arquitectura

```
                ┌─────────────────────────────┐
                │   LangGraph (Orquestador)   │
                │   • Control de flujo         │
                │   • Validaciones            │
                │   • Coordinación            │
                └──────────────┬──────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        v                      v                      v
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Product    │    │    Backend   │    │     QA       │
│   Manager    │    │   Developer  │    │   Engineer   │
│ (Claude SDK) │    │ (Claude SDK) │    │ (Claude SDK) │
└──────────────┘    └──────────────┘    └──────────────┘
                             │
                    ┌────────┴────────┐
                    │      MCPs        │
                    │  • Filesystem    │
                    │  • Git (opt)     │
                    └──────────────────┘
```

### ¿Por qué LangGraph + Claude Agent SDK?

| Aspecto | LangGraph | Claude Agent SDK |
|---------|-----------|------------------|
| **Rol** | Orquestación | Implementación |
| **Control** | Flujo explícito | Autonomía |
| **Validación** | Entre nodos | Dentro de tareas |
| **MCPs** | Manual | Nativo |

**La combinación perfecta**:
- LangGraph coordina el equipo
- Claude Agent SDK hace el trabajo técnico
- MCPs proveen acceso al filesystem

## 📦 Instalación

### Prerrequisitos

- Python 3.10+
- Node.js (para MCPs)
- Anthropic API Key

### Setup

```bash
# Clonar
git clone <repo>
cd ai-dev-team

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -e .

# Instalar MCPs (opcional pero recomendado)
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-git

# Configurar API key
cp .env.example .env
# Editar .env y agregar tu ANTHROPIC_API_KEY
```

## 🚀 Uso

### Básico

```bash
python -m src.main "Crear una app de gestión de tareas"
```

### Con opciones

```bash
# Nombre personalizado
python -m src.main "Blog platform with auth" --name "my-blog"

# Workspace personalizado
python -m src.main "E-commerce site" --workspace ./projects

# Output personalizado
python -m src.main "Social network" --output ./results

# Ver diagrama del workflow
python -m src.main --show-workflow
```

### Ejemplos

```bash
# App de tareas
python -m src.main "Aplicación de gestión de tareas con usuarios, autenticación y CRUD completo"

# Blog
python -m src.main "Blog platform con posts, comments, categories y búsqueda"

# E-commerce
python -m src.main "E-commerce site con productos, carrito de compras y checkout"

# Dashboard
python -m src.main "Admin dashboard con gráficos, tablas y exportación de datos"

# API REST
python -m src.main "RESTful API para gestión de inventario con autenticación JWT"
```

## 📊 Output

Después de ejecutar, obtendrás:

```
output/
├── PROJECT_SUMMARY.md      # Resumen ejecutivo
├── user_stories.json       # User stories creadas por PM
├── tasks.json              # Tareas asignadas por SM
└── metadata.json           # Estadísticas del proyecto

workspace/
└── <project-name>/
    ├── backend/
    │   ├── app/
    │   │   ├── main.py
    │   │   ├── models/
    │   │   ├── schemas/
    │   │   ├── crud/
    │   │   └── routers/
    │   ├── tests/
    │   └── requirements.txt
    │
    └── frontend/
        ├── src/
        │   ├── components/
        │   ├── pages/
        │   ├── features/
        │   └── store/
        └── package.json
```

## 👥 El Equipo

### 👔 Product Manager
- Analiza el requerimiento del usuario
- Crea user stories en formato estándar
- Define acceptance criteria
- Prioriza features
- Estima story points

**Tecnologías**: Claude Agent SDK

### 🏃 Scrum Master
- Lee las user stories
- Descompone en tareas técnicas
- Asigna tareas a backend/frontend
- Identifica dependencias
- Planifica el sprint

**Tecnologías**: Claude Agent SDK

### 🔧 Backend Developer
- Implementa código FastAPI
- Crea modelos SQLAlchemy
- Define schemas Pydantic
- Implementa CRUD operations
- Crea endpoints API

**Tecnologías**: Claude Agent SDK + Filesystem MCP

**Tech Stack**: FastAPI, SQLAlchemy, PostgreSQL, Pydantic

### 🎨 Frontend Developer
- Implementa código React + TypeScript
- Crea componentes reutilizables
- Implementa páginas y routing
- Configura Redux Toolkit
- Integra con backend API

**Tecnologías**: Claude Agent SDK + Filesystem MCP

**Tech Stack**: React, TypeScript, TailwindCSS, Redux Toolkit

### 🧪 QA Engineer
- Analiza el código generado
- Crea tests unitarios
- Configura pytest (backend)
- Configura Vitest (frontend)
- Calcula coverage esperado

**Tecnologías**: Claude Agent SDK + Filesystem MCP

**Tools**: pytest, Vitest, React Testing Library

## 🔧 Configuración Avanzada

### Tech Stack Personalizado

Edita `src/state.py`:

```python
backend_tech_stack={
    "framework": "Django",  # Cambiar a Django
    "database": "MongoDB",
    "orm": "MongoEngine"
}
```

### Agregar un nuevo rol

1. Crear nodo en `src/nodes/tu_rol.py`
2. Agregar al workflow en `src/graph.py`
3. Definir routing logic

### MCPs Adicionales

Edita los nodos de developers para agregar más MCPs:

```python
mcp_servers = {
    "filesystem": {...},
    "git": {...},
    "github": {...},
    "postgres": {...}
}
```

## 📈 Métricas

El sistema genera estadísticas completas:

- ✅ User stories creadas
- ✅ Tareas planificadas y completadas
- ✅ Archivos de código generados
- ✅ Test coverage
- ✅ Bugs encontrados
- ✅ Deployment readiness

## 🎓 Casos de Uso

### 1. Prototipado Rápido
Genera MVPs completos en minutos para validar ideas.

### 2. Aprendizaje
Estudia el código generado para aprender best practices.

### 3. Baseline de Proyectos
Usa el código generado como punto de partida para proyectos reales.

### 4. Documentación
Genera user stories y tasks para proyectos existentes.

### 5. Testing
Aprende cómo estructurar tests para tus proyectos.

## ⚠️ Limitaciones

- **No reemplaza developers reales**: El código requiere revisión
- **Context limits**: Proyectos muy grandes pueden necesitar iteraciones
- **No ejecuta código**: Solo genera archivos
- **MCPs requeridos**: Sin MCPs, no puede escribir archivos
- **Costo**: Usa API de Claude (puede ser costoso para proyectos grandes)

## 🔄 Flujo Completo

```
User Requirement
       │
       v
┌─────────────────┐
│ Product Manager │ → Analiza y crea user stories
└────────┬────────┘
         │
         v
┌─────────────────┐
│  Scrum Master   │ → Planifica sprint, asigna tareas
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Backend Dev     │ → Implementa FastAPI
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Frontend Dev    │ → Implementa React (depende de backend)
└────────┬────────┘
         │
         v
┌─────────────────┐
│ QA Engineer     │ → Crea tests unitarios
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Review & Deploy │ → Genera resumen, valida calidad
└────────┬────────┘
         │
         v
    Project Complete!
```

## 🛠️ Troubleshooting

### Error: "ANTHROPIC_API_KEY not found"
```bash
cp .env.example .env
# Editar .env con tu API key
```

### Error: "MCP server not found"
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

### El código generado no compila
- Es normal, requiere revisión manual
- Usa el código como baseline
- Ajusta según tus necesidades

### Coverage muy bajo
- El QA Engineer estima coverage
- Revisa los tests generados
- Agrega tests manualmente si es necesario

## 🚀 Próximos Pasos

Después de generar el proyecto:

1. **Revisar el código generado**
2. **Instalar dependencias**:
   ```bash
   cd workspace/<project>/backend
   pip install -r requirements.txt
   
   cd ../frontend
   npm install
   ```
3. **Ejecutar tests**:
   ```bash
   # Backend
   pytest
   
   # Frontend
   npm test
   ```
4. **Ajustar y personalizar**
5. **Deploy a producción**

## 📚 Recursos

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)

## 🤝 Contribuir

Ideas para contribuciones:

- Agregar más roles (DevOps, Security Engineer)
- Soporte para más tech stacks
- Integración con GitHub para PRs automáticos
- Dashboard web para visualizar el progreso
- Modo interactivo con human-in-the-loop

## 📝 Licencia

MIT

---

**Creado con ❤️ usando LangGraph + Claude Agent SDK**

¿Preguntas? Abre un issue o contáctanos.

¡Feliz desarrollo automatizado! 🚀