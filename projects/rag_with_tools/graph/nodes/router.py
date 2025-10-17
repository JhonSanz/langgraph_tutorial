from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import GraphState, RouteDecision
from config import DATA_SOURCES


def data_router(state: GraphState):
    """Routes user queries to the appropriate data source (SQL or NoSQL)."""
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
- If the best source uses SQL database → return route: "expert_sql"
- If the best source uses MongoDB/NoSQL database → return route: "expert_nosql"

You MUST respond with valid JSON containing:
- "route": the expert type (expert_sql or expert_nosql)
- "source": the exact name of the data source

Example response:
{{"route": "expert_sql", "source": "users_db"}}
"""

    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini", model_kwargs={"response_format": {"type": "json_object"}}
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
