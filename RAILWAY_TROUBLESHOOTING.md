# 🚂 Railway Deployment Troubleshooting Guide

## Critical Issues That Could Break Your App

### ✅ FIXED: Configuration Issues

#### 1. ✓ Missing .streamlit/config.toml in Docker
**Status:** FIXED in Dockerfile
**What was wrong:** Config file wasn't being copied to Docker image
**How we fixed it:** Added `COPY .streamlit/config.toml .streamlit/config.toml`

#### 2. ✓ CORS Disabled
**Status:** FIXED in config.toml
**What was wrong:** `enableCORS = false` breaks Streamlit's websocket connection
**How we fixed it:** Changed to `enableCORS = true`

---

## ⚠️ Potential Issues You Need to Check

### Issue #3: Authentication Blocking Access 🔐

**Symptom:** App loads but shows login screen, and you can't get past it

**Cause:** If you set `APP_PASSWORD` in Railway environment variables, authentication is enabled by default.

**Solutions:**

**Option A: Disable Authentication (Easiest)**
```bash
# In Railway, DON'T set APP_PASSWORD variable
# Authentication will be skipped automatically
```

**Option B: Enable Authentication (Recommended)**
```bash
# In Railway Environment Variables:
APP_PASSWORD=YourSecurePassword123

# Then use this password to login when you visit the site
```

**Check in Railway:**
1. Go to your app in Railway
2. Click "Variables" tab
3. Look for `APP_PASSWORD`
4. Either remove it OR remember what you set it to

---

### Issue #4: Rate Limiting Too Aggressive 🚦

**Symptom:** After 5 requests in 1 minute, you get blocked for 5 minutes

**Current Settings:**
- 5 requests per 60 seconds
- 5 minute block when exceeded

**If this is too strict for production:**

Edit `movie_recommender.py` line with `RateLimiter`:
```python
# Current (line ~218):
rate_limiter = RateLimiter(max_requests=5, time_window=60)

# More lenient option:
rate_limiter = RateLimiter(max_requests=20, time_window=60)

# Or disable rate limiting entirely (NOT recommended):
# Comment out the rate limit check in the main function
```

---

### Issue #5: Missing Environment Variables 🔑

**Symptom:** "API Key not found" errors, or app loads but crashes when you click "Find Movies"

**Required Variables in Railway:**
```bash
OPENAI_API_KEY=sk-proj-...        # Required for OpenAI
DEEPSEEK_API_KEY=sk-...           # Required for DeepSeek  
TMDB_API_KEY=...                  # Required for movie details
APP_PASSWORD=...                  # Optional (for authentication)
```

**How to Set in Railway:**
1. Go to your Railway project
2. Click on your service
3. Go to "Variables" tab
4. Click "New Variable"
5. Add each variable above

**Testing:**
- The app will show status in sidebar (green ✅ or red ❌)
- If you see "❌ API Key not found", that variable is missing

---

### Issue #6: Port Configuration 🔌

**Symptom:** Railway says "Application failed to respond"

**What Railway Needs:**
- Railway automatically sets `$PORT` environment variable
- Your app MUST listen on `0.0.0.0:$PORT`

**Our Configuration (Should Work):**
```bash
# In Dockerfile (line 30-34):
streamlit run movie_recommender.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true
```

**If it still fails:**
Check Railway logs for the actual port number, then verify Streamlit is binding to it.

---

### Issue #7: SSL Certificate Verification 🔒

**Symptom:** "SSL: CERTIFICATE_VERIFY_FAILED" errors in logs

**Cause:** We enabled `verify=True` on all requests (security feature)

**If TMDB API calls fail:**

Railway's container might not have updated SSL certificates.

**Fix Option A - Update Dockerfile:**
```dockerfile
# Add this after line 6 in Dockerfile:
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
```

**Fix Option B - Temporary (Not Recommended):**
Set environment variable in Railway:
```bash
PYTHONHTTPSVERIFY=0
```
⚠️ This disables SSL verification (less secure)

---

### Issue #8: Memory Limits 💾

**Symptom:** App crashes randomly or during recommendations

**Cause:** Railway free tier has memory limits

**Current Usage:**
- Base Streamlit: ~100MB
- OpenAI/DeepSeek API calls: ~50MB
- PDF generation: ~20MB per PDF
- Total: ~170-200MB peak

**Railway Free Tier Limit:** 512MB (should be fine)

**If you hit limits:**
1. Upgrade Railway plan
2. Reduce max_tokens in API calls
3. Disable PDF generation feature

---

### Issue #9: Cold Starts ❄️

**Symptom:** First load after inactivity is very slow (30-60 seconds)

**This is NORMAL on Railway free tier:**
- App sleeps after inactivity
- First request wakes it up
- Subsequent requests are fast

