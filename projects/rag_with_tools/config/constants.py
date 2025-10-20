"""Constants for graph routing and node names."""


class Routes:
    """Node route constants to avoid magic strings and typos."""

    # Tool nodes
    SQL_TOOLS = "sql_db_tools"
    NOSQL_TOOLS = "nosql_db_tools"
    RAG_TOOLS = "rag_tools"

    # Expert nodes
    EXPERT_SQL = "expert_sql"
    EXPERT_NOSQL = "expert_nosql"
    EXPERT_RAG = "expert_rag"

    # Processing nodes
    EVALUATOR = "db_result_evaluator"
    RESPONSE = "response_generator"
    ROUTER = "data_router"


class EvaluationResults:
    """Evaluation result constants for db_result_evaluator node."""

    NO_RESULTS = "no_results"
    ERROR = "error"
    UNSATISFACTORY = "unsatisfactory"
    SATISFACTORY = "satisfactory"
