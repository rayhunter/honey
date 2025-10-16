# Deploy to Render + Cloudflare DNS

## Overview
Deploy to Render (free tier available) with Cloudflare DNS pointing to your custom domain.

## Why Render?
- ✅ Free tier (750 hours/month)
- ✅ Auto-deploy from Git
- ✅ Native Docker support
- ✅ Zero config for most apps
- ✅ Built-in SSL

---

## Step 1: Prepare render.yaml

Create `render.yaml` in project root:

```yaml
services:
  # MCP Server
  - type: web
    name: omdb-mcp-server
    env: docker
    dockerfilePath: ./omdb-mcp-server/Dockerfile
    dockerContext: ./omdb-mcp-server
    envVars:
      - key: OMDB_API_KEY
        sync: false
      - key: SERVER_PORT
        value: 8081
    healthCheckPath: /actuator/health
    
  # Streamlit App
  - type: web
    name: honey-streamlit
    env: docker
    dockerfilePath: ./Dockerfile.streamlit
    dockerContext: .
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: TMDB_API_KEY
        sync: false
      - key: MCP_SERVER_URL
        fromService:
          type: web
          name: omdb-mcp-server
          property: host
    healthCheckPath: /_stcore/health
```

---

## Step 2: Deploy to Render

### 2.1 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repos

### 2.2 Create New Blueprint
1. Click "New +" → "Blueprint"
2. Connect your `honey` repository
3. Render will detect `render.yaml` automatically
4. Click "Apply"

### 2.3 Configure Environment Variables
1. Go to each service in dashboard
2. Add environment variables:

**omdb-mcp-server:**
```
OMDB_API_KEY=your_key_here
```

**honey-streamlit:**
```
OPENAI_API_KEY=sk-...
TMDB_API_KEY=your_key_here
```

### 2.4 Deploy
Render auto-deploys both services in correct order.

---

## Step 3: Configure Custom Domain

### 3.1 Get Render URL
1. Go to `honey-streamlit` service
2. Copy the `.onrender.com` URL
3. Example: `honey-streamlit.onrender.com`

### 3.2 Add Custom Domain in Render
1. In service settings → "Custom Domains"
2. Click "Add Custom Domain"
3. Enter: `honey.likesugar.ai`
4. Render shows CNAME target

### 3.3 Configure Cloudflare DNS
1. Log into Cloudflare
2. Select `likesugar.ai`
3. DNS → Add record:
   - **Type**: CNAME
   - **Name**: honey
   - **Target**: (from Render, e.g., `honey-streamlit.onrender.com`)
   - **Proxy**: ON (orange cloud)

### 3.4 Verify SSL
- Wait 5-10 minutes
- Visit `https://honey.likesugar.ai`
- SSL auto-configured by Render + Cloudflare

---

## Step 4: Monitoring

### Logs
Dashboard → Select service → "Logs"

### Metrics
Dashboard → Select service → "Metrics"
- CPU usage
- Memory
- Request rate
- Response times

---

## Cost

**Free Tier:**
- 750 hours/month per service
- 2 services = good for personal use
- Auto-sleeps after 15 min inactivity

**Paid Tier ($7/month per service):**
- No sleep
- More resources
- Priority support

---

## Pros & Cons

### ✅ Pros:
- Free tier available
- Easy setup
- Auto-deploy on push
- Built-in monitoring

### ❌ Cons:
- Free tier sleeps after inactivity (~30s cold start)
- Limited free tier resources
- Slower than Railway

---

## Auto-Deploy

Push to GitHub = auto-deploy:

```bash
git add .
git commit -m "Update"
git push origin main
```

Render rebuilds and deploys automatically.

