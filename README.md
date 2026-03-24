# VibeShop Assistant Demo

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

```
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

