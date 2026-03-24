
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    name TEXT,
    market TEXT
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    store_id INT REFERENCES stores(store_id),
    name TEXT,
    description TEXT,
    price INT,
    image_url TEXT,
    embedding vector(768),
    image_embedding vector(1408)
);
