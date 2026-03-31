CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    name TEXT,
    market TEXT,
    phone_number TEXT,
    location TEXT
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

CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id),
    store_id INT REFERENCES stores(store_id),
    reference_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id),
    store_id INT REFERENCES stores(store_id),
    buyer_phone TEXT,
    amount INT,
    commission INT,
    seller_amount INT,
    status TEXT DEFAULT 'pending',
    reference_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
