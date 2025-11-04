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

from graph.state import GraphState
from graph.nodes.product_manager import product_manager_node_async
# from src.nodes.scrum_master import scrum_master_node
# from src.nodes.backend_developer import backend_developer_node
# from src.nodes.frontend_developer import frontend_developer_node
# from src.nodes.qa_engineer import qa_engineer_node



def create_dev_team_workflow() -> StateGraph:
    """
    Crea el workflow del equipo de desarrollo.

    Flujo secuencial:
    PM → SM → Backend → Frontend → QA → Review

    Backend y Frontend se ejecutan secuencialmente porque
    Frontend necesita saber los endpoints del Backend.
    """

    workflow = StateGraph(GraphState)

    # Agregar nodos del equipo
    workflow.add_node("product_manager", product_manager_node_async)


    workflow.set_entry_point("product_manager")
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
