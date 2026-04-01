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

-- === PERFORMANCE INDEXES ===
-- Store indexes
CREATE INDEX IF NOT EXISTS idx_stores_phone ON stores(phone_number);
CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name);

-- Product indexes
CREATE INDEX IF NOT EXISTS idx_products_store_id ON products(store_id);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);
CREATE INDEX IF NOT EXISTS idx_products_store_name ON products(store_id, name);

-- Vector search index (pgvector)
-- Note: Requires pgvector extension with ivfflat support
CREATE INDEX IF NOT EXISTS idx_products_embedding ON products USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_products_image_embedding ON products USING ivfflat (image_embedding vector_cosine_ops) WITH (lists = 100);

-- Lead indexes
CREATE INDEX IF NOT EXISTS idx_leads_product_id ON leads(product_id);
CREATE INDEX IF NOT EXISTS idx_leads_store_id ON leads(store_id);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_leads_reference_code ON leads(reference_code);

-- Transaction indexes
CREATE INDEX IF NOT EXISTS idx_transactions_store_id ON transactions(store_id);
CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_transactions_buyer_phone ON transactions(buyer_phone);
CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_transactions_reference_code ON transactions(reference_code);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_store_status ON transactions(store_id, status);
