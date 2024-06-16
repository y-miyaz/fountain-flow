CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_type VARCHAR(255),
    value FLOAT,
    is_fragile BOOLEAN,
    created_at TIMESTAMP
);
