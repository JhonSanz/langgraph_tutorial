#!/usr/bin/env python3
"""
PostgreSQL Sales Database Setup
Database: sales_db
Description: Base de datos de ventas con información de productos y transacciones
"""

from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import date, datetime

# PostgreSQL connection details (from datasources.yaml)
PG_HOST = "localhost"
PG_PORT = 5432
PG_DATABASE = "mydatabase"
PG_USER = "myuser"
PG_PASSWORD = "mypassword"

Base = declarative_base()

# Define models
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50))
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    sales = relationship("Sale", back_populates="product")

    __table_args__ = (
        Index('idx_products_category', 'category'),
    )


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    product = Column(String(100), nullable=False)  # Denormalized for easier querying
    amount = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    date = Column(Date, nullable=False)
    customer_name = Column(String(100))

    product_rel = relationship("Product", back_populates="sales")

    __table_args__ = (
        Index('idx_sales_date', 'date'),
        Index('idx_sales_product_id', 'product_id'),
    )


# Sample products data
PRODUCTS_DATA = [
    {'name': 'Product A', 'price': 99.99, 'category': 'Electronics', 'stock': 50},
    {'name': 'Product B', 'price': 49.99, 'category': 'Electronics', 'stock': 100},
    {'name': 'Product C', 'price': 29.99, 'category': 'Home', 'stock': 75},
    {'name': 'Product D', 'price': 149.99, 'category': 'Electronics', 'stock': 25},
    {'name': 'Product E', 'price': 19.99, 'category': 'Home', 'stock': 200},
    {'name': 'Product F', 'price': 79.99, 'category': 'Sports', 'stock': 60},
    {'name': 'Product G', 'price': 199.99, 'category': 'Electronics', 'stock': 15},
    {'name': 'Product H', 'price': 39.99, 'category': 'Home', 'stock': 80},
]

# Sample sales data
SALES_DATA = [
    {'product_id': 1, 'product': 'Product A', 'amount': 299.97, 'quantity': 3, 'date': date(2025, 1, 15), 'customer_name': 'John Doe'},
    {'product_id': 1, 'product': 'Product A', 'amount': 99.99, 'quantity': 1, 'date': date(2025, 2, 20), 'customer_name': 'Jane Smith'},
    {'product_id': 2, 'product': 'Product B', 'amount': 99.98, 'quantity': 2, 'date': date(2025, 1, 10), 'customer_name': 'Mike Johnson'},
    {'product_id': 3, 'product': 'Product C', 'amount': 89.97, 'quantity': 3, 'date': date(2025, 2, 5), 'customer_name': 'Sarah Williams'},
    {'product_id': 4, 'product': 'Product D', 'amount': 149.99, 'quantity': 1, 'date': date(2025, 1, 25), 'customer_name': 'Robert Brown'},
    {'product_id': 1, 'product': 'Product A', 'amount': 199.98, 'quantity': 2, 'date': date(2025, 3, 1), 'customer_name': 'Emily Davis'},
    {'product_id': 5, 'product': 'Product E', 'amount': 59.97, 'quantity': 3, 'date': date(2025, 2, 14), 'customer_name': 'David Wilson'},
    {'product_id': 6, 'product': 'Product F', 'amount': 159.98, 'quantity': 2, 'date': date(2025, 1, 30), 'customer_name': 'Lisa Anderson'},
    {'product_id': 7, 'product': 'Product G', 'amount': 199.99, 'quantity': 1, 'date': date(2025, 3, 10), 'customer_name': 'James Taylor'},
    {'product_id': 2, 'product': 'Product B', 'amount': 149.97, 'quantity': 3, 'date': date(2025, 2, 28), 'customer_name': 'Mary Martinez'},
    {'product_id': 3, 'product': 'Product C', 'amount': 29.99, 'quantity': 1, 'date': date(2025, 1, 5), 'customer_name': 'Christopher Lee'},
    {'product_id': 8, 'product': 'Product H', 'amount': 79.98, 'quantity': 2, 'date': date(2025, 3, 15), 'customer_name': 'Patricia Garcia'},
    {'product_id': 4, 'product': 'Product D', 'amount': 299.98, 'quantity': 2, 'date': date(2025, 2, 10), 'customer_name': 'Daniel Rodriguez'},
    {'product_id': 5, 'product': 'Product E', 'amount': 19.99, 'quantity': 1, 'date': date(2025, 1, 18), 'customer_name': 'Jennifer Lopez'},
    {'product_id': 6, 'product': 'Product F', 'amount': 79.99, 'quantity': 1, 'date': date(2025, 3, 5), 'customer_name': 'Matthew Hernandez'},
]


def main():
    """Main function to populate PostgreSQL"""
    print("=" * 60)
    print("PostgreSQL Sales Database Setup")
    print("=" * 60)

    engine = None
    Session = None
    session = None

    try:
        # Create engine and connect to PostgreSQL
        print(f"\nConnecting to PostgreSQL at {PG_HOST}:{PG_PORT}...")
        connection_string = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
        engine = create_engine(connection_string)
        print("✓ Connected successfully")

        # Drop and create all tables
        print("\nDropping existing tables if they exist...")
        Base.metadata.drop_all(engine)
        print("✓ Tables dropped")

        print("\nCreating tables...")
        Base.metadata.create_all(engine)
        print("✓ Tables created successfully")

        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Insert sample products
        print("\nInserting sample products...")
        products = [Product(**data) for data in PRODUCTS_DATA]
        session.add_all(products)
        session.flush()  # Flush to get IDs
        print(f"✓ Inserted {len(products)} products")

        # Insert sample sales
        print("Inserting sample sales...")
        sales = [Sale(**data) for data in SALES_DATA]
        session.add_all(sales)
        print(f"✓ Inserted {len(sales)} sales")

        # Commit all changes
        session.commit()

        # Verify data
        print("\n" + "=" * 60)
        print("Data Verification")
        print("=" * 60)

        products_count = session.query(Product).count()
        print(f"Products count: {products_count}")

        sales_count = session.query(Sale).count()
        print(f"Sales count: {sales_count}")

        # Show sample data
        print("\nSample products (first 5):")
        for product in session.query(Product).limit(5):
            print(f"  - ID: {product.id}, Name: {product.name}, Price: ${product.price}, Category: {product.category}, Stock: {product.stock}")

        print("\nSample sales (first 5):")
        for sale in session.query(Sale).limit(5):
            print(f"  - ID: {sale.id}, Product: {sale.product}, Amount: ${sale.amount}, Qty: {sale.quantity}, Date: {sale.date}, Customer: {sale.customer_name}")

        # Show sales by category
        print("\nSales summary by category:")
        results = session.query(
            Product.category,
            func.count(Sale.id).label('num_sales'),
            func.sum(Sale.amount).label('total_amount')
        ).join(Sale, Product.id == Sale.product_id)\
         .group_by(Product.category)\
         .order_by(func.sum(Sale.amount).desc())\
         .all()

        for row in results:
            print(f"  - {row[0]}: {row[1]} sales, Total: ${row[2]}")

        print("\n" + "=" * 60)
        print("✓ PostgreSQL population completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        if session:
            session.rollback()
        return 1
    finally:
        if session:
            session.close()
        if engine:
            engine.dispose()

    return 0


if __name__ == "__main__":
    exit(main())
