# VibeShop Setup - Next Steps

## Current Status ✅

- **Portal UI:** Running at `http://127.0.0.1:8000/portal/` ✓
- **API Server:** Running at `http://127.0.0.1:8000/` ✓  
- **Database:** ❌ Not configured (PostgreSQL needed)

---

## What You Need to Do

### Step 1: Set Up PostgreSQL Database

**You have 3 options:**

#### **Option A: PostgreSQL Binary Installer (Easiest for Windows)** ⭐
1. Download: https://www.postgresql.org/download/windows/
2. Run installer (port 5432, password for `postgres` user)
3. Remember the password!

#### **Option B: PostgreSQL via WSL2**
```bash
wsl --install
sudo apt install postgresql postgresql-contrib
sudo service postgresql start
```

#### **Option C: PostgreSQL via Docker**
```powershell
docker run --name vibeshop-postgres \
  -e POSTGRES_PASSWORD=vibeshop_password \
  -p 5432:5432 \
  -d postgres:15
```

---

### Step 2: Create `.env` Configuration File

Create a file named `.env` in the project root:

```
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vibeshop
DB_USER=postgres
DB_PASSWORD=your_password_here

# Optional: Google Cloud (for AI embeddings)
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_REGION=us-central1
```

**Replace `your_password_here` with the password you set during PostgreSQL installation.**

---

### Step 3: Initialize Database Schema

```powershell
# Connect to PostgreSQL and create database
psql -U postgres -c "CREATE DATABASE vibeshop;"

# Create tables and extensions
psql -U postgres -d vibeshop -f database/schema.sql
```

Or use Python:
```powershell
cd c:\Users\USER\Downloads\VibeShop-Assistant-demo
.\venv\Scripts\python.exe database/seed_demo.py
```

---

### Step 4: Test Database Connection

```powershell
cd c:\Users\USER\Downloads\VibeShop-Assistant-demo
.\venv\Scripts\python.exe -c "
from api.db_utils import get_connection
try:
    conn = get_connection()
    print('✓ Database connected successfully!')
except Exception as e:
    print(f'✗ Connection failed: {e}')
"
```

---

### Step 5: Restart Server and Test Portal

```powershell
# Server should already be running, or start it:
cd c:\Users\USER\Downloads\VibeShop-Assistant-demo
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

Then:
1. Open `http://127.0.0.1:8000/portal/`
2. Try creating a store
3. Upload a product with an image
4. See your products appear in the list

---

## Quick Reference Document

See **DATABASE_SETUP.md** in the project root for detailed setup instructions.

---

## What Works in Portal Right Now

✅ **Portal UI loads** — Beautiful, responsive interface  
✅ **API server running** — All endpoints ready  
✅ **Error handling** — Clear messages when database is missing  
❌ **Store creation** — Needs PostgreSQL  
❌ **Product upload** — Needs PostgreSQL  
❌ **Product listing** — Needs PostgreSQL  

---

## Timeline to Full System

- **After PostgreSQL setup (5 min):** Portal will be fully functional
- **After adding .env (1 min):** Database connection established
- **After schema init (1 min):** Tables created, ready for data

**Total time: ~7 minutes** to have a fully working system!

---

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| "Connection refused" | PostgreSQL not running |
| "command not found: psql" | PostgreSQL not installed |
| "Authentication failed" | Wrong password in `.env` |
| "Database does not exist" | Run database/schema.sql |

---

## Once Database is Ready...

You can:
1. ✅ Sellers create stores in the portal
2. ✅ Upload products with images
3. ✅ AI generates embeddings automatically
4. ✅ Customer searches via WhatsApp find products
5. ✅ Transactions are recorded with commission tracking

---

**Next Step:** Install PostgreSQL from one of the 3 options above, then come back here!

Questions? Check:
- `DATABASE_SETUP.md` — Database configuration guide
- `PORTAL_DOCS.md` — Portal functionality documentation  
- `ARCHITECTURE.md` — System architecture details
