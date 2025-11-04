from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes.product_manager import product_manager_node_async


def build_graph() -> StateGraph:
    """
    Crea el workflow del equipo de desarrollo.

    Flujo secuencial:
    PM → SM → Backend → Frontend → QA → Review

    Backend y Frontend se ejecutan secuencialmente porque
    Frontend necesita saber los endpoints del Backend.
    """

    workflow = StateGraph(GraphState)

    workflow.add_node("product_manager", product_manager_node_async)

    workflow.set_entry_point("product_manager")
    workflow.add_edge("review", END)

    graph = workflow.compile()
    return graph


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
