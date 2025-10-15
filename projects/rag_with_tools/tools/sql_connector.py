"""
Generalized SQL database connector supporting SQLite, PostgreSQL, and MySQL.
Uses SQLAlchemy for database abstraction.
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Any, Optional
import os


class SQLConnector:
    """
    Unified SQL database connector that works with SQLite, PostgreSQL, and MySQL.
    """

    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize the SQL connector with database configuration.

        Args:
            db_config: Dictionary containing database configuration with keys:
                - type: "sqlite", "postgres", or "mysql"
                - host: database host (not needed for sqlite)
                - port: database port (not needed for sqlite)
                - database: database name
                - username: database username (not needed for sqlite)
                - password: database password (not needed for sqlite)
                - path: file path for sqlite
        """
        self.db_type = db_config.get("type", "").lower()
        self.engine = self._create_engine(db_config)

    def _create_engine(self, config: Dict[str, Any]):
        """Create SQLAlchemy engine based on database type."""
        db_type = config.get("type", "").lower()

        if db_type == "sqlite":
            # SQLite connection
            db_path = config.get("path", "database.db")
            connection_string = f"sqlite:///{db_path}"

        elif db_type == "postgres":
            # PostgreSQL connection
            username = config.get("username", "myuser")
            password = config.get("password", "mypassword")
            host = config.get("host", "localhost")
            port = config.get("port", 5432)
            database = config.get("database", "mydatabase")
            connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

        elif db_type == "mysql":
            # MySQL connection
            username = config.get("username", "myuser")
            password = config.get("password", "mypassword")
            host = config.get("host", "localhost")
            port = config.get("port", 3306)
            database = config.get("database", "mydatabase")
            connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        return create_engine(connection_string, pool_pre_ping=True)

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as list of dictionaries.

        Args:
            query: SQL query string

        Returns:
            List of dictionaries representing rows
        """
        # Security check: block dangerous operations
        lowered = query.lower().strip()
        blocked_keywords = {"update", "delete", "drop", "insert", "alter", "truncate", "create"}

        if any(keyword in lowered for keyword in blocked_keywords):
            return [{"error": "❌ Operación SQL no permitida. Solo se permiten consultas SELECT."}]

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))

                # Check if query returns results (SELECT)
                if result.returns_rows:
                    rows = [dict(row._mapping) for row in result]
                    if not rows:
                        return [{"message": "✅ Consulta ejecutada correctamente, sin resultados."}]
                    return rows
                else:
                    return [{"message": "✅ Operación ejecutada correctamente."}]

        except SQLAlchemyError as e:
            return [{"error": f"❌ Error al ejecutar la query: {str(e)}"}]
        except Exception as e:
            return [{"error": f"❌ Error inesperado: {str(e)}"}]

    def get_schema(self) -> str:
        """
        Get database schema as formatted text.

        Returns:
            String representation of database schema
        """
        try:
            inspector = inspect(self.engine)
            schema_text = ""

            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)

                # Format columns
                col_definitions = []
                for col in columns:
                    col_type = str(col['type'])
                    col_definitions.append(f"{col['name']} {col_type}")

                # Format foreign keys
                fk_definitions = []
                for fk in foreign_keys:
                    constrained_cols = ', '.join(fk['constrained_columns'])
                    referred_table = fk['referred_table']
                    referred_cols = ', '.join(fk['referred_columns'])
                    fk_definitions.append(f"{constrained_cols}→{referred_table}.{referred_cols}")

                # Build table line
                table_line = f"Table {table_name}({', '.join(col_definitions)}"
                if fk_definitions:
                    table_line += f"; FK: {', '.join(fk_definitions)}"
                table_line += ")"

                schema_text += table_line + "\n"

            return schema_text.strip()

        except SQLAlchemyError as e:
            return f"❌ Error al obtener el schema: {str(e)}"
        except Exception as e:
            return f"❌ Error inesperado: {str(e)}"

    def test_connection(self) -> bool:
        """
        Test if the database connection is working.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()


def get_sql_connector_from_datasource(datasource_name: str, datasources: Dict) -> Optional[SQLConnector]:
    """
    Create a SQLConnector instance from datasources.yaml configuration.

    Args:
        datasource_name: Name of the datasource from datasources.yaml
        datasources: Loaded datasources configuration dictionary

    Returns:
        SQLConnector instance or None if not found
    """
    # Search in SQL datasources
    for source in datasources.get("sql", []):
        if source["name"] == datasource_name:
            db_type = source["type"]

            config = {"type": db_type}

            if db_type == "sqlite":
                # For SQLite, use a local path
                config["path"] = source.get("path", f"{datasource_name}.db")
            elif db_type == "postgres":
                config.update({
                    "host": source.get("host", "localhost"),
                    "port": source.get("port", 5432),
                    "database": source.get("database", "mydatabase"),
                    "username": source.get("username", "myuser"),
                    "password": source.get("password", "mypassword"),
                })
            elif db_type == "mysql":
                config.update({
                    "host": source.get("host", "localhost"),
                    "port": source.get("port", 3306),
                    "database": source.get("database", "mydatabase"),
                    "username": source.get("username", "myuser"),
                    "password": source.get("password", "mypassword"),
                })

            return SQLConnector(config)

    return None
