from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from graph.state import GraphState
from config import MAX_RETRIES


def db_result_evaluator(state: GraphState):
    """Evaluates database query results and decides whether to retry, go to RAG, or end."""
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
        # Check if the last message is an error from expert_sql
        last_msg = messages[-1] if messages else None
        if last_msg and isinstance(last_msg, SystemMessage) and "Error" in last_msg.content:
            # Database connection or config error, go to RAG as fallback
            return {"route": "expert_rag"}
        # No tool was called, go to end
        return {"route": END}

    tool_content = str(last_tool_msg.content).strip()

    # Criteria for unsatisfactory results
    is_empty = (
        not tool_content
        or tool_content == "[]"
        or tool_content == "{}"
        or tool_content == "()"
        or tool_content.lower() == "none"
    )
    is_error = "error" in tool_content.lower()
    is_no_results = (
        "no results" in tool_content.lower()
        or "empty" in tool_content.lower()
        or "no rows" in tool_content.lower()
    )

    # If results are clearly unsatisfactory
    if is_empty or is_error or is_no_results:
        # Check if we can retry
        if retry_count < MAX_RETRIES:
            # Retry: go back to the appropriate expert based on selected_source
            source_type = state.get("route", "expert_sql")
            # Extract the expert type from route (could be expert_sql or expert_nosql)
            if "nosql" in source_type:
                return {"route": "expert_nosql"}
            else:
                return {"route": "expert_sql"}
        else:
            # Max retries reached, fallback to RAG
            return {"route": "expert_rag"}

    # Results look good, use LLM to make final evaluation
    user_query = next(
        (m for m in messages if isinstance(m, HumanMessage)), None
    )
    user_question = user_query.content if user_query else "the user's question"

    eval_prompt = f"""You are evaluating database query results.

User's question: {user_question}

Database results: {tool_content}

Determine if these results adequately answer the user's question.
Respond with ONLY one word: "satisfactory" or "unsatisfactory".

If the results contain relevant data that could answer the question, say "satisfactory".
If the results are empty, irrelevant, or don't help answer the question, say "unsatisfactory".
"""

    llm = ChatOpenAI(model="gpt-4o-mini")
    eval_result = llm.invoke([HumanMessage(content=eval_prompt)])

    if "unsatisfactory" in eval_result.content.lower():
        # Check if we can retry
        if retry_count < MAX_RETRIES:
            # Retry
            source_type = state.get("route", "expert_sql")
            if "nosql" in source_type:
                return {"route": "expert_nosql"}
            else:
                return {"route": "expert_sql"}
        else:
            # Max retries reached, fallback to RAG
            return {"route": "expert_rag"}

    # Results are satisfactory, generate final response
    return {"route": "response_generator"}
