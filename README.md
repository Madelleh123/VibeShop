# VibeShop Assistant - AI-Powered Commerce Platform for African Markets

## 🎯 Platform Overview

VibeShop is a **WhatsApp-first AI commerce platform** designed for local market sellers in Africa. Customers find products through image search on WhatsApp, sellers manage inventory through a simple web portal.

### Key Features
- 🛍️ **Seller Portal** — Create stores, manage products, upload images
- 🤳 **WhatsApp Integration** — Customers search and purchase via WhatsApp
- 🔍 **AI Image Search** — Powered by Vertex AI embeddings + pgvector
- 💳 **Payment Processing** — USSD payment support with commission tracking
- 🏪 **Multi-Store Support** — Many sellers, unified search index

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- (Optional) Google Cloud Vertex AI credentials

### 1. Clone & Setup

```bash
cd c:\Users\USER\Downloads\VibeShop-Assistant-demo

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies (already done)
pip install -r requirements.txt
```

### 2. Configure Database

**See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed PostgreSQL setup** ⭐

```bash
# Quick setup (after PostgreSQL is installed):
psql -U postgres -c "CREATE DATABASE vibeshop;"
psql -U postgres -d vibeshop -f database/schema.sql
```

### 3. Create `.env` File

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vibeshop
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### 4. Start Server

```bash
python -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### 5. Open Portal

Visit: **http://127.0.0.1:8000/portal/**

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** | PostgreSQL setup & getting started |
| **[DATABASE_SETUP.md](DATABASE_SETUP.md)** | Detailed database configuration |
| **[PORTAL_DOCS.md](PORTAL_DOCS.md)** | Seller portal & API reference |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design & data flow |

---

## 🏗️ System Architecture

```
┌─ SELLER PORTAL ─┐         ┌─ WHATSAPP BOT ─┐
│ (Web UI)        │         │ (Customer)     │
│ • Create Store  │◄────►   │ • Search Image │
│ • Add Products  │ API     │ • View Results │
│ • Manage Inv.   │         │ • Purchase     │
└─────────────────┘         └────────────────┘
        │                            │
        └────────┬─────────┬─────────┘
                 │         │
        ┌────────▼──────────▼────────┐
        │  FastAPI Backend           │
        │ (/api/portal endpoints)    │
        └────────┬────────────────────┘
                 │
        ┌────────▼──────────────────┐
        │ PostgreSQL + pgvector     │
        │ • Stores                  │
        │ • Products (with vectors) │
        │ • Transactions            │
        └────────┬──────────────────┘
                 │
        ┌────────▼──────────────────┐
        │ Vertex AI Models          │
        │ • Image Embeddings (1408) │
        │ • Text Embeddings (768)   │
        └───────────────────────────┘
```

---

## 🎮 Portal Features

### Store Creation
```
1. Seller enters: name, WhatsApp phone, location
2. System generates unique store_id
3. Seller auto-redirected to product upload
```

### Product Management
```
1. Upload product: name, price, description, image
2. Image source: Local file OR URL
3. Auto-generates AI embeddings
4. View/delete products in grid layout
5. Switch between stores
```

### Data Flow
```
Product Upload
    ↓ (image bytes)
Vertex AI Multimodal
    ↓ (1408-dim vector)
pgvector in PostgreSQL
    ↓ (stored with product)
Customer Search
    ↓ (image similarity)
Top 3 Results
    ↓ (customer purchases)
Transaction recorded
    ↓ (commission split)
Seller notified
```

---

## 🔌 API Endpoints

### Portal API (`/api/portal/`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/create-store` | Create new store |
| `POST` | `/upload-product` | Add product with image |
| `GET` | `/products?store_id=X` | List products |
| `POST` | `/delete-product` | Remove product |

### WhatsApp Webhook (`/webhook`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/webhook` | Handle WhatsApp messages |

---

## 📊 Database Schema

### `stores`
```sql
store_id (PK)
├─ name
├─ phone_number (WhatsApp)
├─ location
└─ market (category)
```

### `products`
```sql
product_id (PK)
├─ store_id (FK)
├─ name
├─ description
├─ price
├─ image_url
└─ image_embedding (pgvector 1408-dim)
```

### `transactions`
```sql
id (PK)
├─ product_id (FK)
├─ store_id (FK)
├─ buyer_phone
├─ amount
├─ commission (%)
└─ seller_amount = amount - commission
```

---

## 🚨 Current Status

✅ **Portal UI** — Fully functional  
✅ **API Endpoints** — All implemented  
✅ **Embeddings Pipeline** — Ready (Vertex AI lazy-loaded)  
⏳ **Database** — **Requires PostgreSQL setup** (see SETUP_INSTRUCTIONS.md)

---

## 🛠️ Development

### Run Tests
```bash
cd tests/
pytest
```

### Run Linter
```bash
pylint api/*.py
```

### Run with Live Reload
```bash
python -m uvicorn api.main:app --reload
```

---

## 🌍 Deployment

### Local Development
```bash
python -m uvicorn api.main:app --reload
```

### Production (via Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 api.main:app
```

### Docker
```bash
docker build -t vibeshop .
docker run -p 8000:8000 vibeshop
```

---

## 🔐 Security

### Current State
- No authentication (portal is open)
- Local database connection

### Production Recommendations
- Add seller authentication (OAuth/JWT)
- Use HTTPS/TLS
- Implement rate limiting
- Add CORS restrictions
- Use secrets manager for credentials
- Enable SQL query logging

---

## 📞 Support & Troubleshooting

### Portal won't load?
- Check if server is running: `http://127.0.0.1:8000/`
- Check browser console for errors (F12)

