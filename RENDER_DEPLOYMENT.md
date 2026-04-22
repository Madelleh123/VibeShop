# Deploy VibeShop to Render

This guide shows how to deploy the VibeShop FastAPI application and PostgreSQL database to Render.

## Prerequisites

1. **GitHub Account** - Render connects to your GitHub repository
2. **Render Account** - Sign up at https://render.com
3. **Git Push** - Ensure your code is pushed to GitHub

## Deployment Steps

### Step 1: Push to GitHub

First, ensure your latest code is pushed:

```bash
git add -A
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Connect to Render

1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Select **"Deploy an existing repository"**
4. Connect your GitHub account if not already connected
5. Select repository: `Madelleh123/VibeShop`
6. Click **"Connect"**

### Step 3: Configure Web Service

**Name:** `vibeshop-portal`

**Root Directory:** (leave blank)

**Environment:** `Python 3`

**Build Command:** 
```bash
pip install -r requirements.txt
```

**Start Command:** 
```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:** Free (to start)

**Advanced Settings:**
- Add Environment Variables:
  ```
  APP_ENV = production
  APP_DEBUG = false
  GOOGLE_PROJECT_ID = (leave empty for now)
  GOOGLE_REGION = us-central1
  ```

### Step 4: Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name:** `vibeshop-db`
3. **Database:** `vibeshop_db`
4. **User:** `postgres` (default)
5. **Region:** Select same as web service
6. **Instance Type:** Free (to start)
7. Click **"Create Database"**

### Step 5: Connect Database to Web Service

1. Go back to your web service settings
2. Click **"Environment"** → **"Add Environment Variable"**
3. Add the database connection variables:

   | Key | Value |
   |-----|-------|
   | `DB_HOST` | Copy from database settings |
   | `DB_PORT` | `5432` |
   | `DB_NAME` | `vibeshop_db` |
   | `DB_USER` | `postgres` |
   | `DB_PASSWORD` | Copy from database settings |

### Step 6: Initialize Database Schema

After both services are deployed:

1. Get the database connection string from your PostgreSQL service
2. Run migrations manually or use a one-time job:

   ```bash
   psql <connection_string> -f database/schema.sql
   ```

   Or in Render, create a **One-off Job**:
   - Command: `psql $DATABASE_URL -f database/schema.sql`
   - Add the `$DATABASE_URL` environment variable

### Step 7: Deploy

1. Your web service should automatically deploy when you create it
2. Monitor the **Logs** tab for build errors
3. Once deployed, your app will be live at: `https://vibeshop-portal.onrender.com`

## Troubleshooting

### Build Fails

Check the build logs in Render. Common issues:
- Missing dependencies in `requirements.txt`
- Python version mismatch
- PostgreSQL not available yet

### Database Connection Fails

1. Verify database URL environment variables
2. Check that PostgreSQL is fully provisioned (takes ~2-3 minutes)
3. Run the schema migration job

### App Crashes on Startup

1. Check logs for specific errors
2. Verify database connection
3. Ensure all environment variables are set

## Environment Variables Reference

| Variable | Example | Notes |
|----------|---------|-------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `vibeshop_db` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASSWORD` | `xxxxxxxxxxxx` | Database password |
| `APP_ENV` | `production` | Environment type |
| `APP_DEBUG` | `false` | Debug mode |
| `GOOGLE_PROJECT_ID` | (optional) | For AI embeddings |

## Next Steps

After successful deployment:

1. Test the portal: `https://vibeshop-portal.onrender.com/portal/`
2. Create a store and add products
3. Set up custom domain (optional)
4. Monitor performance in Render dashboard

## Scaling

As your app grows:
- Upgrade from Free to Paid instance
- Upgrade PostgreSQL storage
- Add caching (Redis)
- Set up auto-scaling

For production, consider:
- Paid instances for reliability
- Dedicated database
- CDN for static assets
- Error monitoring (Sentry)

---

**Questions?** Check [Render Docs](https://render.com/docs) or see [QUICK_START.md](./QUICK_START.md)
