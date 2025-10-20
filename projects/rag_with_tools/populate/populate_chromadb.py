"""
Script to populate ChromaDB with sample documents.

This script loads sample documents into the ChromaDB vector database
for testing the RAG functionality.
"""

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def populate_chromadb():
    """Populate ChromaDB with sample documents."""

    # Sample documents about products and company information
    sample_documents = [
        Document(
            page_content="Nuestro producto estrella es el Widget X-2000, un dispositivo revolucionario que combina tecnología de punta con diseño elegante. Vendimos 40 unidades el mes pasado.",
            metadata={"source": "sales_report", "category": "products", "date": "2025-01"}
        ),
        Document(
            page_content="En el último mes generamos ingresos de $50,000 dólares, superando nuestras expectativas. El producto Z fue nuestro mayor contribuidor con $20,000 en ventas.",
            metadata={"source": "financial_report", "category": "revenue", "date": "2025-01"}
        ),
        Document(
            page_content="La compañía ofrece garantía de 2 años en todos los productos electrónicos. Para hacer válida la garantía, el cliente debe presentar el comprobante de compra original.",
            metadata={"source": "warranty_policy", "category": "policies"}
        ),
        Document(
            page_content="Nuestra política de devoluciones permite que los clientes devuelvan productos dentro de 30 días posteriores a la compra, siempre que estén en su empaque original y sin usar.",
            metadata={"source": "return_policy", "category": "policies"}
        ),
        Document(
            page_content="El horario de atención al cliente es de lunes a viernes de 9:00 AM a 6:00 PM. Los fines de semana y días festivos nuestras oficinas permanecen cerradas.",
            metadata={"source": "customer_service", "category": "operations"}
        ),
        Document(
            page_content="Contamos con tres ubicaciones: sede principal en Ciudad de México, sucursal en Guadalajara y centro de distribución en Monterrey.",
            metadata={"source": "company_info", "category": "locations"}
        ),
        Document(
            page_content="El producto Z es un software de gestión empresarial que ayuda a las PYMES a automatizar sus procesos de inventario y facturación. Precio: $500 dólares por licencia anual.",
            metadata={"source": "product_catalog", "category": "products"}
        ),
        Document(
            page_content="Nuestra misión es proporcionar soluciones tecnológicas innovadoras que impulsen el crecimiento de las pequeñas y medianas empresas en América Latina.",
            metadata={"source": "company_info", "category": "about"}
        ),
    ]

    # Define persistent directory
    persist_directory = Path(__file__).parent / "chroma_db"
    persist_directory.mkdir(exist_ok=True)

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Create vectorstore
    vectorstore = Chroma(
        collection_name="knowledge_base",
        embedding_function=embeddings,
        persist_directory=str(persist_directory),
    )

    # Check if collection already has documents
    existing_count = vectorstore._collection.count()

    if existing_count > 0:
        print(f"⚠️  ChromaDB ya contiene {existing_count} documentos.")
        response = input("¿Quieres eliminar los documentos existentes y volver a cargar? (s/n): ")
        if response.lower() == 's':
            # Delete existing collection
            vectorstore.delete_collection()
            print("✓ Colección eliminada.")

            # Recreate vectorstore
            vectorstore = Chroma(
                collection_name="knowledge_base",
                embedding_function=embeddings,
                persist_directory=str(persist_directory),
            )
        else:
            print("❌ Operación cancelada. No se modificó ChromaDB.")
            return

    # Add documents to vectorstore
    print(f"Agregando {len(sample_documents)} documentos a ChromaDB...")
    vectorstore.add_documents(sample_documents)

    # Verify
    final_count = vectorstore._collection.count()
    print(f"✓ ChromaDB poblado exitosamente con {final_count} documentos.")

    # Test a sample query
    print("\n--- Prueba de búsqueda ---")
    test_query = "¿Cuánto ganamos el mes pasado?"
    results = vectorstore.similarity_search(test_query, k=2)
    print(f"Query: {test_query}")
    print(f"Resultados encontrados: {len(results)}")
    for i, doc in enumerate(results, 1):
        print(f"\nDocumento {i}:")
        print(f"  Contenido: {doc.page_content[:100]}...")
        print(f"  Metadata: {doc.metadata}")


if __name__ == "__main__":
    populate_chromadb()
