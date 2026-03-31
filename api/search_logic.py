import psycopg2
import os
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from .embedding_logic import get_embedding
from .image_embedding_logic import get_image_embedding

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def search_products(image_bytes: bytes, store_id: int):
    """
    Searches for products using image similarity with cosine distance.
    """
    query_embedding = get_image_embedding(image_bytes)

    if query_embedding is None:
        print("Could not generate a query embedding for the image.")
        return [], -1

    conn = get_connection()
    register_vector(conn)
    cur = conn.cursor()

    # Use cosine distance (<=>) for similarity search on normalized image vectors
    query = """
    SELECT p.product_id, p.name, p.price, s.name AS store_name, s.location, p.store_id, p.image_embedding <=> %s AS distance
    FROM products p
    JOIN stores s ON p.store_id = s.store_id
    WHERE p.store_id = %s
    ORDER BY distance
    LIMIT 3;
    """

    cur.execute(query, (query_embedding, store_id))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return [], -1

    results = []
    # The distance is now the 7th element (index 6)
    top_distance = rows[0][6]

    for r in rows:
        results.append({
            "product_id": r[0],
            "name": r[1],  # Changed from product_name to name
            "price": r[2],
            "store_name": r[3],
            "location": r[4],
            "store_id": r[5]  # Added store_id
        })

    return results, top_distance
