# pytest configuration and fixtures
import pytest
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv(".env.test")

@pytest.fixture(scope="session")
def test_db():
    """Setup test database connection"""
    from api.db_utils import get_connection
    
    try:
        conn = get_connection()
        yield conn
        conn.close()
    except Exception as e:
        print(f"Could not connect to test database: {e}")
        yield None


@pytest.fixture(scope="function")
def test_store_id(test_db):
    """Create a test store and return its ID"""
    if test_db is None:
        return 1  # Default for offline testing
    
    cursor = test_db.cursor()
    try:
        cursor.execute(
            "INSERT INTO stores (name, phone_number, location) VALUES (%s, %s, %s) RETURNING store_id",
            ("Test Store", "256700123456", "Kampala")
        )
        store_id = cursor.fetchone()[0]
        test_db.commit()
        
        yield store_id
        
        # Cleanup
        cursor.execute("DELETE FROM stores WHERE store_id = %s", (store_id,))
        test_db.commit()
    finally:
        cursor.close()


@pytest.fixture(scope="function")
def test_product_id(test_db, test_store_id):
    """Create a test product and return its ID"""
    if test_db is None:
        return 1
    
    cursor = test_db.cursor()
    try:
        cursor.execute(
            "INSERT INTO products (store_id, name, price) VALUES (%s, %s, %s) RETURNING product_id",
            (test_store_id, "Test Product", 50000)
        )
        product_id = cursor.fetchone()[0]
        test_db.commit()
        
        yield product_id
        
        # Cleanup
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        test_db.commit()
    finally:
        cursor.close()


# Pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "security: mark test as a security test")
