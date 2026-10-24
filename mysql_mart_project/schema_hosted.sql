-- Run this script against the database selected in your hosted MySQL service.
-- In Railway, open the MySQL service's query/connection details and select MYSQLDATABASE.
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (price >= 0),
    CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    product_id INT NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Placed',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_order_product FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE RESTRICT,
    CHECK (quantity > 0),
    CHECK (total_amount >= 0)
);

INSERT INTO products (product_name, category, price, stock)
SELECT 'Laptop', 'Electronics', 55000.00, 8
WHERE NOT EXISTS (SELECT 1 FROM products WHERE product_name='Laptop');

INSERT INTO products (product_name, category, price, stock)
SELECT 'Headphones', 'Electronics', 1500.00, 25
WHERE NOT EXISTS (SELECT 1 FROM products WHERE product_name='Headphones');

INSERT INTO products (product_name, category, price, stock)
SELECT 'School Bag', 'Accessories', 900.00, 20
WHERE NOT EXISTS (SELECT 1 FROM products WHERE product_name='School Bag');

INSERT INTO products (product_name, category, price, stock)
SELECT 'Keyboard', 'Electronics', 1200.00, 15
WHERE NOT EXISTS (SELECT 1 FROM products WHERE product_name='Keyboard');

INSERT INTO products (product_name, category, price, stock)
SELECT 'Notebook', 'Stationery', 80.00, 100
WHERE NOT EXISTS (SELECT 1 FROM products WHERE product_name='Notebook');

INSERT INTO products (product_name, category, price, stock)
SELECT 'Wireless Mouse', 'Electronics', 650.00, 30
WHERE NOT EXISTS (SELECT 1 FROM products WHERE product_name='Wireless Mouse');
