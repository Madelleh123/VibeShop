# VibeShop Seller Portal Documentation

## Overview

The VibeShop Seller Portal is a simple, mobile-optimized interface for local market sellers to:
1. **Create a store** (once per seller)
2. **Manage products** (add, view, delete)
3. **Prepare data for AI search** (text + image embeddings)

It is **NOT** a marketplace. It is purely a management tool connecting sellers to the WhatsApp-based customer interface.

---

## System Architecture

```
SELLER PORTAL (Frontend)
    ↓
FastAPI Backend (/api/portal)
    ↓
PostgreSQL Database (with pgvector)
    ↓
WhatsApp Bot + AI Search
```

### Data Flow: Store → Product → Vector Embedding → Search

```
1. Seller creates store via portal
   → store_id generated automatically
   → stored in PostgreSQL

2. Seller uploads product
   → product_id auto-generated
   → linked to store_id
   → image processed for embedding

3. Image → Vertex AI Multimodal Model
   → image_embedding (1408-dim vector)
   → stored in pgvector

4. Text (product name) → Vertex AI Text Model
   → text_embedding (768-dim vector)
   → used for semantic search

5. Customer sends image via WhatsApp
   → Search endpoint matches against vectors
   → Returns top 3 products with store_id
   → Customer can purchase and generate transaction
```

---

## Database Schema

### `stores` Table
```sql
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    name TEXT,
    phone_number TEXT,           -- WhatsApp phone for seller
    location TEXT,
    market TEXT                  -- Category/market (optional)
);
```

**Primary Key:** `store_id` (auto-generated)

### `products` Table
```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    store_id INT REFERENCES stores(store_id),
    name TEXT,
    description TEXT,            -- Now supported by portal
    price INT,                   -- In UGX
    image_url TEXT,
    embedding vector(768),       -- Text embedding (future)
    image_embedding vector(1408) -- Image embedding (Vertex AI multimodal)
);
```

**Foreign Key:** `store_id` → `stores(store_id)`

### Other Tables
- `leads` — Store customer interest/clicks
- `transactions` — Payment records with commission tracking

---

## Frontend Structure

### Portal Pages

**Location:** `/portal/`

#### `index.html`
- **Step 1: Store Creation**
  - Inputs: store name, phone, location
  - Output: store_id (displayed to seller)
  - Auto-redirect to product section on success

- **Step 2: Product Management**
  - Add products with name, price, description, image
  - Image source: local file OR URL
  - View all products (grid layout)
  - Delete products
  - Change store (logout + re-create)

#### `app.js`
- LocalStorage persistence (store_id, store_name)
- Fetch API calls to backend
- Product list loading and refresh
- Image preview before upload
- Status message system (success/error/info)

---

## Backend API Endpoints

### Base URL
```
http://localhost:8000/api/portal
```

---

### 1. **Create Store** (POST)
**Endpoint:** `/create-store`

**Request:**
```
POST /api/portal/create-store
Content-Type: application/x-www-form-urlencoded

name=My Store&phone_number=+256771234567&location=Kampala
```

**Response (Success):**
```json
{
    "status": "success",
    "store_id": 42,
    "message": "Store 'My Store' created successfully"
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Store creation failed..."
}
```

---

### 2. **Upload Product** (POST)
**Endpoint:** `/upload-product`

**Request:**
```
POST /api/portal/upload-product
Content-Type: multipart/form-data

store_id: 42
name: "Red T-Shirt"
price: 25000
description: "High-quality cotton t-shirt"
image: <file or image_url>
```

**Response (Success):**
```json
{
    "status": "success",
    "product": {
        "id": 123,
        "name": "Red T-Shirt",
        "price": 25000
    }
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Failed to generate image embedding"
}
```

---

### 3. **List Products** (GET)
**Endpoint:** `/products?store_id=42`

**Request:**
```
GET /api/portal/products?store_id=42
```

**Response:**
```json
{
    "status": "success",
    "products": [
        {
            "product_id": 123,
            "name": "Red T-Shirt",
            "description": "High-quality cotton t-shirt",
            "price": 25000,
            "image_url": "https://..."
        },
        {
            "product_id": 124,
            "name": "Blue Jeans",
            "description": "",
            "price": 45000,
            "image_url": "https://..."
        }
    ]
}
```

---

### 4. **Delete Product** (POST)
**Endpoint:** `/delete-product`

