from langchain_core.tools import tool
from pymongo import MongoClient
from bson import json_util
import json


@tool
def mongo_tool(database: str, collection: str, query: str) -> str:
    """
    Queries MongoDB database given a collection and a query as JSON string

    Parameters:
        - database: str - Name of the database
        - collection: str - Name of the collection
        - query: str - MongoDB query as JSON string (e.g., '{"field": "value"}')
    """
    # Block dangerous operations
    try:
        parsed_query = json.loads(query)
    except json.JSONDecodeError as e:
        return f"❌ Error al parsear la query ({query}) a JSON: {e}"

    # Check for dangerous operations in query
    blocked_ops = {"$where", "$function", "$accumulator", "$expr"}
    query_str = str(parsed_query).lower()
    if any(op in query_str for op in blocked_ops):
        return "❌ Operación MongoDB no permitida."

    try:
        # Connect to MongoDB (adjust connection string as needed)
        client = MongoClient("mongodb://mongouser:mongopassword@localhost:27017/")
        db = client[database]
        coll = db[collection]

        # Execute query
        results = list(coll.find(parsed_query))

        if not results:
            return "✅ Consulta ejecutada correctamente, sin resultados."

        # Convert MongoDB objects to JSON-serializable format
        return json.dumps(results, default=json_util.default, ensure_ascii=False)

    except Exception as e:
        return f"❌ Error al ejecutar la query: {e}"
    finally:
        client.close()
