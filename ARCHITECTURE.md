# VibeShop System Architecture & Data Flow

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    VibeShop Ecosystem                            │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐           ┌──────────────────┐
│  SELLER PORTAL   │           │  WHATSAPP BOT    │
│  (index.html)    │           │ (Customer UX)    │
│                  │           │                  │
│ • Store Create   │           │ • Search by Image│
│ • Add Products   │           │ • Browse Results │
│ • Edit/Delete    │           │ • Make Purchase  │
└────────┬─────────┘           └────────┬─────────┘
         │                              │
         │          FastAPI Backend     │
         ├──────────────────────────────┤
         │                              │
    POST /api/portal/               GET /webhook
    • create-store          ←→     (Twilio WhatsApp)
    • upload-product
    • delete-product
    • get-products
    • search-products
         │
         ▼
┌──────────────────────────────────────────┐
│      PostgreSQL Database                 │
│      (with pgvector extension)           │
│                                          │
│  stores ──┐                              │
│           ├──→ products                  │
│           │    ├── image_embedding       │
│           │    └── text_embedding        │
│           │                              │
│           ├──→ transactions              │
│           └──→ leads                     │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│     Vertex AI Models                     │
│     (Google Cloud)                       │
│                                          │
│  • TextEmbedding (768-dim)              │
│  • MultiModalEmbedding (1408-dim)       │
│  • Image Classification (optional)       │
└──────────────────────────────────────────┘

```

---

## Data Flow: Complete Journey

### Phase 1: Seller Onboarding

```
┌─────────────────────────────────────────┐
│ SELLER OPENS PORTAL                     │
│ http://localhost:8000/portal/           │
└──────────────┬──────────────────────────┘
               │
               ▼
        ┌─────────────────┐
        │ Checks localStorage
        │ for vibeshop_store_id
        └────┬──────────┬─────┘
        ┌────┘          └──────┐
   YES  │ (return user)        │ NO
        ▼                      ▼
    ┌────────────┐      ┌──────────────────┐
    │ Show form  │      │ Show create store│
    │ to upload  │      │ form             │
    │ products   │      └─────┬────────────┘
    └────────────┘            │
                               ▼
                    ┌─────────────────────┐
                    │ SELLER CREATES STORE│
                    │ Input:              │
                    │ • Store name        │
                    │ • Phone (WhatsApp)  │
                    │ • Location          │
                    └────────┬────────────┘
                             │
                             ▼
                    ┌─────────────────────┐
                    │ POST /api/portal/   │
                    │ create-store        │
                    └────────┬────────────┘
                             │
                             ▼
    ┌────────────────────────────────────┐
    │ Backend Processing:                │
    │                                    │
    │ 1. Validate inputs                 │
    │ 2. INSERT INTO stores:             │
    │    - name, phone_number, location  │
    │    - store_id (auto-generated)     │
    │ 3. COMMIT to PostgreSQL            │
    │ 4. Return store_id to frontend     │
    └──────────────┬─────────────────────┘
                   │
                   ▼
    ┌────────────────────────────────────┐
    │ Frontend Receives store_id         │
    │ localStorage[vibeshop_store_id] = 42
    │ localStorage[vibeshop_store_name]  │
    │ → Redirect to product upload step  │
    └────────────────────────────────────┘
```

---

### Phase 2: Product Upload

```
┌──────────────────────────────────┐
│ SELLER IN PRODUCT UPLOAD PAGE    │
│ Store displayed: "My Fashion 42" │
└────────┬─────────────────────────┘
         │
         ▼
    ┌──────────────────┐
    │ Select image      │
    │ • Local file OR  │
    │ • URL            │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────┐
    │ Enter details:   │
    │ • Name           │
    │ • Price          │
    │ • Description    │
    └────────┬─────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │ Click "Add Product"          │
    │ POST /api/portal/upload-product
    └────────┬─────────────────────┘
             │
             ▼
    ┌────────────────────────────────────────┐
    │ Backend Processing:                    │
    │                                        │
    │ 1. Receive multipart data:             │
    │    - store_id: 42                      │
    │    - name: "Red T-Shirt"               │
    │    - price: 25000                      │
    │    - description: "..."                │
    │    - image: <file or URL bytes>        │
    │                                        │
    │ 2. Call get_image_embedding(image)     │
    │    → Lazy init Vertex AI client        │
    │    → Send to MultiModalEmbedding       │
    │    → Receive 1408-dim vector           │
    │    → L2 normalize                      │
    │                                        │
    │ 3. INSERT INTO products:               │
    │    - store_id: 42                      │
    │    - name: "Red T-Shirt"               │
    │    - price: 25000                      │
    │    - description: "..."                │
    │    - image_url: "..."                  │
    │    - image_embedding: [0.1, 0.2, ...] │
    │    - product_id (auto-generated: 123) │
    │                                        │
    │ 4. COMMIT to PostgreSQL                │
    │ 5. Return {status, product.id}        │
    └────────┬─────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────┐
    │ Frontend receives response     │
    │ Success: Show confirmation     │
    │ + Refresh product list         │
    │ GET /api/portal/products       │
    │   ?store_id=42                 │
    └────────┬───────────────────────┘
             │
             ▼
    ┌────────────────────────────────┐
    │ Display product grid           │
    │ • Product image (thumbnail)    │
    │ • Name, price, description     │
    │ • Delete button                │
    └────────────────────────────────┘
