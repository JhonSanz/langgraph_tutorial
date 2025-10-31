"""
LangGraph Workflow - Orquestación del equipo de desarrollo de software.

Flujo:
1. Product Manager → Crea user stories
2. Scrum Master → Planifica sprint y asigna tareas
3. Backend Developer → Implementa FastAPI
4. Frontend Developer → Implementa React (espera a backend)
5. QA Engineer → Crea tests
6. Review & Deploy → Revisión final
"""

from typing import Literal
from langgraph.graph import StateGraph, END

from src.state import DevelopmentState
from src.nodes.product_manager import product_manager_node
from src.nodes.scrum_master import scrum_master_node
from src.nodes.backend_developer import backend_developer_node
from src.nodes.frontend_developer import frontend_developer_node
from src.nodes.qa_engineer import qa_engineer_node


# ============ ROUTING FUNCTIONS ============


def should_continue_after_pm(state: DevelopmentState) -> Literal["scrum_master", "end"]:
    """Decide si continuar después del Product Manager"""

    if not state["product_backlog_created"]:
        print("❌ Product backlog no fue creado. Terminando...")
        return "end"

    if len(state["user_stories"]) == 0:
        print("⚠️  No hay user stories. Terminando...")
        return "end"

    return "scrum_master"


def should_continue_after_scrum(
    state: DevelopmentState,
) -> Literal["backend_dev", "end"]:
    """Decide si continuar después del Scrum Master"""

    if not state["sprint_planned"]:
        print("❌ Sprint no fue planificado. Terminando...")
        return "end"

    if len(state["tasks"]) == 0:
        print("⚠️  No hay tareas asignadas. Terminando...")
        return "end"

    return "backend_dev"


def should_continue_after_backend(
    state: DevelopmentState,
) -> Literal["frontend_dev", "end"]:
    """Decide si continuar después de Backend"""

    if not state["backend_completed"]:
        print("❌ Backend no fue completado. Terminando...")
        return "end"

    # El frontend necesita que el backend esté listo
    return "frontend_dev"


def should_continue_after_frontend(state: DevelopmentState) -> Literal["qa", "end"]:
    """Decide si continuar después de Frontend"""

    if not state["frontend_completed"]:
        print("❌ Frontend no fue completado. Terminando...")
        return "end"

    return "qa"


def should_continue_after_qa(state: DevelopmentState) -> Literal["review", "end"]:
    """Decide si continuar después de QA"""

    if not state["qa_completed"]:
        print("❌ QA no fue completado. Terminando...")
        return "end"

    # Si hay bugs críticos, detener
    critical_bugs = [b for b in state["bugs_found"] if "critical" in b.lower()]
    if critical_bugs:
        print(f"⚠️  Se encontraron {len(critical_bugs)} bugs críticos")
        return "end"

    return "review"


# ============ NODO DE REVISIÓN FINAL ============


def review_and_summary_node(state: DevelopmentState) -> DevelopmentState:
    """
    Nodo de revisión final y generación de resumen.
    Este podría pedir human review en un escenario real.
    """

    print("\n📋 Generando resumen del proyecto...")

    # Calcular estadísticas
    total_backend_files = len(state["backend_files"])
    total_frontend_files = len(state["frontend_files"])
    total_test_files = len(state["test_files"])

    # Contar tareas completadas
    completed_tasks = [t for t in state["tasks"] if t["status"] == "completed"]

    # Generar resumen
    summary = f"""
# 🎉 Proyecto Completado: {state['project_name']}

## 📊 Resumen Ejecutivo

El equipo de desarrollo ha completado exitosamente el proyecto.

### Equipo
- 👔 Product Manager: {len(state['user_stories'])} user stories creadas
- 🏃 Scrum Master: {len(state['tasks'])} tareas planificadas
- 🔧 Backend Developer: {total_backend_files} archivos creados
- 🎨 Frontend Developer: {total_frontend_files} archivos creados
- 🧪 QA Engineer: {total_test_files} archivos de test

### Métricas
- **User Stories**: {len(state['user_stories'])}
- **Tareas totales**: {len(state['tasks'])}
- **Tareas completadas**: {len(completed_tasks)}
- **Coverage de tests**: {state['test_coverage']*100:.1f}%
- **Bugs encontrados**: {len(state['bugs_found'])}

### Tech Stack
**Backend:**
{chr(10).join(f"- {k}: {v}" for k, v in state['backend_tech_stack'].items())}

**Frontend:**
{chr(10).join(f"- {k}: {v}" for k, v in state['frontend_tech_stack'].items())}

### Archivos Generados
- **Backend**: {total_backend_files} archivos Python
- **Frontend**: {total_frontend_files} archivos TypeScript/React
- **Tests**: {total_test_files} archivos de test

### Estado del Deployment
"""

    # Determinar si está listo para deploy
    deployment_ready = (
        state["backend_completed"]
        and state["frontend_completed"]
        and state["qa_completed"]
        and state["test_coverage"] >= 0.7
        and len(state["bugs_found"]) == 0
    )

    if deployment_ready:
        summary += "✅ **LISTO PARA DEPLOYMENT**\n"
    else:
        summary += "⚠️ **REQUIERE REVISIÓN ADICIONAL**\n\n"

        if state["test_coverage"] < 0.7:
            summary += (
                f"- Coverage bajo: {state['test_coverage']*100:.1f}% (mínimo: 70%)\n"
            )

        if len(state["bugs_found"]) > 0:
            summary += f"- Bugs encontrados: {len(state['bugs_found'])}\n"
            for bug in state["bugs_found"]:
                summary += f"  • {bug}\n"

    # Si hay errores
    if state["errors"]:
        summary += "\n### ⚠️ Errores durante el desarrollo\n"
        for error in state["errors"]:
            summary += f"- {error}\n"

    summary += f"""

## 📁 Estructura del Proyecto

```
{state['project_name']}/
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
    ├── public/
    └── package.json
```

## 🚀 Próximos Pasos

1. Revisar código generado
2. Ejecutar tests localmente
3. Configurar CI/CD
4. Deploy a staging
5. QA manual
6. Deploy a producción

---
Generado por AI Dev Team
"""

    print(f"\n{'='*70}")
    print("📊 RESUMEN DEL PROYECTO")
    print("=" * 70)
    print(f"✅ User Stories: {len(state['user_stories'])}")
    print(f"✅ Tareas: {len(state['tasks'])}")
    print(f"✅ Backend: {total_backend_files} archivos")
    print(f"✅ Frontend: {total_frontend_files} archivos")
    print(
        f"✅ Tests: {total_test_files} archivos ({state['test_coverage']*100:.1f}% coverage)"
    )

    if deployment_ready:
        print(f"\n🎉 ¡Proyecto listo para deployment!")
    else:
        print(f"\n⚠️  Proyecto requiere revisión adicional")

    print("=" * 70)

    return {**state, "project_summary": summary, "deployment_ready": deployment_ready}


