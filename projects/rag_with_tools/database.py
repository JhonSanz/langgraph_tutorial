# import sqlite3

# conn = sqlite3.connect("finanzas.db")
# cursor = conn.cursor()


# cursor.execute(
#     """
# CREATE TABLE IF NOT EXISTS ventas (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     producto INTEGER NOT NULL,
#     cantidad INTEGER NOT NULL,
#     fecha DATE NOT NULL,
#     FOREIGN KEY (producto) REFERENCES producto (id)
# );
# """
# )

# cursor.execute(
#     """
# CREATE TABLE IF NOT EXISTS producto (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     nombre TEXT NOT NULL,
#     proveedor INTEGER NOT NULL,
#     precio REAL NOT NULL,
#     FOREIGN KEY (proveedor) REFERENCES proveedor (id)
# );
# """
# )
# cursor.execute(
# """
# CREATE TABLE IF NOT EXISTS proveedor (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     nombre TEXT NOT NULL,
#     contacto TEXT NOT NULL
# )
# """
# )
# conn.commit()


# # ---


# proveedores = [
#     ("Proveedor A", "contacto_a@example.com"),
#     ("Proveedor B", "contacto_b@example.com"),
#     ("Proveedor C", "contacto_c@example.com"),
# ]
# cursor.executemany(
#     """
# INSERT INTO proveedor (nombre, contacto)
# VALUES (?, ?)
# """,
#     proveedores,
# )
# conn.commit()


# productos = [
#     ("Producto A", 1, 10.0),
#     ("Producto B", 2, 20.0),
#     ("Producto C", 1, 30.0),
#     ("Producto D", 3, 40.0),
# ]
# cursor.executemany(
#     """
# INSERT INTO producto (nombre, proveedor, precio)
# VALUES (?, ?, ?)
# """,
#     productos,
# )
# conn.commit()


# ventas = [
#     (1, 5, "2025-01-01"),
#     (2, 10, "2025-01-02"),
#     (3, 15, "2025-01-03"),
#     (4, 20, "2025-01-04"),
#     (1, 3, "2025-01-05"),
#     (2, 8, "2025-01-06"),
#     (3, 12, "2025-01-07"),
#     (4, 18, "2025-01-08")
# ]
# cursor.executemany(
#     """
# INSERT INTO ventas (producto, cantidad, fecha)
# VALUES (?, ?, ?)
# """,
#     ventas,
# )

# conn.commit()


# # --- PRUEBAS CON QUERIES
# import sqlite3

# query = """
# SELECT p.nombre, SUM(v.cantidad) as total_vendido
# FROM ventas as v
# JOIN producto as p ON v.producto = p.id
# GROUP BY p.id
# """

# query = """
# SELECT SUM(v.cantidad)
# FROM ventas as v

# """

# lowered = query.lower()
# blocked = {"update", "delete", "drop", "insert", "alter"}
# if any(word in lowered for word in blocked):
#     print("❌ Operación SQL no permitida.")

# conn = sqlite3.connect("finanzas.db")
# conn.row_factory = sqlite3.Row
# cursor = conn.cursor()

# try:
#     cursor.execute(query)
#     rows = [dict(row) for row in cursor.fetchall()]
#     if not rows:
#         print("✅ Consulta ejecutada correctamente, sin resultados.")
#     print(str(rows))
# except sqlite3.Error as e:
#     print(f"❌ Error al ejecutar la query: {e}")
# finally:
#     cursor.close()
#     conn.close()