```

---

### Phase 3: Customer Search (WhatsApp)

```
┌──────────────────────────────────┐
│ CUSTOMER SENDS IMAGE TO WHATSAPP │
│ "Show me similar clothes"        │
└────────┬─────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Twilio receives image                  │
│ Sends webhook POST to /webhook         │
│ MediaUrl0: "https://..."               │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ FastAPI /webhook handler:              │
│                                        │
│ 1. Extract image URL from request      │
│ 2. requests.get(MediaUrl0)             │
│    → Download image from Twilio CDN    │
│    → image_bytes                       │
│                                        │
│ 3. Call search_products(image_bytes)   │
│    from search_logic.py:               │
│                                        │
│    a) get_image_embedding(image)       │
│       → Vertex AI multimodal           │
│       → query_embedding (1408-dim)     │
│       → L2 normalize                   │
│                                        │
│    b) PostgreSQL pgvector query:       │
│       SELECT product_id, name, price,  │
│              store_name, location      │
│       FROM products p                  │
│       JOIN stores s on p.store_id...   │
│       ORDER BY                         │
│         p.image_embedding <=> query_embedding
│       LIMIT 3                          │
│       (cosine distance search)         │
│                                        │
│    c) Returns top 3 matches with:      │
│       - product details                │
│       - store info                     │
│       - distance score                 │
│                                        │
│ 4. Format for WhatsApp:                │
│    "Here are 3 similar items:          │
│     1️⃣ Red T-Shirt - 25000 UGX        │
│        Store: My Fashion (Kampala)     │
│     2️⃣ Blue Shirt - 22000 UGX        │
│     3️⃣ Green Shirt - 28000 UGX        │
│                                        │
│     Reply with number to select"       │
└────────┬──────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Customer replies "1"                   │
│ Backend handler:                       │
│                                        │
│ 1. Lookup product_id from search       │
│ 2. Store in user_state[phone]          │
│ 3. Transition to payment flow          │
└────────┬──────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────┐
│ Customer pays via USSD                 │
│ Backend creates transaction:           │
│                                        │
│ INSERT INTO transactions:              │
│   - buyer_phone                        │
│   - product_id                         │
│   - amount                             │
│   - commission (%) calc                │
│   - seller_amount = amt - commission   │
│   - store_id (from product)            │
│   - status: 'completed'                │
│                                        │
│ Seller notified via WhatsApp           │
│ "You have a new order!"                │
└────────────────────────────────────────┘
```

---

## Database Relationships

```
stores (1)
  │
  ├─→ products (N)
  │     ├─ product_id (PK)
  │     ├─ store_id (FK)
  │     ├─ name
  │     ├─ price
  │     ├─ image_embedding [vector 1408]
  │     │
  │     ├─→ transactions (N)
  │     │    ├─ buyer_phone
  │     │    ├─ product_id (FK)
  │     │    ├─ store_id (FK)
  │     │    └─ commission
  │     │
  │     └─→ leads (N)
  │          ├─ product_id (FK)
  │          ├─ store_id (FK)
  │          └─ reference_code
  │
  └─→ transactions (N)
       └─ Direct seller sales
```

---

## Vector Search Implementation

### Embedding Dimensions

| Model | Dimension | Use Case |
|-------|-----------|----------|
| `textembedding-gecko@003` | 768 | Product names (future) |
| `multimodalembedding@001` | 1408 | Product images |

### Search Algorithm

```
# Customer image → Query embedding
query_embedding = get_image_embedding(customer_image)
# [1408-dimensional normalized vector]

