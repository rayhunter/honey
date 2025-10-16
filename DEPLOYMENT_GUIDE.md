# 🚀 Deployment Guide: Simplified Options

## Quick Comparison

| Platform | Complexity | Cost | Docker Support | Auto-Deploy | Cold Starts | Best For |
|----------|-----------|------|----------------|-------------|-------------|----------|
| **Railway** | ⭐ Easiest | $5/mo | ✅ Native | ✅ | ❌ None | **Recommended** |
| **Render** | ⭐⭐ Easy | Free* | ✅ Native | ✅ | ⚠️ Yes (free) | Budget-conscious |
| **Fly.io** | ⭐⭐⭐ Medium | $5/mo | ✅ Native | ✅ | ❌ None | Performance |
| **DigitalOcean** | ⭐⭐⭐⭐ Complex | $12/mo | ✅ Manual | ❌ | ❌ None | Full control |
| **Cloudflare Pages** | ⭐⭐⭐⭐⭐ | N/A | ❌ No Docker | - | - | ❌ Won't work |

*Free tier has limitations

---

## 🏆 Recommended: Railway

### Why Railway?

1. **Dead Simple Setup** (< 30 minutes)
   - Connect GitHub repo
   - Auto-detects Docker
   - One-click deploy

2. **Zero Configuration**
   - No YAML files needed
   - Environment variables in UI
   - Auto-SSL for custom domains

3. **Great Developer Experience**
   - Real-time logs
   - Instant rollbacks
   - Preview deployments for PRs

4. **Affordable**
   - $5 credit/month (free)
   - Pay only for what you use
   - ~$5-10/month for both services

### Railway Setup (Quick Start)

```bash
# 1. Push your code to GitHub
git add .
git commit -m "Prepare for deployment"
git push origin main

# 2. Go to railway.app and:
#    - Click "Start a New Project"
#    - Select "Deploy from GitHub repo"
#    - Choose your repo
#    - Add two services:
#      a) omdb-mcp-server (from ./omdb-mcp-server)
#      b) streamlit-app (from root with Dockerfile.streamlit)

# 3. Set environment variables in Railway UI:
#    MCP Server:
#      OMDB_API_KEY=your_key
#    
#    Streamlit:
#      OPENAI_API_KEY=your_key
#      TMDB_API_KEY=your_key
#      MCP_SERVER_URL=https://[mcp-service-url].railway.app

# 4. Add custom domain:
#    - In Streamlit service → Settings → Domains
#    - Add "honey.likesugar.ai"
#    - Copy the CNAME target

# 5. Configure Cloudflare DNS:
#    - Type: CNAME
#    - Name: honey
#    - Target: [from Railway]
#    - Proxy: ON
```

**Done!** 🎉 Your app is live at `https://honey.likesugar.ai`

[Full Railway Guide →](./DEPLOYMENT_RAILWAY.md)

---

## 🆓 Budget Option: Render

### Pros:
- Free tier (750 hours/month per service)
- Easy setup with `render.yaml`
- Good for personal projects

### Cons:
- ⚠️ **Sleeps after 15 min inactivity** (30s cold start)
- Limited resources on free tier
- Can be slow

### When to use:
- Personal projects
- Low traffic
- Budget is $0

[Full Render Guide →](./DEPLOYMENT_RENDER.md)

---

## ⚡ Performance Option: Fly.io

### Pros:
- Extremely fast (edge deployment)
- Great for global users
- Docker native

### Cons:
- Steeper learning curve
- CLI-first (less UI)
- More expensive ($10-20/month)

### Setup:
```bash
# Install Fly CLI
brew install flyctl

# Login
flyctl auth login

# Create apps
cd omdb-mcp-server
flyctl launch --name honey-mcp

cd ..
flyctl launch --name honey-app

# Deploy
flyctl deploy
```

---

## 🔧 Self-Hosted Option

If you have your own VPS (DigitalOcean, AWS, etc.):

### 1. Clone repo on server
```bash
ssh user@your-server
git clone https://github.com/your-username/honey.git
cd honey
```

### 2. Create .env file
```bash
cat > .env << EOF
OMDB_API_KEY=your_key
OPENAI_API_KEY=your_key
TMDB_API_KEY=your_key
EOF
```

### 3. Deploy with Docker Compose
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Setup Nginx reverse proxy
```nginx
server {
    listen 80;
    server_name honey.likesugar.ai;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

### 5. Configure Cloudflare DNS
Point `honey` CNAME to your server's IP.

---

## 🎯 Decision Tree

**Choose Railway if:**
- ✅ You want the easiest setup
- ✅ You're okay spending $5-10/month
- ✅ You value simplicity over control

**Choose Render if:**
- ✅ You need a free tier
- ✅ You can tolerate cold starts
- ✅ You have low traffic

**Choose Fly.io if:**
- ✅ You need global performance
- ✅ You're comfortable with CLI tools
- ✅ You have users worldwide

**Choose Self-Hosted if:**
- ✅ You already have a VPS
- ✅ You want full control
- ✅ You're comfortable with server admin

---

## 📊 Cost Breakdown

### Railway (Recommended)
```
MCP Server:  $3-5/month
Streamlit:   $2-3/month
Total:       $5-8/month
```

### Render
```
Free Tier:   $0 (with cold starts)
Paid:        $14/month ($7 per service)
```

### Fly.io
```
MCP Server:  $5-8/month
Streamlit:   $5-8/month
Total:       $10-16/month
```

### Self-Hosted (DigitalOcean Droplet)
```
Server:      $12/month (2GB RAM)
Domain:      Already owned
Total:       $12/month
```

---

## 🚦 Next Steps

### For Railway (Recommended):

1. ✅ Review [DEPLOYMENT_RAILWAY.md](./DEPLOYMENT_RAILWAY.md)
2. ✅ Push code to GitHub
3. ✅ Create Railway account
4. ✅ Deploy both services
5. ✅ Configure custom domain
6. ✅ Test at `https://honey.likesugar.ai`

**Time: ~30 minutes**

### For any platform:

1. Ensure these files exist:
   - ✅ `Dockerfile.streamlit` (created)
   - ✅ `docker-compose.prod.yml` (created)
   - ✅ `requirements.txt` (exists)
   - ✅ `.dockerignore` (recommended)

2. Set up environment variables (never commit secrets!)

3. Test locally first:
   ```bash
   docker-compose -f docker-compose.prod.yml up
   ```

4. Deploy to your chosen platform

5. Configure Cloudflare DNS

---

## 🔒 Security Checklist

Before deploying:

- [ ] Remove all hardcoded API keys
- [ ] Add `.streamlit/secrets.toml` to `.gitignore`
- [ ] Use environment variables for all secrets
- [ ] Enable Cloudflare's security features:
  - [ ] SSL/TLS (Full Strict mode)
  - [ ] WAF
  - [ ] DDoS protection
  - [ ] Rate limiting (optional)
- [ ] Set up proper CORS if needed
- [ ] Enable Railway/Render/Fly security features

---

## 📞 Support

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Fly.io Docs: https://fly.io/docs
- Cloudflare DNS: https://developers.cloudflare.com/dns

---

## 🎬 Summary

**Simplest Path to `https://honey.likesugar.ai`:**

1. Use Railway (30 min setup)
2. Keep MCP server (you've already built it!)
3. Auto-deploys on git push
4. ~$5-8/month
5. Zero server management

**Deploy now:** Follow [DEPLOYMENT_RAILWAY.md](./DEPLOYMENT_RAILWAY.md)

