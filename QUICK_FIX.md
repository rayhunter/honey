# 🚨 Quick Fix Guide - App Not Working on Railway

## Tell Me Your Error and I'll Give You the Solution

### Error 1: "Sorry, OpenAI service is unavailable"
**Cause:** Missing or invalid `OPENAI_API_KEY` in Railway

**Fix:**
1. Go to Railway → Your Service → Variables
2. Click "+ New Variable"
3. Name: `OPENAI_API_KEY`
4. Value: Copy from your `.env` file (starts with `sk-proj-` or `sk-`)
5. Click "Add"
6. Wait 30 seconds for Railway to restart
7. Refresh your browser

**Double-check:**
- Key should be 100+ characters long
- Starts with `sk-proj-` or `sk-`
- No spaces before/after
- No quotes around it

---

### Error 2: "Rate limit exceeded"
**Cause:** You clicked too fast (rate limiter triggered)

**Temporary Fix - Wait:**
- Wait 5 minutes
- Refresh page
- Try again

**Permanent Fix - Disable Rate Limiting:**

Edit `movie_recommender.py` around line 983:

**FIND THIS:**
```python
if find_button:
    # Check rate limit first
    is_allowed, rate_error = rate_limiter.check_rate_limit()
    if not is_allowed:
        st.error(rate_error)
        st.info("💡 Tip: This limit prevents abuse and keeps API costs reasonable. Try again in a moment!")
        st.stop()
```

**REPLACE WITH:**
```python
if find_button:
    # Rate limiting temporarily disabled for debugging
    # is_allowed, rate_error = rate_limiter.check_rate_limit()
    # if not is_allowed:
    #     st.error(rate_error)
    #     st.info("💡 Tip: This limit prevents abuse and keeps API costs reasonable. Try again in a moment!")
    #     st.stop()
```

Then commit and push:
```bash
git add movie_recommender.py
git commit -m "Temporarily disable rate limiting"
git push origin main
```

---

### Error 3: Red ❌ "API Key not found" in sidebar
**Cause:** Railway can't see your environment variables

**Fix:**
1. Railway → Your Service → Variables
2. Make sure you see:
   - `OPENAI_API_KEY` with a long value
   - `TMDB_API_KEY` with a value
3. If missing, add them
4. If they exist, try **deleting and re-adding** them

**Important:** 
- Copy-paste directly from `.env` file
- Or copy from https://platform.openai.com/api-keys
- Don't type them manually (easy to make mistakes)

---

### Error 4: App loads but sidebar shows nothing
**Cause:** App crashed during startup

**Fix:**
1. Railway → Deployments → View Logs
2. Look for Python errors (lines in red)
3. Common errors:
   - `ModuleNotFoundError` → Dependency issue
   - `ImportError` → Dependency issue
   - `FileNotFoundError` → Missing file in Docker

**Solution for dependency issues:**
```bash
# Make sure requirements.txt is correct
cat requirements.txt

# Should show:
# streamlit>=1.41.1
# openai>=1.59.5
# python-dotenv>=1.0.1
# requests>=2.32.3
# reportlab>=4.2.5
```

If wrong, fix it, then:
```bash
git add requirements.txt
git commit -m "Fix requirements"
git push origin main
```

---

### Error 5: "TMDB movie details error"
**Cause:** Missing or invalid `TMDB_API_KEY`

**Fix:**
1. Get TMDB API key from: https://www.themoviedb.org/settings/api
2. Railway → Variables → Add:
   - Name: `TMDB_API_KEY`
   - Value: Your TMDB key (NOT the API Read Access Token)
3. Save and wait 30 seconds

---

### Error 6: SSL Certificate errors
**Cause:** Missing `ca-certificates` in Docker

**Already Fixed!** If you see this error:
```bash
git pull  # Get latest fixes
git push origin main  # Redeploy
```

---

### Error 7: Authentication blocking access
**Cause:** `APP_PASSWORD` is set in Railway

**Option A - Disable Auth:**
1. Railway → Variables
2. Find `APP_PASSWORD`
3. Click the trash icon to delete it
4. Wait for restart

**Option B - Use Auth:**
1. Railway → Variables
2. Click on `APP_PASSWORD` to view it
3. Use that password to login

---

### Error 8: Nothing happens when clicking "Find Movies"
**Cause:** Could be many things

**Debug Steps:**
1. Open browser console (F12 → Console tab)
2. Look for red errors
3. Common errors:
   - CORS error → Config issue (already fixed)
   - WebSocket error → Railway networking issue
   - 429 error → Rate limit
   - 401 error → Bad API key
   - 500 error → Server crash

**Generic fix:**
```bash
# Get latest code
git pull

# Force rebuild on Railway
# Go to Railway → Deployments → Click "Redeploy"
```

---

## 🔍 How to Get Better Error Messages

### Method 1: Add Debug Mode

Add this at the top of your `movie_recommender.py` main function (around line 930):

```python
def main():
    # Initialize session state
    init_session_state()
    
    # ADD THIS LINE:
    st.session_state.debug_mode = True  # Enable debug logging
    
    # Set page config first...
```

This will show detailed error messages.

### Method 2: Check Railway Logs

```bash
Railway → Your Service → Deployments → Latest → View Logs
```

Filter logs by clicking "Runtime Logs" to see live errors.

---

## 💊 Nuclear Option - Complete Reset

If nothing works, try this complete reset:

```bash
# 1. Delete Railway service
Railway → Your Service → Settings → Delete Service

# 2. Create new service from scratch
Railway → New Project → Deploy from GitHub

# 3. Add environment variables one by one:
OPENAI_API_KEY=...
TMDB_API_KEY=...

# 4. Wait for deployment (2-5 minutes)

# 5. Test again
```

---

## 📞 Still Broken? Share This Info:

Please tell me:

1. **Exact error message** (copy-paste or screenshot)
2. **What Railway logs show** (copy last 20 lines)
3. **What sidebar shows** (green ✅ or red ❌?)
4. **Did you set environment variables?** (Yes/No)
5. **Does it work locally?** (Yes/No)

With this info, I can give you an exact fix!

---

## ✅ Working Checklist

Your app is working when:
- [ ] Railway shows "Active" status
- [ ] URL loads without blank screen
- [ ] Sidebar shows "✅ OpenAI API configured"
- [ ] Sidebar shows "✅ TMDB API configured"
- [ ] Can type movie titles (no errors)
- [ ] Click "Find Movies" button (no crash)
- [ ] Recommendations appear within 10 seconds
- [ ] Movie posters load
- [ ] No red error messages

If ANY of these fail, that's your clue to the problem!

