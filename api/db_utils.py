import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def init_db(conn):
    """Initialize database schema if tables do not exist."""
    try:
        cur = conn.cursor()
        
        # Enable vector extension
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Create stores table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                store_id SERIAL PRIMARY KEY,
                name TEXT,
                market TEXT,
                phone_number TEXT,
                location TEXT,
                store_code TEXT UNIQUE
            );
        """)
        
        # Add store_code column to existing stores table if it doesn't exist
        cur.execute("""
            ALTER TABLE stores 
            ADD COLUMN IF NOT EXISTS store_code TEXT UNIQUE;
        """)
        
        # Create products table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                store_id INT REFERENCES stores(store_id),
                name TEXT,
                description TEXT,
                price INT,
                image_url TEXT,
                embedding vector(768),
                image_embedding vector(1408) NULL
            );
        """)
        
        # Create leads table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                product_id INT REFERENCES products(product_id),
                store_id INT REFERENCES stores(store_id),
                reference_code TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create transactions table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
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
        """)
        
        # Create indexes for performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stores_phone ON stores(phone_number);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_store_id ON products(store_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);")
        
        conn.commit()
        cur.close()
        print("Database schema initialized successfully.")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        raise


def get_connection():
    """Create and return a PostgreSQL connection using DATABASE_URL."""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set")
        conn = psycopg2.connect(database_url)
        init_db(conn)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise RuntimeError(f"Failed to connect to database: {e}")