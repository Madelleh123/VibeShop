# VibeShop Render Deployment Guide

> **Note**: This project uses **FastAPI** (not Flask) with **PostgreSQL**, deployed via **Render**.

---

## 📋 Quick Checklist

- ✅ Code is on GitHub
- ✅ `requirements.txt` is production-ready
- ✅ `Procfile` configured for Render
- ✅ Database connection uses environment variables
- ✅ `.env.example` provides template for Render

---

## 🚀 Deployment Steps

### Step 1: Push Code to GitHub

Ensure your latest code is pushed:

```bash
git add -A
git commit -m "Prepare for Render deployment"
git push origin main
```

Verify on GitHub: https://github.com/Madelleh123/VibeShop

### Step 2: Create Render Services

#### 2A: Create Web Service

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Deploy an existing repository"**
4. Connect GitHub and select `Madelleh123/VibeShop`
5. Click **"Connect"**

**Configure:**

| Setting | Value |
|---------|-------|
| **Name** | `vibeshop-portal` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` (can upgrade) |

#### 2B: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. **Name:** `vibeshop-db`
3. **Database:** `vibeshop_db`
4. **User:** `postgres`
5. **Region:** Same as web service (e.g., `Oregon`)
6. **Instance Type:** `Free` (can upgrade)
7. Click **"Create Database"**

**⏱️ Wait 2-3 minutes for database provisioning**

### Step 3: Connect Database to Web Service

After database is provisioned:

1. In web service settings, go to **"Environment"**
2. Click **"Add Environment Variable"** for each:

   | Key | Value |
   |-----|-------|
   | `DB_HOST` | Paste from postgres service |
   | `DB_PORT` | `5432` |
   | `DB_NAME` | `vibeshop_db` |
   | `DB_USER` | `postgres` |
   | `DB_PASSWORD` | Paste from postgres service |
   | `APP_ENV` | `production` |
   | `APP_DEBUG` | `false` |

**Where to find database credentials:**
- Go to PostgreSQL service
- Click **"Info"** tab
- Copy connection details

### Step 4: Initialize Database Schema

After both services are deployed and connected:

**Option A: Using One-off Job (Recommended)**

1. In Render dashboard, create a **"One-off Job"**
2. **Command:**
   ```bash
   psql $DATABASE_URL -f database/schema.sql
   ```
3. Run the job

**Option B: Manual via psql**

```bash
# Get DATABASE_URL from your PostgreSQL service
psql postgresql://user:password@host:port/vibeshop_db -f database/schema.sql
```

### Step 5: Deploy

The web service should auto-deploy once created. Monitor:

1. Go to web service → **"Logs"** tab
2. Watch for build and startup messages
3. Should see: `Application startup complete`

**Your app is now live at:**
```
https://vibeshop-portal.onrender.com
```

**Test it:**
- Portal: https://vibeshop-portal.onrender.com/portal/
- API health: https://vibeshop-portal.onrender.com/

---

## 📁 Project Structure

```
vibeshop/
├── api/
│   ├── main.py                 # FastAPI app (entry point)
│   ├── db_utils.py            # Database connection
│   ├── config.py              # Configuration
│   └── ...
├── database/
│   ├── schema.sql             # PostgreSQL schema
│   └── seed_demo.py           # Demo data
├── portal/
│   ├── app.js                 # Frontend logic
│   ├── index.html             # Frontend UI
├── requirements.txt           # Production dependencies
├── Procfile                   # Render startup command
├── render.yaml                # Render infrastructure (optional)
└── .env.example               # Environment template
```

---

## 🔑 Environment Variables Explained

### Database Connection (Required)

Choose ONE option:

**Option 1: DATABASE_URL** (recommended for Render)
```
DATABASE_URL=postgresql://user:password@host:port/dbname
```

**Option 2: Individual variables**
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=vibeshop_db
DB_USER=postgres
DB_PASSWORD=secure_password
```

### Application Settings

```
APP_ENV=production        # "production" or "development"
APP_DEBUG=false          # Set to "true" only for debugging
```

### Optional Services

```
GOOGLE_PROJECT_ID=       # For AI embeddings (optional)
TWILIO_ACCOUNT_SID=      # For WhatsApp (optional)
USSD_API_KEY=            # For mobile payments (optional)
```

