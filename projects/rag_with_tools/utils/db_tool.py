from langchain_core.tools import tool
import sqlite3


@tool
def db_tool(query: str) -> str:
    """
    Queries products database given a SQL query as string

    Parameters:
        - query: str
    """
    print("\n" * 5, query, "\n" * 5)

    lowered = query.lower()
    blocked = {"update", "delete", "drop", "insert", "alter"}
    if any(word in lowered for word in blocked):
        return "❌ Operación SQL no permitida."

    conn = sqlite3.connect("finanzas.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        if not rows:
            return "✅ Consulta ejecutada correctamente, sin resultados."
        return str(rows)
    except sqlite3.Error as e:
        return f"❌ Error al ejecutar la query: {e}"
    finally:
        cursor.close()
        conn.close()
