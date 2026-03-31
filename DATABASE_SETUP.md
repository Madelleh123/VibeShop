# PostgreSQL Setup Guide for VibeShop

## Quick Setup Options

### Option A: PostgreSQL via Binary Installer (Windows) ✅ RECOMMENDED

1. **Download PostgreSQL 15 for Windows**
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer"
   - Select version 15 or later

2. **Run Installer**
   - Double-click the downloaded `.exe`
   - Follow the setup wizard
   - **Important settings:**
     - Port: `5432` (default)
     - Password: Set a password for `postgres` user (remember this!)
     - Locale: English

3. **Verify Installation**
   ```powershell
   psql --version
   ```

4. **Create VibeShop Database**
   ```powershell
   # Connect to PostgreSQL
   psql -U postgres
   
   # In psql prompt, run:
   CREATE DATABASE vibeshop;
   \c vibeshop
   
   # Create vector extension (for pgvector)
   CREATE EXTENSION IF NOT EXISTS vector;
   
   # Run schema
   \i database/schema.sql
   
   # Exit
   \q
   ```

---

### Option B: PostgreSQL via WSL2 (Windows Subsystem for Linux)

1. **Install WSL2** (if not already installed)
   ```powershell
   wsl --install
   ```

2. **In WSL terminal, install PostgreSQL**
   ```bash
   sudo apt update
   sudo apt install postgresql postgresql-contrib
   ```

3. **Start PostgreSQL**
   ```bash
   sudo service postgresql start
   ```

4. **Create database** (same as Option A steps 4)

---

### Option C: PostgreSQL via Docker (Requires Docker Desktop)

If you have Docker Desktop installed:

```bash
# Create data directory
mkdir -p ~/vibeshop_db_data

# Run PostgreSQL container
docker run --name vibeshop-postgres \
  -e POSTGRES_PASSWORD=vibeshop_password \
  -e POSTGRES_DB=vibeshop \
  -p 5432:5432 \
  -v ~/vibeshop_db_data:/var/lib/postgresql/data \
  -d postgres:15
```

---

## Configuration

### 1. Create `.env` file in project root

```bash
# === Database ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vibeshop
DB_USER=postgres
DB_PASSWORD=your_password_here

# === Google Cloud / Vertex AI (Optional) ===
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_REGION=us-central1
```

### 2. Update `DB_PASSWORD` with your actual password

---

## Initialize Database Schema

```bash
cd c:\Users\USER\Downloads\VibeShop-Assistant-demo

# Create tables and extensions
psql -U postgres -d vibeshop -f database/schema.sql

# Or use Python to create schema
python database/seed_demo.py
```

---

## Verify Setup

```powershell
# Test connection
cd c:\Users\USER\Downloads\VibeShop-Assistant-demo
.\venv\Scripts\python.exe -c "from api.db_utils import get_connection; conn = get_connection(); print('✓ Database connected!')"
```

---

## Troubleshooting

### ❌ "psql: command not found"
- PostgreSQL not installed or not in PATH
- **Fix:** Install PostgreSQL or add to PATH manually

### ❌ "Connection refused on port 5432"
- PostgreSQL not running
- **Fix:** Start PostgreSQL service
  ```powershell
  # Windows (if installed via installer)
  Get-Service postgresql* | Start-Service
  
  # Or manually start from Services app
  ```

### ❌ "FATAL: password authentication failed"
- Wrong password in `.env`
- **Fix:** Update `.env` with correct password, or reset PostgreSQL password:
  ```bash
  psql -U postgres
  ALTER USER postgres WITH PASSWORD 'new_password';
  ```

### ❌ "pgvector extension not found"
- pgvector not installed
- **Fix:** Install pgvector for PostgreSQL
  ```bash
  # On Windows with PostgreSQL installed:
  # Run PostgreSQL installer again → Choose "pgvector" from extensions
  
  # Or on Linux:
  sudo apt install postgresql-15-pgvector
  sudo systemctl restart postgresql
  ```

---

## Quick Start After Installation

```powershell
# 1. Start PostgreSQL (if not auto-starting)
Get-Service postgresql* | Start-Service

# 2. Activate venv
cd c:\Users\USER\Downloads\VibeShop-Assistant-demo
.\venv\Scripts\Activate.ps1

# 3. Run server
python -m uvicorn api.main:app --reload

# 4. Open portal
Start http://127.0.0.1:8000/portal/
```

---

## Development Database Backup

```bash
# Backup database
pg_dump -U postgres vibeshop > vibeshop_backup.sql

# Restore database
psql -U postgres vibeshop < vibeshop_backup.sql
```

---

**Recommendation:** Use Option A (Binary Installer) for easiest setup on Windows.

After installation, return to the terminal and restart the VibeShop API server. The database will be ready! ✅