### Store creation fails?
- Database not running (see SETUP_INSTRUCTIONS.md)
- Invalid `.env` configuration
- Check server logs for details

### Product upload fails?
- Database connection issue
- Image file too large
- Vertex AI credentials not set

### See Also
- [DATABASE_SETUP.md](DATABASE_SETUP.md) — Database troubleshooting
- [PORTAL_DOCS.md](PORTAL_DOCS.md) — API troubleshooting
- [ARCHITECTURE.md](ARCHITECTURE.md) — System troubleshooting

---

## 🗺️ Project Structure

```
VibeShop-Assistant-demo/
├── api/                      # FastAPI backend
│   ├── main.py              # Main app & endpoints
│   ├── embedding_logic.py   # Text embeddings
│   ├── image_embedding_logic.py # Image embeddings
│   ├── search_logic.py      # Vector search
│   ├── db_utils.py          # Database utilities
│   ├── payment_logic.py     # Payment processing
│   └── config.py            # Configuration
│
├── portal/                   # Seller portal UI
│   ├── index.html           # Portal page
│   └── app.js               # Portal logic
│
├── database/                # Database setup
│   ├── schema.sql           # Table definitions
│   └── seed_demo.py         # Demo data script
│
├── ussd/                    # USSD payment provider
│   └── provider.py          # Payment integration
│
├── docs/                    # Documentation
│   ├── SETUP_INSTRUCTIONS.md
│   ├── DATABASE_SETUP.md
│   ├── PORTAL_DOCS.md
│   └── ARCHITECTURE.md
│
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
└── README.md               # This file
```

---

## 🗣️ Languages & Stack

### Backend
- **Python 3.11** — FastAPI web framework
- **PostgreSQL 13+** — Relational database
- **pgvector** — Vector similarity search
- **Vertex AI** — Image & text embeddings

### Frontend
- **HTML5** — Responsive portal UI
- **CSS3** — Material Design styling  
- **JavaScript (ES6)** — Interactive forms

### Infrastructure
- **Uvicorn** — ASGI server
- **Psycopg2** — PostgreSQL connector
- **Requests** — HTTP client
- **python-dotenv** — Configuration management

---

## 📝 Next Steps

1. **Set up PostgreSQL** (see SETUP_INSTRUCTIONS.md)
2. **Create `.env` file** with database credentials
3. **Initialize database schema** (schema.sql)
4. **Start the server** (uvicorn)
5. **Open the portal** (http://127.0.0.1:8000/portal/)
6. **Create a store** and upload test products
7. **Test WhatsApp webhook** image search flow

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙋 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

**Made for African Market Sellers • Powered by AI • Connected via WhatsApp**

[Twitter](https://twitter.com/vibeshop) | [GitHub](https://github.com/vibeshop) | [Docs](PORTAL_DOCS.md)

Last Updated: March 31, 2026
 Assistant Demo

AI-powered WhatsApp shopping assistant for African markets (Owino Market demo).

## Project Description

This repository implements a demo backend for image-based product recommendations using:

- FastAPI for HTTP endpoints
- PostgreSQL with pgvector for embedding similarity search
- Google Vertex AI for text and image embeddings (`textembedding-gecko@003`, `multimodalembedding@001`)
- Gemini (`gemini-1.5-flash`) for optional image visual description

Users upload a clothing photo to `/webhook`, then the server computes an image embedding, retrieves nearest products by vector similarity, and returns recommendations.

## Key components

- `api/main.py`: FastAPI app and `/webhook` image ingest endpoint
- `api/search_logic.py`: database search logic, vector similarity, cosine distance threshold
- `api/embedding_logic.py`: text embedding utilities with Vertex AI
- `api/image_embedding_logic.py`: image embedding utilities with Vertex AI
- `api/vision_logic.py`: Gemini vision-to-JSON description helper (optional)
- `database/schema.sql`: PostgreSQL schema (stores, products, vectors)
- `database/seed_demo.py`: seed script for stores/products + embeddings
- `ussd/provider.py`: placeholder payment trigger stub (simulated)

## Requirements

- Python 3.11+ (Python 3.10 might work)
- PostgreSQL with `pgvector` extension
- Google Cloud credentials and project setup for Vertex AI
- Gemini API key

## Env setup

Create `.env` with values:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_pwd
GOOGLE_PROJECT_ID=your_gcp_project
GOOGLE_REGION=us-central1
GEMINI_API_KEY=your_gemini_key
```

## Database

SQL schema is in `database/schema.sql`. Ensure extension and table definitions are valid.

Run:

```bash
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f database/schema.sql
```

## Seed data

```bash
python database/seed_demo.py
```

## Run app

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

## API

`POST /webhook` with multipart image file (key: `file`).

Response: message and top 3 matched products.

## Notes

- `database/schema.sql` currently has malformed SQL and should be fixed manually:
  - `stores` table definition closes early
  - `products` table duplicate statement pattern
  - `vector` dimensions must match model output (image 1408, text 768)

- `api/vision_logic.py` uses Gemini and may require additional error handling in production.

