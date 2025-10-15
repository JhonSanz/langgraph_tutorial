-- PostgreSQL Sales Database Setup
-- Database: sales_db
-- Description: Base de datos de ventas con información de productos y transacciones

-- Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS products CASCADE;

-- Create products table
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50),
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sales table
CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product VARCHAR(100) NOT NULL,  -- Denormalized for easier querying
    amount DECIMAL(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    customer_name VARCHAR(100),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Insert sample products
INSERT INTO products (name, price, category, stock) VALUES
    ('Product A', 99.99, 'Electronics', 50),
    ('Product B', 49.99, 'Electronics', 100),
    ('Product C', 29.99, 'Home', 75),
    ('Product D', 149.99, 'Electronics', 25),
    ('Product E', 19.99, 'Home', 200),
    ('Product F', 79.99, 'Sports', 60),
    ('Product G', 199.99, 'Electronics', 15),
    ('Product H', 39.99, 'Home', 80);

-- Insert sample sales
INSERT INTO sales (product_id, product, amount, quantity, date, customer_name) VALUES
    (1, 'Product A', 299.97, 3, '2025-01-15', 'John Doe'),
    (1, 'Product A', 99.99, 1, '2025-02-20', 'Jane Smith'),
    (2, 'Product B', 99.98, 2, '2025-01-10', 'Mike Johnson'),
    (3, 'Product C', 89.97, 3, '2025-02-05', 'Sarah Williams'),
    (4, 'Product D', 149.99, 1, '2025-01-25', 'Robert Brown'),
    (1, 'Product A', 199.98, 2, '2025-03-01', 'Emily Davis'),
    (5, 'Product E', 59.97, 3, '2025-02-14', 'David Wilson'),
    (6, 'Product F', 159.98, 2, '2025-01-30', 'Lisa Anderson'),
    (7, 'Product G', 199.99, 1, '2025-03-10', 'James Taylor'),
    (2, 'Product B', 149.97, 3, '2025-02-28', 'Mary Martinez'),
    (3, 'Product C', 29.99, 1, '2025-01-05', 'Christopher Lee'),
    (8, 'Product H', 79.98, 2, '2025-03-15', 'Patricia Garcia'),
    (4, 'Product D', 299.98, 2, '2025-02-10', 'Daniel Rodriguez'),
    (5, 'Product E', 19.99, 1, '2025-01-18', 'Jennifer Lopez'),
    (6, 'Product F', 79.99, 1, '2025-03-05', 'Matthew Hernandez');

-- Create indexes for better query performance
CREATE INDEX idx_sales_date ON sales(date);
CREATE INDEX idx_sales_product_id ON sales(product_id);
CREATE INDEX idx_products_category ON products(category);

-- Verify data
SELECT 'Products count:' as info, COUNT(*) as count FROM products
UNION ALL
SELECT 'Sales count:' as info, COUNT(*) as count FROM sales;

COMMIT;
