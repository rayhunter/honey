# ✅ Railway Deployment Checklist

## Before You Deploy

### 1. Environment Variables (Railway Dashboard → Variables)
```bash
✓ OPENAI_API_KEY=sk-proj-...
✓ TMDB_API_KEY=...
✓ DEEPSEEK_API_KEY=sk-...       # Optional, only if using DeepSeek
✓ APP_PASSWORD=...               # Optional, only if you want login protection
```

**Important:** 
- ❌ **DO NOT** set `APP_PASSWORD` unless you want authentication
- If you set it, you'll need that password to access your app!

### 2. Files Check
```bash
✓ Dockerfile exists
✓ requirements.txt updated
✓ .streamlit/config.toml exists
✓ movie_recommender.py has all security fixes
✓ style/ directory exists
```

### 3. Git Push
```bash
git add .
git commit -m "Security updates and deployment fixes"
git push origin main
```

---

## Railway Setup

### 1. Create New Project
1. Go to https://railway.app
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Dockerfile

### 2. Add Environment Variables
1. Click on your service
2. Click "Variables" tab
3. Click "+ New Variable"
4. Add each variable from step 1 above
5. Click "Add" after each one

### 3. Deploy
1. Railway will automatically deploy
2. Wait for build to complete (2-5 minutes)
3. Click "View Logs" to monitor progress

---

## Post-Deployment Testing

### 1. Check Deployment Status
- ✅ Build succeeded?
- ✅ Deploy succeeded?
- ✅ Service is running?

### 2. Open Your App
1. Click "Settings" tab
2. Find "Public Networking"
3. Click "Generate Domain"
4. Click the URL to open your app

### 3. Test Basic Functions
- [ ] App loads (no white screen)
- [ ] Sidebar shows "✅ API configured" (green checkmarks)
- [ ] Can type movie titles
- [ ] "Find Movies" button works
- [ ] Recommendations appear
- [ ] Movie posters load
- [ ] PDF download works

### 4. If Using Authentication
- [ ] Login screen appears
- [ ] Can login with `APP_PASSWORD`
- [ ] App works after login
- [ ] Logout button in sidebar

---

## 🚨 If Something Breaks

### App won't load at all
1. Check Railway "Deploy Logs"
2. Look for red error messages
3. Common causes:
   - Missing environment variable
   - Dockerfile error
   - Port configuration issue

### App loads but crashes when clicking "Find Movies"
1. Check "Runtime Logs" in Railway
2. Common causes:
   - Missing `OPENAI_API_KEY` or `TMDB_API_KEY`
   - Invalid API keys
   - Rate limit exceeded (wait 5 minutes)

### "CORS policy" or "WebSocket" errors
1. Make sure `.streamlit/config.toml` has `enableCORS = true`
2. Rebuild and redeploy

### "Rate limit exceeded"
- This is NORMAL if you click too fast
- Wait 5 minutes and try again
- Or increase limits (see RAILWAY_TROUBLESHOOTING.md)

### Can't get past login screen
- Make sure you're using the exact `APP_PASSWORD` from Railway Variables
- If you forgot it, go to Railway → Variables → View/Edit `APP_PASSWORD`
- Or delete `APP_PASSWORD` variable to disable authentication

---

## 🎯 Success Indicators

Your app is working correctly when you see:

✅ Railway shows "Active" status  
✅ URL loads without errors  
✅ Sidebar shows green "✅ API configured"  
✅ Can enter movies and get recommendations  
✅ Movie details and posters appear  
✅ No errors in browser console (F12 → Console tab)  

---

## 🔄 Updating Your App

When you make code changes:

```bash
# 1. Make your changes
# 2. Commit to git
git add .
git commit -m "Your update description"
git push origin main

# 3. Railway will automatically rebuild and redeploy
# 4. Wait 2-5 minutes for deployment
# 5. Refresh your browser
```

Railway automatically detects git pushes and redeploys!

---

## 💰 Cost Monitoring

### Free Tier Limits
- $5 free credit per month
- Typically enough for personal use
- ~1000-2000 recommendation requests per month

### Monitor Usage
1. Railway Dashboard → Usage tab
2. Check credit remaining
3. Set up billing alerts

### API Costs (Separate)
- OpenAI: ~$0.01 per recommendation
- TMDB: Free (no cost)
- DeepSeek: ~$0.001 per recommendation (cheaper!)

---

## Need Help?

📖 **Detailed Troubleshooting:** See `RAILWAY_TROUBLESHOOTING.md`  
🔒 **Security Info:** See `SECURITY.md`  
📝 **Full Deployment Guide:** See `DEPLOYMENT_RAILWAY.md`  

---

**Quick Reference:**
- Railway Dashboard: https://railway.app/dashboard
- Railway Status: https://status.railway.app
- Railway Discord: https://discord.gg/railway

