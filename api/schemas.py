# Input validation schemas using Pydantic
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional
import re

class StoreCreate(BaseModel):
    """Validation schema for store creation"""
    name: str = Field(..., min_length=2, max_length=100, description="Store name")
    phone_number: str = Field(..., description="WhatsApp phone number")
    location: str = Field(..., min_length=2, max_length=100, description="Store location")
    market: Optional[str] = Field(None, max_length=100, description="Market name")
    
    @validator('phone_number')
    def validate_phone(cls, v):
        """Validate phone number format"""
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\+]', '', v)
        if not re.match(r'^(?:\d{10,15}|whatsapp:\d{10,15})$', cleaned):
            raise ValueError('Invalid phone number format. Use 10-15 digits.')
        return v
    
    @validator('name', 'location')
    def sanitize_text(cls, v):
        """Sanitize text input"""
        if not v or not isinstance(v, str):
            raise ValueError('Must be non-empty string')
        return v.strip()


class ProductCreate(BaseModel):
    """Validation schema for product creation"""
    store_id: int = Field(..., gt=0, description="Store ID")
    name: str = Field(..., min_length=2, max_length=200, description="Product name")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    price: int = Field(..., gt=0, le=1000000, description="Price in UGX")
    image_url: Optional[HttpUrl] = Field(None, description="Image URL")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Product name is required')
        return v.strip()
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        if v > 1000000:
            raise ValueError('Price exceeds maximum limit')
        return v


class ProductDelete(BaseModel):
    """Validation schema for product deletion"""
    product_id: int = Field(..., gt=0, description="Product ID to delete")
    store_id: int = Field(..., gt=0, description="Store ID for authorization")


class WebhookMessage(BaseModel):
    """Validation schema for WhatsApp webhook messages"""
    From: str = Field(..., description="Sender phone number")
    Body: str = Field(..., min_length=1, max_length=4096, description="Message body")
    NumMedia: int = Field(default=0, ge=0, description="Number of media attachments")
    MediaUrl0: Optional[str] = Field(None, description="First media URL")


class TransactionCreate(BaseModel):
    """Validation schema for transactions"""
    product_id: int = Field(..., gt=0, description="Product ID")
    store_id: int = Field(..., gt=0, description="Store ID")
    buyer_phone: str = Field(..., description="Buyer phone number")
    amount: int = Field(..., gt=0, le=10000000, description="Transaction amount in UGX")
    
    @validator('buyer_phone')
    def validate_buyer_phone(cls, v):
        cleaned = re.sub(r'[\s\-\(\)\+]', '', v)
        if not re.match(r'^\d{10,15}$', cleaned):
            raise ValueError('Invalid buyer phone number')
        return v


class PaymentWebhook(BaseModel):
    """Validation schema for payment provider webhooks"""
    reference_code: str = Field(..., min_length=5, description="Transaction reference code")
    status: str = Field(..., pattern="^(pending|completed|failed|cancelled)$", description="Payment status")
    amount: Optional[int] = Field(None, gt=0, description="Payment amount")
