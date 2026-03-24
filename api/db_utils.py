import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Create and return a PostgreSQL connection using env values."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST") or "localhost",
        port=os.getenv("DB_PORT") or "5432",
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
