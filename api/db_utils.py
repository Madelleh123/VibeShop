import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Create and return a PostgreSQL connection using env values."""
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            return psycopg2.connect(database_url)
        else:
            return psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432"),
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
    except Exception as e:
        print(f"Database connection error: {e}")
        raise RuntimeError(f"Failed to connect to database: {e}")