**Solutions:**
1. Accept it (it's free!)
2. Use Railway Pro plan (no cold starts)
3. Set up a health check ping service (keeps it awake)

---

### Issue #10: XSRF Protection Issues 🛡️

**Symptom:** "XSRF cookie mismatch" errors

**Cause:** `enableXsrfProtection = true` can cause issues with some proxies

**If you see XSRF errors:**

Edit `.streamlit/config.toml`:
```toml
[server]
enableXsrfProtection = false  # Change from true to false
```

Then redeploy.

---

## 🔍 Debugging Steps

### Step 1: Check Railway Logs
```bash
# In Railway dashboard:
1. Click your service
2. Click "Deployments" tab
3. Click latest deployment
4. Check "Deploy Logs" and "Runtime Logs"
```

**Look for:**
- ❌ "ModuleNotFoundError" → Missing dependency
- ❌ "API Key not found" → Missing environment variable
- ❌ "Port already in use" → Port configuration issue
- ❌ "SSL" errors → Certificate verification issues

### Step 2: Test Locally First
```bash
# Run the EXACT same way Railway does:
cd /your/project
docker build -t honey-test .
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e TMDB_API_KEY=your_key \
  honey-test

# Visit http://localhost:8501
```

### Step 3: Verify Environment Variables
```python
# Add this temporarily to movie_recommender.py (top of main function):
st.write("Environment Check:")
st.write(f"OpenAI: {bool(os.getenv('OPENAI_API_KEY'))}")
st.write(f"DeepSeek: {bool(os.getenv('DEEPSEEK_API_KEY'))}")
st.write(f"TMDB: {bool(os.getenv('TMDB_API_KEY'))}")
st.write(f"Auth: {bool(os.getenv('APP_PASSWORD'))}")
```

### Step 4: Check Railway Dashboard
- **Build logs:** Did Docker build succeed?
- **Deploy logs:** Did the app start?
- **Runtime logs:** Any errors after startup?
- **Metrics:** CPU/Memory usage normal?

---

## 🚀 Deployment Checklist

Before deploying to Railway:

### Code Changes:
- [ ] Latest code committed to git
- [ ] `requirements.txt` updated
- [ ] `.streamlit/config.toml` exists and configured
- [ ] `Dockerfile` copies all necessary files
- [ ] Tested locally with Docker

### Railway Configuration:
- [ ] Environment variables set:
  - [ ] `OPENAI_API_KEY`
  - [ ] `TMDB_API_KEY`
  - [ ] `DEEPSEEK_API_KEY` (if using)
  - [ ] `APP_PASSWORD` (if using auth)
- [ ] Connected to correct GitHub repo/branch
- [ ] Custom domain configured (if using)
- [ ] Railway CLI installed (optional)

### Post-Deployment Testing:
- [ ] App loads without errors
- [ ] Can enter movie titles
- [ ] "Find Movies" button works
- [ ] Recommendations appear
- [ ] Movie details load (posters, cast, etc.)
- [ ] PDF download works
- [ ] No console errors in browser DevTools

---

## 🔧 Quick Fixes

### "App won't start"
1. Check Railway build logs
2. Verify `Dockerfile` syntax
3. Check `requirements.txt` for typos
4. Try rebuilding: `railway up --detach`

### "App starts but crashes on use"
1. Check runtime logs for errors
2. Verify ALL environment variables are set
3. Test API keys separately
4. Check if rate limit was hit

### "Can't login" (if using authentication)
1. Verify `APP_PASSWORD` is set in Railway
2. Try the password you set
3. Check browser console for errors
4. Clear browser cookies and try again

### "Too many rate limit blocks"
1. Increase rate limits in code (see Issue #4)
2. Or disable rate limiting temporarily
3. Or wait 5 minutes for block to expire

---

## 📞 Getting Help

If still broken after checking everything:

1. **Check Railway Status:** https://status.railway.app/
2. **Railway Discord:** https://discord.gg/railway
3. **Review Logs:** Copy error messages from Railway logs
4. **GitHub Issues:** Open issue in your repo with:
   - Error message
   - Railway logs (redact API keys!)
   - Steps to reproduce

---

## 🎯 Expected Behavior

### Successful Deployment Shows:
✅ Build succeeded in Railway  
✅ App accessible at Railway URL  
✅ Sidebar shows "✅ API configured" (green)  
✅ Can enter 3+ movies per partner  
✅ Recommendations appear within 10 seconds  
✅ Movie posters and details load  
✅ PDF download works  
✅ No errors in Railway logs  

### Performance Expectations:
- First load (cold start): 30-60 seconds
- Subsequent loads: 2-5 seconds
- Recommendation generation: 5-10 seconds
- Movie details loading: 1-3 seconds per movie

---

**Last Updated:** December 2025  
**Railway Version:** Compatible with Railway v2  
**App Status:** Production Ready ✅