---

## ⚠️ Common Deployment Issues

### Issue: "Could not connect to database"

**Cause:** PostgreSQL not fully provisioned yet

**Fix:**
1. Wait another minute
2. Check PostgreSQL service status in Render
3. Verify environment variables are correct
4. Try redeploying web service

### Issue: "Build failed - missing dependencies"

**Cause:** Old `requirements.txt` with wrong packages

**Fix:**
1. Ensure `requirements.txt` contains only production deps
2. Check Python version (should be 3.11+)
3. Redeploy: Render dashboard → Web service → Manual deploy

### Issue: "Application startup complete" but site shows error

**Cause:** Database schema not initialized

**Fix:**
1. Create One-off Job with schema migration
2. Or manually run: `psql $DATABASE_URL -f database/schema.sql`
3. Redeploy web service

### Issue: "Disallowed Host" or "Bad Gateway"

**Cause:** CORS or routing issue

**Fix:**
1. Check Render logs for specific error
2. Verify FastAPI is binding to `0.0.0.0`
3. Ensure PORT env var is respected

---

## 🔒 Security Best Practices

### Secrets Management

✅ **DO:**
- Store all passwords in Render environment variables
- Use strong, random PostgreSQL passwords
- Rotate secrets monthly
- Never commit `.env` with real values

❌ **DON'T:**
- Hardcode credentials in code
- Commit `.env` to Git
- Use same password for multiple services
- Share credentials in logs

### Database Security

```python
# ✅ GOOD - Uses environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")
conn = psycopg2.connect(
    host=DB_HOST,
    password=DB_PASSWORD,
    ...
)

# ❌ BAD - Hardcoded credentials
conn = psycopg2.connect(
    host="localhost",
    password="secret123",
    ...
)
```

---

## 📈 Scaling & Upgrades

As your app grows:

### Free to Paid Tier

| Tier | Cost/mo | CPU | RAM | Benefits |
|------|---------|-----|-----|----------|
| Free | $0 | Shared | 512MB | Development, demos |
| Starter | ~$7 | 0.5 | 512MB | Production-ready |
| Standard | ~$20+ | 1+ | 2GB+ | High traffic |

### Upgrade Steps

1. Go to web service settings
2. Scroll to **"Plan"**
3. Change from **"Free"** to **"Starter"** (or higher)
4. Service will restart with more resources

---

## 🧪 Post-Deployment Testing

Once deployed:

```bash
# 1. Test root endpoint
curl https://vibeshop-portal.onrender.com/

# 2. Test portal loads
curl -L https://vibeshop-portal.onrender.com/portal/

# 3. Create a test store via API
curl -X POST https://vibeshop-portal.onrender.com/api/portal/create-store \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Store",
    "phone_number": "+256700000000",
    "location": "Kampala"
  }'

# 4. Check database connection
# (Logs should show no connection errors)
```

---

## 🚨 Monitoring & Logs

### View Logs

1. Render dashboard → Web service
2. Click **"Logs"** tab
3. Real-time output

### Common Log Messages

```
✅ "Application startup complete"
   → App is running successfully

❌ "connection refused"
   → Database not available

⚠️ "health check failed"
   → App might be crashing
```

### Set Up Alerts (Optional)

1. Go to service settings
2. **"Notifications"** tab
3. Enable email/Slack alerts for deploy events

---

## 📝 Summary

| Component | Status | Location |
|-----------|--------|----------|
| Web App | FastAPI | `api/main.py` |
| Database | PostgreSQL | Render managed |
| Portal | HTML/JS | `portal/app.js` |
| Procfile | ✅ Configured | `Procfile` |
| Env Template | ✅ Ready | `.env.example` |
| Dependencies | ✅ Production-ready | `requirements.txt` |

**Next Steps:**
1. ✅ Push to GitHub
2. ✅ Create Render services
3. ✅ Set environment variables
4. ✅ Initialize database
5. ✅ Test the deployment
6. ✅ Monitor logs

---

## 📚 Resources

- [Render Docs](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL on Render](https://render.com/docs/databases)
- [VibeShop GitHub](https://github.com/Madelleh123/VibeShop)

---

**Questions?** Check the main [README.md](./README.md) or [QUICK_START.md](./QUICK_START.md)
