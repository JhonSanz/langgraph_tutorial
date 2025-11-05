"""
Backend Subgraph - Define el flujo de trabajo para construir el backend.

Flujo:
1. backend_setup → Estructura base
2. backend_models → Modelos SQLAlchemy
3. backend_schemas → Schemas Pydantic
4. backend_crud → CRUD operations
5. backend_api → Endpoints FastAPI
6. backend_tests → Tests con pytest
"""

from langgraph.graph import StateGraph, END
from graph.state import GraphState
from .backend_setup import backend_setup_node_async
from .backend_models import backend_models_node_async
from .backend_schemas import backend_schemas_node_async
from .backend_crud import backend_crud_node_async
from .backend_api import backend_api_node_async
from .backend_tests import backend_tests_node_async


def create_backend_subgraph():
    """
    Crea el subgrafo para desarrollo backend.

    El subgrafo divide el trabajo en 6 pasos secuenciales para evitar
    GraphRecursionError al generar muchos archivos.

    Returns:
        Compiled subgraph
    """

    # Crear el subgrafo
    subgraph = StateGraph(GraphState)

    # Agregar nodos
    subgraph.add_node("backend_setup", backend_setup_node_async)
    subgraph.add_node("backend_models", backend_models_node_async)
    subgraph.add_node("backend_schemas", backend_schemas_node_async)
    subgraph.add_node("backend_crud", backend_crud_node_async)
    subgraph.add_node("backend_api", backend_api_node_async)
    subgraph.add_node("backend_tests", backend_tests_node_async)

    # Definir flujo secuencial
    subgraph.set_entry_point("backend_setup")

    subgraph.add_edge("backend_setup", "backend_models")
    subgraph.add_edge("backend_models", "backend_schemas")
    subgraph.add_edge("backend_schemas", "backend_crud")
    subgraph.add_edge("backend_crud", "backend_api")
    subgraph.add_edge("backend_api", "backend_tests")
    subgraph.add_edge("backend_tests", END)

    return subgraph.compile()
