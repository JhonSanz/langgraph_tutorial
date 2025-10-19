from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from graph.state import GraphState
from config import MAX_RETRIES, Routes, DEFAULT_LLM_MODEL, get_user_query, is_result_empty, has_error, DATA_SOURCES


def _determine_retry_route(state: GraphState, retry_count: int) -> dict:
    """
    Determine the retry route based on retry count and selected source.

    Args:
        state: Current graph state
        retry_count: Number of retry attempts made

    Returns:
        Dictionary with route to next node (expert or RAG)
    """
    if retry_count < MAX_RETRIES:
        # Determine which expert to retry based on selected_source
        selected_source = state.get("selected_source", "")

        # Check if source is in SQL databases
        sql_sources = DATA_SOURCES.get("sql", [])
        is_sql = any(source["name"] == selected_source for source in sql_sources)

        if is_sql:
            return {"route": Routes.EXPERT_SQL}
        else:
            return {"route": Routes.EXPERT_NOSQL}
    else:
        # Max retries reached, fallback to RAG
        return {"route": Routes.EXPERT_RAG}


def db_result_evaluator(state: GraphState):
    """
    Evaluates database query results and decides next action (retry, RAG fallback, or response).

    This node analyzes the results from database queries to determine if they adequately
    answer the user's question. It can trigger retries for failed queries (up to MAX_RETRIES),
    fallback to RAG for persistent failures, or proceed to generate the final response.

    Args:
        state (GraphState): Current graph state containing:
            - messages: Conversation history including tool results
            - retry_count: Number of retry attempts made
            - route: Current route information to determine expert type

    Returns:
        dict: Updated state with:
            - route: Next node ("expert_sql", "expert_nosql", "expert_rag",
                    "response_generator", or END)

    Decision logic:
        1. No tool results → Check for errors → RAG or END
        2. Empty/error results → Retry (if attempts left) or RAG
        3. LLM evaluation unsatisfactory → Retry or RAG
        4. Results satisfactory → Generate response
    """
    messages = state["messages"]
    retry_count = state.get("retry_count", 0)

    # Find the last tool message (database result)
    last_tool_msg = None
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'tool':
            last_tool_msg = msg
            break

    # If no tool message found, check if there's an error message
    if not last_tool_msg:
        # Check if the last message is an error from expert_sql/nosql
        last_msg = messages[-1] if messages else None
        if last_msg and isinstance(last_msg, SystemMessage) and "Error" in last_msg.content:
            # Database connection or config error, go to RAG as fallback
            return {"route": Routes.EXPERT_RAG}
        # No tool was called, go to end
        return {"route": END}

    tool_content = str(last_tool_msg.content).strip()

    # Check if results are clearly unsatisfactory
    if is_result_empty(tool_content) or has_error(tool_content):
        return _determine_retry_route(state, retry_count)

    # Results look good, use LLM to make final evaluation
    user_query = get_user_query(messages)
    user_question = user_query.content if user_query else "the user's question"

    eval_prompt = f"""You are evaluating database query results.

User's question: {user_question}

Database results: {tool_content}

Determine if these results adequately answer the user's question.
Respond with ONLY one word: "satisfactory" or "unsatisfactory".

If the results contain relevant data that could answer the question, say "satisfactory".
If the results are empty, irrelevant, or don't help answer the question, say "unsatisfactory".
"""

    llm = ChatOpenAI(model=DEFAULT_LLM_MODEL)
    eval_result = llm.invoke([HumanMessage(content=eval_prompt)])

    if "unsatisfactory" in eval_result.content.lower():
        return _determine_retry_route(state, retry_count)

    # Results are satisfactory, generate final response
    return {"route": Routes.RESPONSE}
