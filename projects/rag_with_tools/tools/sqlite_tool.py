from langchain_core.tools import tool
import sqlite3
import os


@tool
def db_tool(query: str) -> str:
    """
    Queries products database given a SQL query as string

    Parameters:
        - query: str
    """
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


def get_schema_from_sqlite(db_path="finanzas.db"):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "finanzas.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Obtener todas las tablas, excluyendo sqlite_sequence
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name!='sqlite_sequence';"
    )
    tables = [row[0] for row in cursor.fetchall()]

    schema_text = ""
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        cols = [f"{col[1]} {col[2]}" for col in cursor.fetchall()]

        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fks = [f"{fk[3]}→{fk[2]}.{fk[4]}" for fk in cursor.fetchall()]

        table_line = f"{table}({', '.join(cols)}"
        if fks:
            table_line += f"; FK: {', '.join(fks)}"
        table_line += ")"

        schema_text += table_line + "\n"

    conn.close()
    return schema_text