# ============ CREAR WORKFLOW ============


def create_dev_team_workflow() -> StateGraph:
    """
    Crea el workflow del equipo de desarrollo.

    Flujo secuencial:
    PM → SM → Backend → Frontend → QA → Review

    Backend y Frontend se ejecutan secuencialmente porque
    Frontend necesita saber los endpoints del Backend.
    """

    workflow = StateGraph(DevelopmentState)

    # Agregar nodos del equipo
    workflow.add_node("product_manager", product_manager_node)
    workflow.add_node("scrum_master", scrum_master_node)
    workflow.add_node("backend_dev", backend_developer_node)
    workflow.add_node("frontend_dev", frontend_developer_node)
    workflow.add_node("qa", qa_engineer_node)
    workflow.add_node("review", review_and_summary_node)

    # Definir el flujo
    workflow.set_entry_point("product_manager")

    # PM → SM
    workflow.add_conditional_edges(
        "product_manager",
        should_continue_after_pm,
        {"scrum_master": "scrum_master", "end": END},
    )

    # SM → Backend
    workflow.add_conditional_edges(
        "scrum_master",
        should_continue_after_scrum,
        {"backend_dev": "backend_dev", "end": END},
    )

    # Backend → Frontend
    workflow.add_conditional_edges(
        "backend_dev",
        should_continue_after_backend,
        {"frontend_dev": "frontend_dev", "end": END},
    )

    # Frontend → QA
    workflow.add_conditional_edges(
        "frontend_dev", should_continue_after_frontend, {"qa": "qa", "end": END}
    )

    # QA → Review
    workflow.add_conditional_edges(
        "qa", should_continue_after_qa, {"review": "review", "end": END}
    )

    # Review → END
    workflow.add_edge("review", END)

    return workflow


def compile_workflow():
    """Compila el workflow"""
    workflow = create_dev_team_workflow()
    app = workflow.compile()
    return app


# Diagrama del flujo
WORKFLOW_DIAGRAM = """
┌──────────────────────────────────────────────────────────────────┐
│                   AI DEV TEAM WORKFLOW                            │
└──────────────────────────────────────────────────────────────────┘

                           START
                             │
                             v
                    ┌─────────────────┐
                    │ Product Manager │
                    │  👔 User Stories │
                    └────────┬────────┘
                             │
                        [Backlog OK?]
                             │
                    Yes      │      No
                    ┌────────┴─────┐
                    │              │
                    v              v
            ┌─────────────┐       END
            │Scrum Master │
            │  🏃 Planning │
            └──────┬──────┘
                   │
             [Tasks OK?]
                   │
              Yes  │  No
              ┌────┴────┐
              │         │
              v         v
      ┌────────────────┐ END
      │Backend Developer│
      │  🔧 FastAPI    │
      └───────┬────────┘
              │
        [Backend OK?]
              │
         Yes  │  No
         ┌────┴────┐
         │         │
         v         v
   ┌─────────────────┐ END
   │Frontend Developer│
   │  🎨 React       │
   └────────┬────────┘
            │
      [Frontend OK?]
            │
       Yes  │  No
       ┌────┴────┐
       │         │
       v         v
   ┌─────────┐  END
   │   QA    │
   │  🧪Tests │
   └────┬────┘
        │
    [QA OK?]
        │
   Yes  │  No
   ┌────┴────┐
   │         │
   v         v
┌─────────┐ END
│ Review  │
│📋Summary│
└────┬────┘
     │
     v
    END

Características:
✨ Flujo secuencial coordinado
✨ Cada nodo usa Claude Agent SDK
✨ MCPs para filesystem access
✨ Validación en cada paso
✨ Resumen ejecutivo al final
"""


if __name__ == "__main__":
    print(WORKFLOW_DIAGRAM)
