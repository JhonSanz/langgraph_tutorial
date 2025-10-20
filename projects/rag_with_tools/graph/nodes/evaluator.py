from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from graph.state import GraphState
from config import DEFAULT_LLM_MODEL, get_user_query, is_result_empty, has_error, EvaluationResults


def db_result_evaluator(state: GraphState):
    """
    Evaluates database query results to determine their quality.

    This node analyzes the results from database queries to determine if they adequately
    answer the user's question. It does NOT make routing decisions - it only evaluates
    and labels the results. The graph's routing function makes decisions based on this evaluation.

    Args:
        state (GraphState): Current graph state containing:
            - messages: Conversation history including tool results

    Returns:
        dict: Updated state with:
            - evaluation_result: One of:
                - "no_results": No tool message found
                - "error": Tool message found but contains error
                - "unsatisfactory": Results don't adequately answer the question (LLM evaluated)
                - "satisfactory": Results adequately answer the question

    Evaluation criteria:
        1. Check if tool results exist
        2. Check if results are empty or contain errors
        3. Use LLM to evaluate if results answer the user's question
    """
    messages = state["messages"]

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
            # Database connection or config error
            return {"evaluation_result": EvaluationResults.ERROR}
        # No tool was called
        return {"evaluation_result": EvaluationResults.NO_RESULTS}

    tool_content = str(last_tool_msg.content).strip()

    # Check if results are clearly unsatisfactory (empty or error)
    if is_result_empty(tool_content) or has_error(tool_content):
        return {"evaluation_result": EvaluationResults.ERROR}

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
        # Increment retry_count since results are unsatisfactory and may need retry
        retry_count = state.get("retry_count", 0)
        return {
            "evaluation_result": EvaluationResults.UNSATISFACTORY,
            "retry_count": retry_count + 1
        }

    # Results are satisfactory
    return {"evaluation_result": EvaluationResults.SATISFACTORY}
