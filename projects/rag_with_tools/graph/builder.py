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
from config import Routes, MAX_RETRIES, DATA_SOURCES, EvaluationResults


def route_data_router(state: GraphState) -> str:
    """Route from data_router to the appropriate expert."""
    return state.get("route", END)


def route_expert_sql(state: GraphState) -> str:
    """Route from expert_sql based on whether tool calls were made."""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return Routes.SQL_TOOLS
    else:
        return Routes.EVALUATOR


def route_expert_nosql(state: GraphState) -> str:
    """Route from expert_nosql based on whether tool calls were made."""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        return Routes.NOSQL_TOOLS
    else:
        return Routes.EVALUATOR


def route_evaluator(state: GraphState) -> str:
    """
    Route from evaluator based on evaluation results and retry count.

    Decision logic:
        - NO_RESULTS → END
        - ERROR or UNSATISFACTORY → Retry (if attempts left) or RAG
        - SATISFACTORY → Generate response

    Args:
        state: Current graph state with evaluation_result and retry_count

    Returns:
        Route constant for next node
    """
    evaluation = state.get("evaluation_result", "")
    retry_count = state.get("retry_count", 0)

    # No results found, end gracefully
    if evaluation == EvaluationResults.NO_RESULTS:
        return "__end__"

    # Results are unsatisfactory or have errors
    if evaluation in [EvaluationResults.ERROR, EvaluationResults.UNSATISFACTORY]:
        # Check if we can retry
        if retry_count < MAX_RETRIES:
            # Determine which expert to retry based on selected_source
            selected_source = state.get("selected_source", "")
            sql_sources = DATA_SOURCES.get("sql", [])
            is_sql = any(source["name"] == selected_source for source in sql_sources)
            return Routes.EXPERT_SQL if is_sql else Routes.EXPERT_NOSQL
        else:
            # Max retries reached, fallback to RAG
            return Routes.EXPERT_RAG

    # Results are satisfactory, generate response
    return Routes.RESPONSE


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
        route_data_router,
        {
            Routes.EXPERT_SQL: "expert_sql",
            Routes.EXPERT_NOSQL: "expert_nosql",
        }
    )

    # expert_sql can either call tools or go to evaluator
    builder.add_conditional_edges(
        "expert_sql",
        route_expert_sql,
        {
            Routes.SQL_TOOLS: "sql_db_tools",
            Routes.EVALUATOR: "db_result_evaluator",
        }
    )

    # expert_nosql can either call tools or go to evaluator
    builder.add_conditional_edges(
        "expert_nosql",
        route_expert_nosql,
        {
            Routes.NOSQL_TOOLS: "nosql_db_tools",
            Routes.EVALUATOR: "db_result_evaluator",
        }
    )

    # After tools execute, go to evaluator
    builder.add_edge("sql_db_tools", "db_result_evaluator")
    builder.add_edge("nosql_db_tools", "db_result_evaluator")

    # Evaluator decides: retry (go back to expert), fallback to RAG, or go to response generator
    builder.add_conditional_edges(
        "db_result_evaluator",
        route_evaluator,
        {
            Routes.EXPERT_SQL: "expert_sql",
            Routes.EXPERT_NOSQL: "expert_nosql",
            Routes.EXPERT_RAG: "expert_rag",
            Routes.RESPONSE: "response_generator",
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
