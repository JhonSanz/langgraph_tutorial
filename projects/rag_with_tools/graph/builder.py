from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes import (
    data_router,
    expert_sql,
    expert_nosql,
    db_result_evaluator,
    expert_rag,
    response_generator,
)
from tools.sql_tool import sql_db_tool
from tools.mongo_tool import mongo_tool
from tools.rag_tool import rag_tool


def build_graph():
    """Constructs and returns the compiled StateGraph."""
    # Define tool nodes
    sql_db_tools = [sql_db_tool]
    nosql_db_tools = [mongo_tool]
    rag_tools = [rag_tool]

    # Initialize graph builder
    builder = StateGraph(GraphState)

    # Add nodes
    builder.add_node("data_router", data_router)
    builder.add_node("expert_sql", expert_sql)
    builder.add_node("expert_nosql", expert_nosql)
    builder.add_node("expert_rag", expert_rag)
    builder.add_node("db_result_evaluator", db_result_evaluator)
    builder.add_node("response_generator", response_generator)

    # Add tool nodes
    builder.add_node("sql_db_tools", ToolNode(sql_db_tools))
    builder.add_node("nosql_db_tools", ToolNode(nosql_db_tools))
    builder.add_node("rag_tools", ToolNode(rag_tools))

    # Add edges
    # Entry point: data_router decides which expert to use
    builder.add_conditional_edges(
        "data_router",
        lambda state: state.get("route", END),
        {
            "expert_sql": "expert_sql",
            "expert_nosql": "expert_nosql",
        }
    )

    # expert_sql can either call tools or go to evaluator
    builder.add_conditional_edges(
        "expert_sql",
        lambda state: state.get("route", END),
        {
            "sql_db_tools": "sql_db_tools",
            "db_result_evaluator": "db_result_evaluator",
        }
    )

    # expert_nosql can either call tools or go to evaluator
    builder.add_conditional_edges(
        "expert_nosql",
        lambda state: state.get("route", END),
        {
            "nosql_db_tools": "nosql_db_tools",
            "db_result_evaluator": "db_result_evaluator",
        }
    )

    # After tools execute, go to evaluator
    builder.add_edge("sql_db_tools", "db_result_evaluator")
    builder.add_edge("nosql_db_tools", "db_result_evaluator")

    # Evaluator decides: retry (go back to expert), fallback to RAG, or go to response generator
    builder.add_conditional_edges(
        "db_result_evaluator",
        lambda state: state.get("route", END),
        {
            "expert_sql": "expert_sql",
            "expert_nosql": "expert_nosql",
            "expert_rag": "expert_rag",
            "response_generator": "response_generator",
            "__end__": END,
        }
    )

    # expert_rag calls RAG tools
    builder.add_conditional_edges(
        "expert_rag",
        tools_condition,
        {"tools": "rag_tools", "__end__": END},
    )

    # After RAG tools, go to response generator to synthesize final answer
    builder.add_edge("rag_tools", "response_generator")

    # response_generator always ends the graph
    builder.add_edge("response_generator", END)

    # Set entry point
    builder.set_entry_point("data_router")

    # Compile and return the graph
    return builder.compile()
