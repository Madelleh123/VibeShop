import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Create and return a PostgreSQL connection using DATABASE_URL."""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set")
        return psycopg2.connect(database_url)
    except Exception as e:
        print(f"Database connection error: {e}")
        raise RuntimeError(f"Failed to connect to database: {e}")