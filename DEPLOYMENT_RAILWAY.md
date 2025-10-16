# Deploy to Railway + Cloudflare DNS

## Overview
Deploy the Honey Movie Recommender to Railway and point your Cloudflare subdomain to it.

## Prerequisites
- GitHub account with your `honey` repo pushed
- Railway account (free tier available): https://railway.app
- Cloudflare account with `likesugar.ai` domain

---

## Step 1: Prepare Your Project

### 1.1 Create a Railway-compatible structure

Create `railway.json` in project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "streamlit run movie_recommender.py --server.port=$PORT --server.address=0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 1.2 Create a unified Dockerfile

Create `Dockerfile.streamlit` for the Streamlit app:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY movie_recommender.py .
COPY style/ style/
COPY .streamlit/ .streamlit/

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["streamlit", "run", "movie_recommender.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### 1.3 Update requirements.txt

Ensure all dependencies are listed:

```txt
streamlit>=1.28.0
openai>=1.3.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## Step 2: Deploy to Railway

### 2.1 Create Railway Project

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select the `honey` repository

### 2.2 Deploy MCP Server

1. Click "New Service" → "Docker Image"
2. Choose the `omdb-mcp-server` directory
3. Set environment variables:
   - `OMDB_API_KEY`: Your OMDB API key
   - `SERVER_PORT`: 8081
4. Deploy
5. Railway will assign a URL like: `omdb-mcp-server.railway.app`

### 2.3 Deploy Streamlit App

1. Click "New Service"
2. Select root path: `/` (root directory)
3. Under Settings → Build, set:
   - **Builder**: Dockerfile
   - **Dockerfile Path**: Dockerfile.streamlit
4. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI key
   - `TMDB_API_KEY`: Your TMDB key
   - `MCP_SERVER_URL`: `https://omdb-mcp-server.railway.app` (from step 2.2)
5. Deploy
6. Railway will assign a URL like: `honey.railway.app`

---

## Step 3: Configure Cloudflare DNS

### 3.1 Get Railway URL

1. In Railway, go to your Streamlit service
2. Click "Settings" → "Domains"
3. Copy the Railway domain (e.g., `honey-production.up.railway.app`)

### 3.2 Add Custom Domain in Railway

1. In Railway domain settings, click "Custom Domain"
2. Enter `honey.likesugar.ai`
3. Railway will show you DNS records to add

### 3.3 Configure Cloudflare

1. Log into Cloudflare dashboard
2. Select `likesugar.ai` domain
3. Go to DNS → Records
4. Add a CNAME record:
   - **Type**: CNAME
   - **Name**: honey
   - **Target**: `honey-production.up.railway.app` (your Railway domain)
   - **Proxy status**: Proxied (orange cloud)
   - **TTL**: Auto

### 3.4 Wait for Propagation

- DNS changes take 5-60 minutes
- Check status: `dig honey.likesugar.ai`
- Or use: https://dnschecker.org

---

## Step 4: Configure SSL (Automatic)

Railway + Cloudflare automatically handle SSL:
- Railway provides SSL certificate
- Cloudflare provides additional SSL/TLS encryption
- Your site will be accessible via `https://honey.likesugar.ai`

---

## Step 5: Update Secrets

### 5.1 Railway Environment Variables

In Railway dashboard for Streamlit service:

```bash
OPENAI_API_KEY=sk-...
TMDB_API_KEY=...
MCP_SERVER_URL=https://omdb-mcp-server.railway.app
OMDB_API_KEY=...  # Only if calling OMDB directly
```

### 5.2 Remove .streamlit/secrets.toml from Git

Add to `.gitignore`:

```
.streamlit/secrets.toml
```

Railway will use environment variables instead.

---

## Cost Estimate

**Railway Free Tier:**
- $5 of usage credit per month
- Both services should fit within free tier for moderate usage

**If you exceed free tier:**
- ~$5-10/month for both services
- Much cheaper than VPS hosting

---

## Deployment Commands

### Push updates:

```bash
git add .
git commit -m "Update app"
git push origin main
```

Railway auto-deploys on push to `main` branch.

### Manual deploy:

In Railway dashboard:
1. Go to service
2. Click "Deploy"
3. Select "Deploy Latest"

---

## Monitoring

### Logs:
1. Railway dashboard → Select service → "Logs" tab
2. Real-time streaming logs

### Health checks:
- Streamlit: `https://honey.likesugar.ai/_stcore/health`
- MCP Server: `https://omdb-mcp-server.railway.app/actuator/health`

---

## Troubleshooting

### App not loading:
```bash
# Check Railway logs
# Ensure environment variables are set
# Verify MCP_SERVER_URL points to correct Railway URL
```

### DNS not resolving:
```bash
# Check Cloudflare DNS settings
# Ensure CNAME is "Proxied" (orange cloud)
# Wait 5-60 minutes for propagation
```

### MCP server timeout:
```bash
# Check Railway logs for MCP service
# Verify OMDB_API_KEY is set
# Check network connection between services
```

---

## Alternative: Single Container Approach

If you want even simpler deployment, you can run both services in one container using Docker Compose on Railway.

Create `railway.toml`:

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile.combined"

[deploy]
startCommand = "docker-compose up"
```

This runs the entire stack as one Railway service.

---

## Security Notes

1. **Never commit secrets** to Git
2. Use Railway environment variables for all API keys
3. Enable Cloudflare's security features:
   - WAF (Web Application Firewall)
   - DDoS protection
   - Rate limiting

---

## Conclusion

Once deployed:
- ✅ Auto-deploys on git push
- ✅ Auto-SSL via Railway + Cloudflare
- ✅ Custom domain: `https://honey.likesugar.ai`
- ✅ Auto-scaling
- ✅ Built-in monitoring
- ✅ Zero server management

Total setup time: ~30 minutes

