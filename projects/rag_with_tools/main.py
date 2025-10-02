from langgraph.prebuilt import tools_condition, ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from utils.inspect_schema_db import get_schema_from_sqlite
from utils.db_tool import db_tool
from utils.rag_tool import rag_tool
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

load_dotenv()


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    route: str

db_tools = [db_tool]
rag_tools = [rag_tool]


def expert_database(state: GraphState):
    db_schema = get_schema_from_sqlite()
    instruction  = f"""
    You are an expert tasked to query a database given the following schema. You HAVE TO generate the query, based on this:

    {db_schema}

    IMPORTANT:
    - If you don't find useful data or it's empty, output the text 'expert_rag' (to delegate).
    - If you generate a valid SQL query, call the tool.
    - If you have the answer, output it directly and end (route 'done').
    """
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(db_tools)
    ai_msg = llm_with_tools.invoke([sys_msg] + state["messages"])

    response = {
        "messages": [ai_msg] 
    }
    if "expert_rag" in ai_msg.content.lower():
        response["route"] = "expert_rag"
    elif ai_msg.tool_calls:
        response["route"] = "database_tools"
    else:
        response["route"] = END
    return response

def expert_rag(state: GraphState):
    user_query = next((msg for msg in state["messages"] if isinstance(msg, HumanMessage)), None)
    if user_query is None:
        clean_history = state["messages"] 
    else:
        clean_history = [user_query]

    instruction = "You are a helpful assistant tasked to query the chromaDB database to find the answer"
    sys_msg = SystemMessage(content=instruction)
    llm_with_tools = ChatOpenAI(model="gpt-4o-mini").bind_tools(rag_tools)
    return {"messages": [llm_with_tools.invoke([sys_msg] + clean_history)]}


def database_condition(state: GraphState):
    route = state.get("route", END)
    return route


builder = StateGraph(GraphState)

builder.add_node("expert_database", expert_database)
builder.add_node("expert_rag", expert_rag)

builder.add_node("database_tools", ToolNode(db_tools))
builder.add_node("rag_tools", ToolNode(rag_tools))


builder.add_conditional_edges(
    "expert_database",
    database_condition,
)
builder.add_conditional_edges(
    "expert_rag",
    tools_condition,
    {"tools": "rag_tools", "__end__": END},
)

builder.add_edge("database_tools", "expert_database")
builder.add_edge("rag_tools", "expert_rag")

builder.set_entry_point("expert_database")

graph = builder.compile()


# mermaid_code = graph.get_graph().draw_mermaid()
# print(mermaid_code)


result = graph.invoke(
    {"messages": [HumanMessage(content="How much we made with product A sales?")]}
)

print("\n=== Resultados finales ===")
for msg in result["messages"]:
    msg.pretty_print()



"""
MEJORAS PROPUESTAS:


https://chatgpt.com/c/68de6d03-67f0-8320-90a4-6ee71b3fb433


# utils/db_tool.py
import sqlite3
from typing import Dict, Any

def db_tool(query: str) -> Dict[str, Any]:
    conn = sqlite3.connect("mi_db.sqlite")
    cur = conn.cursor()
    try:
        cur.execute(query)
    except Exception as e:
        conn.close()
        return {"status": "error", "error": str(e), "query": query}
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description] if cur.description else []
    conn.close()
    if not rows:
        return {"status": "no_rows", "rows": [], "columns": cols, "query": query}
    return {"status": "ok", "rows": [dict(zip(cols, r)) for r in rows], "columns": cols, "query": query}

    

from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from typing_extensions import Annotated
from typing import TypedDict, List, Dict, Any
from utils.db_tool import db_tool
from langgraph.graph import END
from utils.inspect_schema_db import get_schema_from_sqlite
import re

class GraphState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], ...]
    route: str
    executed_queries: List[str]
    node_attempts: Dict[str, int]
    total_hops: int

MAX_HOPS = 12
MAX_DB_ATTEMPTS = 2

def find_sql_in_messages(messages: List[AnyMessage]) -> str | None:
    # heurística simple: buscar la última cadena que contenga SELECT
    for msg in reversed(messages):
        if getattr(msg, "content", None) and isinstance(msg.content, str):
            text = msg.content.strip()
            if re.search(r'\bselect\b', text, re.IGNORECASE):
                return text
    return None

def database_tools_executor(state: GraphState):
    state.setdefault("total_hops", 0)
    state["total_hops"] += 1
    if state["total_hops"] > MAX_HOPS:
        return {"messages": state["messages"] + [HumanMessage(content="Máximo de pasos alcanzado, respondiendo con lo mejor que tengo.")], "route": END}

    sql = find_sql_in_messages(state["messages"])
    if not sql:
        # No hay SQL detectada: volvemos al planner para que genere la query
        return {"messages": state["messages"], "route": "expert_database"}

    # fingerprint simple: normalize whitespace
    fingerprint = " ".join(sql.lower().split())
    executed = state.setdefault("executed_queries", [])
    if fingerprint in executed:
        # ya intentamos la misma query -> escalar a RAG
        return {"messages": state["messages"] + [HumanMessage(content="query_already_tried")], "route": "expert_rag"}

    result = db_tool(sql)
    # marcaremos la query como intentada si devuelve no_rows o error
    if result.get("status") in ("no_rows", "error"):
        executed.append(fingerprint)
        attempts = state.setdefault("node_attempts", {})
        attempts["database_tools"] = attempts.get("database_tools", 0) + 1
        if attempts["database_tools"] >= MAX_DB_ATTEMPTS:
            # después de X intentos, delegamos al RAG
            return {"messages": state["messages"] + [HumanMessage(content=f"DB empty or error: {result.get('status')}. Escalando a RAG.")], "route": "expert_rag"}
        else:
            # permitimos que el LLM reintente (regresamos al planner)
            return {"messages": state["messages"] + [HumanMessage(content=f"DB returned {result.get('status')}, ask to try another query.")], "route": "expert_database"}

    # si hay resultados, formateamos respuesta y terminamos
    rows = result["rows"]
    # formatea tabla simple (puedes mejorar)
    cols = result["columns"]
    lines = ["\t".join(cols)]
    for r in rows:
        lines.append("\t".join(str(r[c]) for c in cols))
    answer = "\n".join(lines)
    return {"messages": state["messages"] + [HumanMessage(content=answer)], "route": END}

builder.add_node("database_tools", database_tools_executor)  # reemplaza ToolNode(db_tools)

"""