**Request:**
```
POST /api/portal/delete-product
Content-Type: application/json

{"product_id": 123}
```

**Response (Success):**
```json
{
    "status": "success",
    "message": "Product deleted"
}
```

**Response (Error):**
```json
{
    "status": "error",
    "message": "Product not found"
}
```

---

## Frontend Workflow

### Step 1: Store Creation
```
User opens portal
    ↓
Enters store details (name, phone, location)
    ↓
Clicks "Create Store"
    ↓
POST /api/portal/create-store
    ↓
Backend saves to PostgreSQL
    ↓
store_id returned to frontend
    ↓
LocalStorage persists: vibeshop_store_id, vibeshop_store_name
    ↓
Auto-redirect to Step 2
```

### Step 2: Product Management
```
Seller in portal with store created
    ↓
Enters product details (name, price, desc, image)
    ↓
Clicks "Add Product"
    ↓
POST /api/portal/upload-product
    ↓
Image → Vertex AI → embedding
    ↓
Backend saves to PostgreSQL with embedding
    ↓
GET /api/portal/products (refresh list)
    ↓
Frontend displays all products
    ↓
Seller can delete products
    ↓
Seller can change store (logout)
```

---

## Image Handling & Embeddings

### Image Processing Pipeline

1. **Upload Source**
   - Local file: Uploaded via multipart/form-data
   - URL: Fetched by backend via `requests.get()`

2. **Image to Embedding**
   - Uses Vertex AI Multimodal Embedding Model (`multimodalembedding@001`)
   - Output: 1408-dimensional vector
   - Normalized (L2 normalized)
   - Stored in PostgreSQL pgvector column

3. **Vector Search (WhatsApp Bot)**
   - Customer sends image
   - Image → Vertex AI → 1408-dim vector
   - Cosine distance search in pgvector
   - Returns top 3 products from any store

---

## Key Features

### ✅ Implemented
- Store creation with auto-generated ID
- Product upload with image (local or URL)
- Product listing
- Product deletion
- Image preview before upload
- LocalStorage persistence (seller session)
- Mobile-responsive UI
- Lazy-loading of embeddings (no heavy initialization at startup)
- Error handling with user-friendly messages

### 🚀 Future Enhancements
- Product editing (update name, price, description)
- Bulk product import (CSV)
- Store analytics (view count, purchase count)
- Multi-language support (Luganda, Swahili, etc.)
- Seller communication tools (WhatsApp notifications)
- Inventory tracking

---

## Deployment Checklist

- [ ] PostgreSQL database initialized with schema
- [ ] Vertex AI credentials set (GOOGLE_PROJECT_ID, GOOGLE_REGION)
- [ ] FastAPI server running on `http://localhost:8000`
- [ ] Portal accessible at `/portal/`
- [ ] Test store creation
- [ ] Test product upload with image
- [ ] Test product listing
- [ ] Test product deletion
- [ ] Verify embedding generation (check for success log)
- [ ] Test WhatsApp webhook image search

---

## Troubleshooting

### Portal won't load
- Check if FastAPI server is running: `python -m uvicorn api.main:app --reload`
- Check network access to backend

### Image upload fails
- Ensure image file is valid (JPEG, PNG, WebP)
- Check if `google-cloud-aiplatform` is installed
- Check if GOOGLE_PROJECT_ID is set

### Products not appearing in list
- Check PostgreSQL connection
- Verify store_id is correct
- Check database schema (should have `products` table)

### Slow embedding generation
- Vertex AI calls may take time on first request (lazy initialization)
- Image size matters (larger images = slower processing)

---

## API Security Notes

### Current State
- No authentication on portal endpoints
- Open to public (use firewall in production)

### Future: Add Authentication
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/portal/upload-product")
async def upload_product(..., credentials = Depends(security)):
    # Verify seller identity
    pass
```

---

## Performance Optimization

### Current
- **Lazy initialization** of Vertex AI models (only when needed)
- **Database indexes** on `store_id` and `product_id`
- **Vector search** uses pgvector native operators

### Future
- Cache product list in Redis
- CDN for image storage
- Batch embedding processing
- Database partitioning by market region

---

## Support & Questions

For issues or feature requests, check logs:
```bash
# Server logs
tail -f /var/log/vibeshop/server.log

# Database logs
psql -U vibeshop_user vibeshop_db -c "SHOW log_filename"
```

---

**Last Updated:** March 30, 2026  
**Portal Version:** 1.0  
**API Version:** v1
