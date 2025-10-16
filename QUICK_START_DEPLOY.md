# 🚀 Quick Start: Deploy in 15 Minutes

## TL;DR

Get `https://honey.likesugar.ai` live in 15 minutes using Railway.

---

## Prerequisites

✅ GitHub account  
✅ Cloudflare account with `likesugar.ai` domain  
✅ Credit card (for Railway, $0 for first month with $5 credit)

---

## Step 1: Push to GitHub (2 min)

```bash
# In your project directory
git add .
git commit -m "Prepare for deployment"
git push origin main
```

---

## Step 2: Deploy to Railway (5 min)

### 2.1 Sign Up
1. Go to https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway

### 2.2 Create Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `honey` repository

### 2.3 Deploy MCP Server
1. Click "Add Service" → "Add Service from GitHub"
2. Select root path: `/omdb-mcp-server`
3. Railway auto-detects Dockerfile
4. Click "Add Variables"
   ```
   OMDB_API_KEY = your_omdb_key_here
   ```
5. Click "Deploy"
6. Wait ~2 minutes for build
7. **Copy the service URL** (click service → Settings → copy domain)
   - Example: `omdb-mcp-server-production.up.railway.app`

### 2.4 Deploy Streamlit App
1. Click "New Service"
2. Select root path: `/` (root directory)
3. Under Settings → Build, set:
   - Builder: Dockerfile
   - Dockerfile Path: `Dockerfile.streamlit`
4. Click "Add Variables"
   ```
   OPENAI_API_KEY = sk-...
   TMDB_API_KEY = your_tmdb_key_here
   MCP_SERVER_URL = https://omdb-mcp-server-production.up.railway.app
   ```
   ⚠️ Use the URL from step 2.3!
5. Click "Deploy"
6. Wait ~3 minutes for build

---

## Step 3: Add Custom Domain (3 min)

### 3.1 In Railway
1. Go to your Streamlit service
2. Click "Settings" → "Domains"
3. Click "Custom Domain"
4. Enter: `honey.likesugar.ai`
5. Railway shows a CNAME target like:
   ```
   honey-production-abc123.up.railway.app
   ```
6. **Copy this URL**

### 3.2 In Cloudflare
1. Go to Cloudflare Dashboard
2. Select `likesugar.ai` domain
3. Click "DNS" → "Add record"
4. Fill in:
   ```
   Type: CNAME
   Name: honey
   Target: honey-production-abc123.up.railway.app (from Railway)
   Proxy status: Proxied (orange cloud icon)
   TTL: Auto
   ```
5. Click "Save"

---

## Step 4: Wait & Test (5 min)

### 4.1 Wait for DNS
DNS propagation takes 5-15 minutes.

Check status:
```bash
dig honey.likesugar.ai
```

Or use: https://dnschecker.org/#CNAME/honey.likesugar.ai

### 4.2 Test Your Site
1. Visit `https://honey.likesugar.ai`
2. You should see your Streamlit app! 🎉
3. Test the movie taste analysis

---

## ✅ Done!

Your app is now live at:
- 🌐 **Production**: `https://honey.likesugar.ai`
- 📊 **Railway Dashboard**: https://railway.app/project/[your-project]
- 🔍 **Logs**: Railway Dashboard → Select service → Logs tab

---

## 🔄 Auto-Deploy Updates

Any time you push to `main`, Railway auto-deploys:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Railway detects the push and redeploys in ~3 minutes.

---

## 🐛 Troubleshooting

### App shows "Application Error"
**Check Railway logs:**
1. Railway Dashboard → Streamlit service → Logs
2. Look for error messages
3. Common issues:
   - Environment variables not set
   - MCP_SERVER_URL pointing to wrong URL
   - Python dependencies missing

**Fix:**
- Verify all environment variables are set
- Check MCP server is running (visit its health endpoint)
- Redeploy: Settings → Redeploy

### DNS not resolving
**Wait longer:** DNS can take up to 60 minutes

**Check Cloudflare:**
1. Ensure CNAME record is correct
2. Ensure "Proxied" is ON (orange cloud)
3. Check SSL/TLS mode: Full (strict)

### MCP Server timeout
**Check logs:**
1. Railway → MCP service → Logs
2. Look for startup errors

**Common fixes:**
- Verify OMDB_API_KEY is set correctly
- Check health: `https://[mcp-url]/actuator/health`
- Increase memory if needed: Settings → Resources

---

## 💰 Costs

**Month 1:** $0 (using $5 free credit)  
**Month 2+:** ~$5-8/month

Both services combined typically use:
- MCP Server: ~$3-5/month
- Streamlit: ~$2-3/month

---

## 🔐 Security

### Enable Cloudflare Protection

1. **SSL/TLS**
   - Cloudflare → SSL/TLS → Full (strict)

2. **Firewall Rules** (optional)
   - Block by country
   - Rate limiting
   - Bot protection

3. **Security Settings**
   - Under Security → Settings
   - Enable "Bot Fight Mode"
   - Enable "Email Address Obfuscation"

---

## 📊 Monitoring

### Railway Dashboard
- Real-time logs
- CPU/Memory usage
- Request metrics
- Error tracking

### Cloudflare Analytics
- Traffic stats
- Geographic distribution
- Security events
- Cache performance

---

## 🎯 Next Steps

- [ ] Set up monitoring alerts
- [ ] Configure Railway notifications (Settings → Notifications)
- [ ] Add more security rules in Cloudflare
- [ ] Set up staging environment (create a `develop` branch)
- [ ] Add CI/CD tests (optional)

---

## 📞 Support

**Railway Issues:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Cloudflare Issues:**
- Docs: https://developers.cloudflare.com
- Community: https://community.cloudflare.com

**App Issues:**
- Check the logs in Railway
- Review environment variables
- Test MCP server independently

---

## 🎬 Summary

**You now have:**
- ✅ Production app at `https://honey.likesugar.ai`
- ✅ Auto-deployments from GitHub
- ✅ SSL/TLS encryption
- ✅ DDoS protection via Cloudflare
- ✅ Built-in monitoring
- ✅ Zero server management

**Total time:** ~15 minutes  
**Monthly cost:** ~$5-8  
**Complexity:** Minimal  

Enjoy your deployed app! 🍯🎬

