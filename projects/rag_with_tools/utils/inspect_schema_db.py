import sqlite3


def get_schema_from_sqlite(db_path="finanzas.db"):
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