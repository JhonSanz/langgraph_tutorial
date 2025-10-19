from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import GraphState, RouteDecision
from config import DATA_SOURCES, DEFAULT_LLM_MODEL, Routes


def data_router(state: GraphState):
    """
    Routes user queries to the appropriate data source based on content analysis.

    Analyzes the user's query using an LLM to determine which database
    (SQL or MongoDB) is most appropriate for answering the question. The LLM
    evaluates the query against all available data sources and selects the
    best match based on descriptions and database capabilities.

    Args:
        state (GraphState): Current graph state containing:
            - messages: Conversation history with user query

    Returns:
        dict: Updated state with:
            - route: Expert to use ("expert_sql" or "expert_nosql")
            - selected_source: Name of the selected data source

    Raises:
        ValueError: If data sources catalog or user query is empty
        RuntimeError: If LLM fails to process the query or returns invalid route
    """
    user_query = next(
        (m for m in state["messages"] if isinstance(m, HumanMessage)), None
    )
    query_text = user_query.content if user_query else ""

    catalog_str = ""
    for engine, sources in DATA_SOURCES.items():
        for s in sources:
            catalog_str += (
                f"- {s['name']} ({engine}): {s.get('description', 'No description')}\n"
            )

    if not catalog_str or not user_query:
        raise ValueError("Data sources catalog or user query is empty.")

    instruction = f"""
You are a routing agent for a data query system. Analyze the user's query and select the most appropriate data source.

User query: "{query_text}"

Available sources:
{catalog_str}

ROUTING RULES:
- If the best source uses SQL database → return route: "{Routes.EXPERT_SQL}"
- If the best source uses MongoDB/NoSQL database → return route: "{Routes.EXPERT_NOSQL}"

You MUST respond with valid JSON containing:
- "route": the expert type ({Routes.EXPERT_SQL} or {Routes.EXPERT_NOSQL})
- "source": the exact name of the data source

Example response:
{{"route": "{Routes.EXPERT_SQL}", "source": "users_db"}}
"""

    try:
        llm = ChatOpenAI(
            model=DEFAULT_LLM_MODEL, model_kwargs={"response_format": {"type": "json_object"}}
        )
        structured_llm = llm.with_structured_output(RouteDecision)
        result = structured_llm.invoke(
            [SystemMessage(content=instruction), HumanMessage(content=query_text)]
        )

        return {"route": result.route, "selected_source": result.source}

    except Exception as e:
        # Re-lanzar con contexto adicional para debugging
        raise RuntimeError(
            f"Router failed to process query: '{query_text[:100]}...'. "
            f"Error: {str(e)}"
        ) from e
