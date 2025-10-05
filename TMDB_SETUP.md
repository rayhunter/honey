# TMDB API Setup Guide 📺

This guide will help you set up The Movie Database (TMDB) API to enable streaming availability features in the Honey Movie Recommender app.

## Why TMDB?

TMDB provides real-time streaming availability data, showing users where they can watch recommended movies on platforms like:
- Netflix
- Amazon Prime Video
- Disney+
- Hulu
- Apple TV+
- And many more!

## Getting Your TMDB API Key

### Step 1: Create a TMDB Account

1. Go to [https://www.themoviedb.org/](https://www.themoviedb.org/)
2. Click "Join TMDB" in the top right corner
3. Fill out the registration form and verify your email

### Step 2: Request an API Key

1. Once logged in, go to your account settings:
   - Click on your profile icon (top right)
   - Select "Settings"

2. Navigate to the API section:
   - In the left sidebar, click on "API"
   - Click "Request an API Key"

3. Choose API type:
   - Select "Developer" (for non-commercial use)
   - Or "Commercial" if you plan to monetize your app

4. Fill out the application form:
   - Application Name: "Honey Movie Recommender" (or your app name)
   - Application URL: Your app URL or GitHub repo
   - Application Summary: Brief description of your movie recommendation app
   - Agree to the Terms of Use

5. Submit and wait for approval (usually instant for Developer keys)

### Step 3: Copy Your API Key

Once approved, you'll see two keys:
- **API Key (v3 auth)** - This is what you need!
- API Read Access Token (v4 auth) - Not needed for this app

Copy the **API Key (v3 auth)**.

## Configuring the App

### Option 1: Using .streamlit/secrets.toml (Recommended)

1. Open or create `.streamlit/secrets.toml` in your project root
2. Add your TMDB API key:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
TMDB_API_KEY = "your_tmdb_api_key_here"
```

### Option 2: Using Environment Variables

Add to your shell profile (~/.zshrc, ~/.bashrc, etc.):

```bash
export TMDB_API_KEY="your_tmdb_api_key_here"
```

Or add to your `.env` file:

```bash
TMDB_API_KEY=your_tmdb_api_key_here
```

## Testing the Integration

1. Restart your Streamlit app if it's running
2. Enter movie preferences for both partners
3. Click "Find Our Perfect Movies"
4. Look for the "🎥 Where to Watch:" section in each movie result

If configured correctly, you'll see streaming services like:
- 📺 Netflix
- 📺 Amazon Prime Video
- 🎬 Apple TV+ (rent)
- 🛒 Vudu (buy)

## Troubleshooting

### No Streaming Information Showing

**Possible causes:**
1. **API key not configured**: Check `.streamlit/secrets.toml` or environment variables
2. **Invalid API key**: Verify your key is correct and active
3. **Movie not available**: Some movies may not have streaming data
4. **Regional restrictions**: Streaming availability is US-only by default

### Enable Debug Mode

To see detailed error messages:
1. Add `?debug` to your app URL: `http://localhost:8501?debug`
2. Check the debug toggle at the bottom right of the page
3. Look for TMDB-related error messages

### API Rate Limits

TMDB free tier limits:
- **40 requests per 10 seconds**
- **Thousands of requests per day**

This is more than enough for typical usage. If you hit rate limits, the app will gracefully skip streaming info for that movie.

## API Documentation

For more details about TMDB API:
- [Official TMDB API Documentation](https://developers.themoviedb.org/3)
- [Get Watch Providers Endpoint](https://developers.themoviedb.org/3/movies/get-movie-watch-providers)

## Attribution

Per TMDB's terms of service, any app using their API must provide attribution. This is already included in the app's footer and README.

---

## Optional: Customize Streaming Region

By default, the app shows US streaming availability. To change this:

1. Edit `movie_recommender.py`
2. Find the `TMDBClient.get_streaming_providers()` call
3. Change `country="US"` to your desired region code (e.g., "GB", "CA", "AU")

**Common region codes:**
- `US` - United States
- `GB` - United Kingdom
- `CA` - Canada
- `AU` - Australia
- `DE` - Germany
- `FR` - France
- `JP` - Japan

---

**Note:** TMDB API is optional. If not configured, the app will work normally but won't display streaming availability information.
