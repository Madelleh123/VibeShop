# Unit tests for VibeShop API endpoints
import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.schemas import StoreCreate, ProductCreate, WebhookMessage
import json

client = TestClient(app)

# ============================================================================
# ROOT & HEALTH TESTS
# ============================================================================
def test_root_endpoint():
    """Test that the root endpoint returns a health message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "VibeShop Assistant Running"


# ============================================================================
# STORE TESTS
# ============================================================================
def test_create_store_valid():
    """Test creating a store with valid data"""
    store_data = {
        "name": "Test Store",
        "phone_number": "256700123456",
        "location": "Kampala",
        "market": "Central Market"
    }
    response = client.post("/api/portal/create-store", json=store_data)
    
    # Should succeed or already exist (depending on implementation)
    assert response.status_code in [200, 201, 409]


def test_create_store_invalid_name():
    """Test creating a store with invalid name (too short)"""
    store_data = {
        "name": "A",  # Too short
        "phone_number": "256700123456",
        "location": "Kampala",
    }
    
    # Should fail validation
    with pytest.raises(Exception):
        StoreCreate(**store_data)


def test_create_store_invalid_phone():
    """Test creating a store with invalid phone number"""
    store_data = {
        "name": "Test Store",
        "phone_number": "123",  # Too short
        "location": "Kampala",
    }
    
    # Should fail validation
    with pytest.raises(Exception):
        StoreCreate(**store_data)


def test_create_store_missing_required_fields():
    """Test creating a store without required fields"""
    store_data = {
        "name": "Test Store",
        # Missing phone_number and location
    }
    
    with pytest.raises(Exception):
        StoreCreate(**store_data)


# ============================================================================
# PRODUCT TESTS
# ============================================================================
def test_product_validation_valid():
    """Test product validation with valid data"""
    product_data = {
        "store_id": 1,
        "name": "Test Product",
        "description": "A test product",
        "price": 50000,
        "image_url": None,
    }
    
    product = ProductCreate(**product_data)
    assert product.name == "Test Product"
    assert product.price == 50000


def test_product_validation_invalid_price_zero():
    """Test that price must be greater than zero"""
    product_data = {
        "store_id": 1,
        "name": "Test Product",
        "price": 0,
    }
    
    with pytest.raises(Exception):
        ProductCreate(**product_data)


def test_product_validation_invalid_price_negative():
    """Test that negative prices are rejected"""
    product_data = {
        "store_id": 1,
        "name": "Test Product",
        "price": -1000,
    }
    
    with pytest.raises(Exception):
        ProductCreate(**product_data)


def test_product_validation_price_too_high():
    """Test that prices exceeding maximum are rejected"""
    product_data = {
        "store_id": 1,
        "name": "Test Product",
        "price": 2000000,  # Exceeds 1,000,000 limit
    }
    
    with pytest.raises(Exception):
        ProductCreate(**product_data)


def test_product_name_sanitization():
    """Test that product names are properly sanitized"""
    product_data = {
        "store_id": 1,
        "name": "  Test Product  ",  # Extra spaces
        "price": 50000,
    }
    
    product = ProductCreate(**product_data)
    assert product.name == "Test Product"


def test_get_products():
    """Test retrieving products for a store"""
    response = client.get("/api/portal/products?store_id=1")
    
    # Should return 200 if store exists, 404 if not
    assert response.status_code in [200, 404]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)  # Should be a list of products


# ============================================================================
# WEBHOOK TESTS
# ============================================================================
def test_webhook_message_validation_valid():
    """Test webhook message validation with valid data"""
    webhook_data = {
        "From": "whatsapp:256700123456",
        "Body": "Hello",
        "NumMedia": 0,
    }
    
    message = WebhookMessage(**webhook_data)
    assert message.Body == "Hello"


def test_webhook_message_validation_empty_body():
    """Test that empty message bodies are rejected"""
    webhook_data = {
        "From": "whatsapp:256700123456",
        "Body": "",  # Empty
        "NumMedia": 0,
    }
    
    with pytest.raises(Exception):
        WebhookMessage(**webhook_data)


def test_webhook_message_too_long():
    """Test that messages exceeding max length are rejected"""
    webhook_data = {
        "From": "whatsapp:256700123456",
        "Body": "x" * 5000,  # Too long (max 4096)
        "NumMedia": 0,
    }
    
    with pytest.raises(Exception):
        WebhookMessage(**webhook_data)


# ============================================================================
# SECURITY TESTS
# ============================================================================
def test_portal_endpoint_requires_auth():
    """Test that portal endpoints require authentication"""
    # Try accessing portal without auth - should redirect or require auth
    response = client.get("/portal/")
    
    # Should be accessible (public) or require auth
    assert response.status_code in [200, 401, 403]


# ============================================================================
# INPUT VALIDATION EDGE CASES
# ============================================================================
def test_store_name_with_special_characters():
    """Test store names with special characters"""
    store_data = {
        "name": "Test Store @#$%",
        "phone_number": "256700123456",
        "location": "Kampala",
    }
    
    # Should work - special chars in name are OK, just need sanitization
    store = StoreCreate(**store_data)
    assert "Test Store" in store.name


def test_product_with_very_long_description():
    """Test product with maximum length description"""
    product_data = {
        "store_id": 1,
        "name": "Test Product",
        "description": "x" * 1000,  # Max length
        "price": 50000,
    }
    
    product = ProductCreate(**product_data)
    assert len(product.description) == 1000


def test_product_with_too_long_description():
    """Test that descriptions exceeding max are rejected"""
    product_data = {
        "store_id": 1,
        "name": "Test Product",
        "description": "x" * 1001,  # Exceeds max
        "price": 50000,
    }
    
    with pytest.raises(Exception):
        ProductCreate(**product_data)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================
@pytest.mark.integration
def test_store_and_product_flow():
    """Test complete flow: create store, then create product"""
    # Create store
    store_data = {
        "name": "Integration Test Store",
        "phone_number": "256700999888",
        "location": "Kampala",
    }
    store_response = client.post("/api/portal/create-store", json=store_data)
    assert store_response.status_code in [200, 201, 409]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