# Cosine distance search in pgvector
SELECT product_id, name, price, store_name
FROM products p
JOIN stores s ON p.store_id = s.store_id
WHERE s.market = customer_market  # (optional filter)
ORDER BY p.image_embedding <=> query_embedding
       -- pgvector cosine distance operator
LIMIT 3;
```

### Distance Metric

- **<=> (cosine distance)**
- Values: 0 (identical) to 2 (opposite)
- Lower = better match
- **Normalized vectors** ensure consistent scoring

---

## Error Handling Flow

```
Customer Image Search
    │
    ├─ No image: "Send an image of what you want"
    │
    ├─ Embedding failed: "Could not process image"
    │
    ├─ No products found: "Sorry, no matches found"
    │
    ├─ Database error: "System error, try again"
    │
    └─ Success → Return results
```

---

## Performance Considerations

### Current Optimizations

1. **Lazy Initialization**
   - Vertex AI models only loaded on first use
   - Reduces startup time ~80%

2. **Database Indexes**
   ```sql
   CREATE INDEX idx_products_store_id ON products(store_id);
   CREATE INDEX idx_products_image_embedding ON products USING ivfflat 
       (image_embedding vector_cosine_ops);
   ``` 

3. **Vector Normalization**
   - Vectors normalized before storage
   - Faster cosine distance (dot product = similarity)

### Bottlenecks

| Component | Time | Mitigation |
|-----------|------|-----------|
| Image embedding | 2-5s | Cache, batch processing |
| Network upload | 1-3s | CDN, compression |
| DB query | 100-500ms | Indexing, partitioning |
| WhatsApp latency | 1-2s | Accept as SLA |

---

## Scalability Path

### Stage 1: Single Market (Current)
- Single database
- Direct Vertex AI API calls
- No caching

### Stage 2: Multi-Market
```python
# Filter by market on search
markets = ["kampala", "mbarara", "jinja"]

for market in markets:
    results += search_products(
        image, 
        store_id=None, 
        market=market
    )
```

### Stage 3: Regional Sharding
```
├─ Uganda Region
│  ├─ Kampala DB
│  ├─ Masaka DB
│  └─ Fort Portal DB
│
├─ Kenya Region
│  ├─ Nairobi DB
│  └─ Mombasa DB
│
└─ Multi-region replication
```

### Stage 4: ML Pipeline
```
store_embeddings
    ├─ Average product embeddings per store
    ├─ Detect store specialization
    └─ Personalized recommendations
```

---

## Security Architecture

### Current State
- **Portal:** Public (open)
- **WhatsApp Webhook:** Twilio signature verification (TBD)
- **Database:** Local connection (no internet exposure)
- **Vertex AI:** Google service account (IAM roles)

### Production Hardening
```python
# 1. Portal authentication
@auth.login_required
def create_store():
    pass

# 2. Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@limiter.limit("100/hour")
def upload_product():
    pass

# 3. Input validation
from pydantic import BaseModel, Field
class StoreCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., regex=r'^\+\d{1,3}\d{6,14}$')

# 4. CORS restriction
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, 
    allow_origins=["https://vibeshop.example.com"])
```

---

## Deployment Target

### Local Development
```bash
# 1. Start PostgreSQL
docker run -e POSTGRES_PASSWORD=pass postgres:15

# 2. Set environment
export GOOGLE_PROJECT_ID=my-project
export GOOGLE_REGION=us-central1
export DB_HOST=localhost
export DB_NAME=vibeshop

# 3. Run embedded models
python -m uvicorn api.main:app --reload

# 4. Access portal
curl http://localhost:8000/portal/
```

### Production Deployment
```
AWS/GCP/DigitalOcean
  ├─ RDS PostgreSQL (managed)
  ├─ App Server (FastAPI + Gunicorn)
  ├─ CDN (image hosting)
  ├─ Vertex AI (Google Cloud)
  └─ Monitoring (DataDog/New Relic)
```

---

## Future Roadmap

- [ ] Seller authentication & multi-user support
- [ ] Product analytics (views, sales, search rank)
- [ ] Bulk import from CSV
- [ ] Product variants (size, color, etc.)
- [ ] Inventory tracking
- [ ] Seller commission dashboard
- [ ] Mobile-native apps (iOS/Android)
- [ ] AI recommendations for sellers ("trending items")
- [ ] Marketplace federation (Uganda ↔ Kenya ↔ Tanzania)

---

**Document Version:** 1.0  
**Last Updated:** March 30, 2026
