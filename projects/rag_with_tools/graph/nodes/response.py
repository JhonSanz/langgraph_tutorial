from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from graph.state import GraphState


def response_generator(state: GraphState):
    """
    Generates a comprehensive final response to the user based on all collected information.
    This node synthesizes data from database queries or RAG results into a clear, complete answer.
    """
    messages = state["messages"]

    # Find the user's original question
    user_query = next(
        (msg for msg in messages if isinstance(msg, HumanMessage)), None
    )
    user_question = user_query.content if user_query else "your question"

    # Collect all relevant information from the conversation
    db_results = []
    rag_results = []
    errors = []

    for msg in messages:
        # Collect database tool results
        if hasattr(msg, 'type') and msg.type == 'tool':
            tool_name = getattr(msg, 'name', 'unknown')
            if 'sql' in tool_name.lower() or 'mongo' in tool_name.lower():
                db_results.append(str(msg.content))
            elif 'rag' in tool_name.lower():
                rag_results.append(str(msg.content))
        # Collect error messages
        elif isinstance(msg, SystemMessage) and "Error" in msg.content:
            errors.append(msg.content)

    # Determine which sources were used
    sources_used = []
    if db_results:
        source_name = state.get("selected_source", "database")
        sources_used.append(f"Database: {source_name}")
    if rag_results:
        sources_used.append("Knowledge base (RAG)")

    # Build context for the LLM
    context_parts = []

    if db_results:
        context_parts.append(f"Database Query Results:\n{chr(10).join(db_results)}")

    if rag_results:
        context_parts.append(f"Knowledge Base Information:\n{chr(10).join(rag_results)}")

    if errors:
        context_parts.append(f"Encountered Issues:\n{chr(10).join(errors)}")

    context = "\n\n".join(context_parts)

    # Generate the final response
    instruction = f"""You are a helpful assistant providing a final answer to the user.

User's Question: {user_question}

Available Information:
{context}

Sources Used: {', '.join(sources_used) if sources_used else 'None'}

Your task:
1. Synthesize all the information provided above
2. Answer the user's question clearly and completely
3. If data came from databases, present it in a readable format (tables, lists, summaries)
4. If the information is insufficient, acknowledge what's missing
5. Be professional and concise
6. At the end, briefly mention which sources were consulted

Provide a complete, well-formatted response."""

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    final_response = llm.invoke([
        SystemMessage(content=instruction),
        HumanMessage(content=user_question)
    ])

    return {"messages": [final_response], "route": END}
