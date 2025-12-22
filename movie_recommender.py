import streamlit as st
from openai import OpenAI
import os
import requests
import json
import re
import html
import time
from typing import List, Dict, Optional
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Security: HTML sanitization to prevent XSS attacks
def sanitize_html(text: str) -> str:
    """
    Sanitize user input to prevent XSS attacks.
    Escapes HTML entities and removes potentially dangerous characters.
    """
    if not text:
        return ""
    # Escape HTML entities
    sanitized = html.escape(str(text))
    return sanitized

def sanitize_dict(data: dict) -> dict:
    """
    Recursively sanitize all string values in a dictionary.
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_html(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [sanitize_html(item) if isinstance(item, str) else item for item in value]
        else:
            sanitized[key] = value
    return sanitized

# Security: Input validation
def validate_movie_title(title: str, max_length: int = 200) -> tuple[bool, str]:
    """
    Validate movie title input.
    Returns (is_valid, error_message)
    """
    if not title or not title.strip():
        return True, ""  # Empty is ok, will be filtered out
    
    # Check length
    if len(title) > max_length:
        return False, f"Movie title too long (max {max_length} characters)"
    
    # Check for suspicious patterns that could indicate injection attacks
    suspicious_patterns = [
        '<script', '</script>', 'javascript:', 'onerror=', 'onclick=',
        'onload=', '<iframe', '<object', '<embed', 'data:text/html'
    ]
    
    title_lower = title.lower()
    for pattern in suspicious_patterns:
        if pattern in title_lower:
            return False, "Invalid characters in movie title"
    
    # Validate characters (allow letters, numbers, spaces, and common punctuation)
    # Allow unicode characters for international movie titles
    allowed_pattern = re.compile(r'^[\w\s\-\.\,\'\:\!\?\&\(\)]+$', re.UNICODE)
    if not allowed_pattern.match(title):
        return False, "Movie title contains invalid characters"
    
    return True, ""

def validate_all_inputs(partner1_movies: List[str], partner2_movies: List[str]) -> tuple[bool, str]:
    """
    Validate all user inputs.
    Returns (is_valid, error_message)
    """
    # Validate partner 1 movies
    for i, movie in enumerate(partner1_movies, 1):
        if movie:  # Only validate non-empty entries
            is_valid, error = validate_movie_title(movie)
            if not is_valid:
                return False, f"Partner 1, Movie {i}: {error}"
    
    # Validate partner 2 movies
    for i, movie in enumerate(partner2_movies, 1):
        if movie:  # Only validate non-empty entries
            is_valid, error = validate_movie_title(movie)
            if not is_valid:
                return False, f"Partner 2, Movie {i}: {error}"
    
    # Check minimum number of movies
    p1_count = len([m for m in partner1_movies if m])
    p2_count = len([m for m in partner2_movies if m])
    
    if p1_count < 1:
        return False, "Partner 1 must enter at least 1 movie"
    if p2_count < 1:
        return False, "Partner 2 must enter at least 1 movie"
    
    return True, ""

# Security: Prompt injection protection
def sanitize_for_llm(text: str) -> str:
    """
    Sanitize user input before sending to LLM to prevent prompt injection.
    Removes or escapes characters that could be used to manipulate prompts.
    """
    if not text:
        return ""
    
    # Remove common prompt injection patterns
    dangerous_patterns = [
        'ignore previous', 'ignore all previous', 'disregard',
        'system:', 'assistant:', 'user:', '###', '---',
        'forget everything', 'new instructions', 'override',
        'you are now', 'act as', 'pretend', 'roleplay'
    ]
    
    text_lower = text.lower()
    for pattern in dangerous_patterns:
        if pattern in text_lower:
            # Replace with safe equivalent
            text = text.replace(pattern, pattern.replace(' ', '_'))
            text = text.replace(pattern.capitalize(), pattern.replace(' ', '_'))
    
    # Limit length to prevent token flooding
    max_length = 200
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove newlines and excessive whitespace that could break prompts
    text = ' '.join(text.split())
    
    return text.strip()

def sanitize_movie_list(movies: List[str]) -> List[str]:
    """
    Sanitize a list of movie titles for safe LLM prompting.
    """
    return [sanitize_for_llm(movie) for movie in movies if movie]

# Security: Rate limiting
class RateLimiter:
    """
    Simple rate limiter to prevent API abuse.
    Limits number of requests per time window.
    """
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Args:
            max_requests: Maximum number of requests allowed in time window
            time_window: Time window in seconds (default 60 = 1 minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        
    def check_rate_limit(self, session_key: str = 'rate_limit_data') -> tuple[bool, str]:
        """
        Check if rate limit has been exceeded.
        Returns (is_allowed, error_message)
        """
        # Initialize rate limit data in session state
        if session_key not in st.session_state:
            st.session_state[session_key] = {
                'requests': [],
                'blocked_until': None
            }
        
        rate_data = st.session_state[session_key]
        current_time = datetime.now()
        
        # Check if currently blocked
        if rate_data['blocked_until']:
            if current_time < rate_data['blocked_until']:
                remaining = (rate_data['blocked_until'] - current_time).seconds
                return False, f"⏳ Rate limit exceeded. Please wait {remaining} seconds before trying again."
            else:
                # Unblock and clear
                rate_data['blocked_until'] = None
                rate_data['requests'] = []
        
        # Remove requests outside time window
        cutoff_time = current_time - timedelta(seconds=self.time_window)
        rate_data['requests'] = [
            req_time for req_time in rate_data['requests'] 
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(rate_data['requests']) >= self.max_requests:
            # Block for 5 minutes
            rate_data['blocked_until'] = current_time + timedelta(minutes=5)
            return False, f"⚠️ Too many requests! Maximum {self.max_requests} requests per {self.time_window} seconds. Blocked for 5 minutes."
        
        # Add current request
        rate_data['requests'].append(current_time)
        st.session_state[session_key] = rate_data
        
        return True, ""

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=5, time_window=60)  # 5 requests per minute

# Security: Simple authentication
def check_authentication() -> bool:
    """
    Check if user is authenticated.
    Returns True if authenticated, False otherwise.
    Uses environment variable or Streamlit secrets for password.
    """
    # Get password from environment or secrets
    app_password = os.getenv("APP_PASSWORD")
    if not app_password:
        try:
            app_password = st.secrets.get("APP_PASSWORD", "")
        except:
            app_password = ""
    
    # If no password is set, skip authentication (for development)
    if not app_password:
        return True
    
    # Check if already authenticated
    if st.session_state.get('authenticated', False):
        return True
    
    # Show login form
    st.markdown("## 🔐 Authentication Required")
    st.info("Please enter the password to access this application.")
    
    with st.form("login_form"):
        password_input = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if password_input == app_password:
                st.session_state.authenticated = True
                st.success("✅ Authentication successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
                # Add delay to prevent brute force
                time.sleep(2)
    
    return False

def add_logout_button():
    """Add logout button to sidebar if authenticated."""
    if st.session_state.get('authenticated', False):
        if st.sidebar.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

# Security: Error message sanitization
def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize error messages to prevent information disclosure.
    Removes sensitive paths, keys, and internal details.
    """
    error_str = str(error)
    
    # Remove file paths
    error_str = re.sub(r'[A-Za-z]:\\[^\s]+', '[PATH]', error_str)  # Windows paths
    error_str = re.sub(r'/[^\s]+', '[PATH]', error_str)  # Unix paths
    
    # Remove potential API keys or tokens
    error_str = re.sub(r'[A-Za-z0-9]{20,}', '[REDACTED]', error_str)
    
    # Remove IP addresses
    error_str = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]', error_str)
    
    # Truncate very long errors
    if len(error_str) > 200:
        error_str = error_str[:200] + "..."
    
    return error_str

def get_user_friendly_error(error: Exception, context: str = "") -> str:
    """
    Get a user-friendly error message based on the error type.
    """
    error_type = type(error).__name__
    
    # Map common errors to user-friendly messages
    friendly_messages = {
        'ConnectionError': 'Unable to connect to the service. Please check your internet connection.',
        'Timeout': 'Request timed out. Please try again.',
        'HTTPError': 'Service temporarily unavailable. Please try again later.',
        'JSONDecodeError': 'Received invalid response from service.',
        'KeyError': 'Missing expected data in response.',
        'ValueError': 'Invalid data format.',
        'APIError': 'API service error. Please try again later.',
    }
    
    base_message = friendly_messages.get(error_type, f'{context} error occurred.')
    
    # In debug mode, add sanitized error details
    if st.session_state.get('debug_mode', False):
        sanitized = sanitize_error_message(error)
        return f"{base_message}\n\nDebug info: {sanitized}"
    
    return base_message

# Load CSS
def load_css():
    with open("style/tailwind_glassmorphism.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Legacy setup_app function (kept for compatibility)
def setup_app():
    st.set_page_config(
        page_title="Honey, I Love You But I Can't Watch That",
        page_icon="🎬",
        layout="wide"
    )
    load_css()

# Initialize AI client (OpenAI or DeepSeek)
def init_ai_client():
    if st.session_state.use_deepseek:
        # DeepSeek configuration
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
            except:
                api_key = ""

        if api_key:
            st.sidebar.success("✅ DeepSeek API configured")
            return OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
        else:
            st.sidebar.error("❌ DeepSeek API Key not found!")
            return None
    else:
        # OpenAI configuration
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY", "")
            except:
                api_key = ""

        if api_key:
            st.sidebar.success("✅ OpenAI API configured")
            return OpenAI(api_key=api_key)
        else:
            st.sidebar.error("❌ OpenAI API Key not found!")
            return None

# Legacy function for backward compatibility
def init_openai():
    return init_ai_client()

# TMDB client for streaming availability
class TMDBClient:
    def __init__(self, api_key: str = None):
        tmdb_secret = ""
        try:
            tmdb_secret = st.secrets.get("TMDB_API_KEY", "")
        except:
            tmdb_secret = ""

        self.api_key = api_key or os.getenv("TMDB_API_KEY") or tmdb_secret

        # Show TMDB API key status (without exposing key)
        if self.api_key:
            st.sidebar.success("✅ TMDB API configured")
        else:
            st.sidebar.warning("⚠️ TMDB API Key not found!")
        self.base_url = "https://api.themoviedb.org/3"
    
    def find_movie_by_imdb_id(self, imdb_id: str) -> Optional[int]:
        """Find TMDB movie ID using IMDB ID"""
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/find/{imdb_id}",
                params={
                    "api_key": self.api_key,
                    "external_source": "imdb_id"
                },
                timeout=10,
                verify=True  # SSL verification
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("movie_results"):
                return data["movie_results"][0]["id"]
            return None
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.warning(get_user_friendly_error(e, "TMDB lookup"))
            return None
    
    def find_movie_by_title(self, title: str, year: Optional[str] = None) -> Optional[int]:
        """Find TMDB movie ID using title and optional year"""
        if not self.api_key or not title:
            return None
        
        try:
            params = {
                "api_key": self.api_key,
                "query": title,
                "include_adult": "false"
            }
            
            # Add year for better accuracy
            if year:
                params["year"] = year
            
            response = requests.get(
                f"{self.base_url}/search/movie",
                params=params,
                timeout=10,
                verify=True  # SSL verification
            )
            response.raise_for_status()
            data = response.json()
            
            if st.session_state.get('debug_mode', False):
                st.write(f"   - TMDB search for '{title}' ({year}): {len(data.get('results', []))} results")
            
            # Return first result's ID if found
            if data.get("results") and len(data["results"]) > 0:
                return data["results"][0]["id"]
            return None
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.warning(get_user_friendly_error(e, "TMDB search"))
            return None
    
    def get_streaming_providers(self, tmdb_id: int, country: str = "US") -> Optional[Dict]:
        """Get streaming availability for a movie"""
        if not self.api_key or not tmdb_id:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/movie/{tmdb_id}/watch/providers",
                params={"api_key": self.api_key},
                timeout=10,
                verify=True  # SSL verification
            )
            response.raise_for_status()
            data = response.json()

            # Return streaming info for specified country
            return data.get("results", {}).get(country, {})
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.warning(get_user_friendly_error(e, "TMDB streaming info"))
            return None

    def get_movie_details(self, title: str, year: Optional[str] = None) -> Optional[Dict]:
        """Get detailed movie information from TMDB"""
        if not self.api_key:
            return None

        try:
            # First, find the movie ID
            tmdb_id = self.find_movie_by_title(title, year)
            if not tmdb_id:
                return None

            # Get movie details
            response = requests.get(
                f"{self.base_url}/movie/{tmdb_id}",
                params={
                    "api_key": self.api_key,
                    "append_to_response": "credits"  # Include cast and crew
                },
                timeout=10,
                verify=True  # SSL verification
            )
            response.raise_for_status()
            data = response.json()

            if st.session_state.get('debug_mode', False):
                st.write(f"   - TMDB details for '{title}': Success")

            # Extract cast (limit to first 5 actors)
            cast_list = []
            if data.get('credits', {}).get('cast'):
                cast_list = [actor['name'] for actor in data['credits']['cast'][:5]]

            # Extract director
            director = ""
            if data.get('credits', {}).get('crew'):
                for person in data['credits']['crew']:
                    if person.get('job') == 'Director':
                        director = person['name']
                        break

            # Extract genres
            genres = ", ".join([genre['name'] for genre in data.get('genres', [])])

            # Format runtime
            runtime_min = data.get('runtime', 0)
            runtime = f"{runtime_min} min" if runtime_min else "Runtime not available"

            # Construct movie details dictionary
            details = {
                "title": data.get('title', title),
                "year": data.get('release_date', '')[:4] if data.get('release_date') else year or '',
                "plot": data.get('overview', 'Plot not available'),
                "actors": ", ".join(cast_list) if cast_list else "Cast not available",
                "runtime": runtime,
                "genre": genres if genres else "Genre not available",
                "director": director if director else "Director not available",
                "imdb_rating": f"{data.get('vote_average', 0):.1f}" if data.get('vote_average') else "Rating not available",
                "imdb_id": data.get('imdb_id', ''),
                "tmdb_id": tmdb_id
            }

            return details

        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.warning(get_user_friendly_error(e, "TMDB movie details"))
            return None

# Analyze movie preferences and get recommendations
def get_movie_recommendations(partner1_movies: List[str], partner2_movies: List[str], client=None) -> List[str]:
    if not partner1_movies or not partner2_movies:
        return []
    
    if not client:
        client = init_ai_client()
        if not client:
            show_error_once("Sorry, API service is unavailable at this time. Please check your API key configuration.")
            return []
    
    # Select model based on user choice
    model_name = "deepseek-chat" if st.session_state.use_deepseek else "gpt-4o-mini"
    
    # Sanitize movie titles to prevent prompt injection
    safe_partner1 = sanitize_movie_list(partner1_movies)
    safe_partner2 = sanitize_movie_list(partner2_movies)
    
    system_message = "You are a knowledgeable film critic who can identify cinematic commonalities between different movie preferences. Only respond with movie recommendations."
    user_message = f"""
    Analyze these two lists of favorite movies from partners in a relationship and identify 7 new movie recommendations 
    that would appeal to both based on common themes, genres, directors, or styles. 
    Return only the movie titles in a numbered list, nothing else.
    
    Partner 1's favorite movies: {", ".join(safe_partner1)}
    Partner 2's favorite movies: {", ".join(safe_partner2)}
    
    Recommendations:
    1. 
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        recommendations = response.choices[0].message.content.strip()
        return [line.split(". ", 1)[1] for line in recommendations.split("\n") if ". " in line]
    except Exception as e:
        current_model = "DeepSeek" if st.session_state.use_deepseek else "OpenAI"
        show_error_once(f"Sorry, {current_model} service is unavailable at this time. Try other model selection or try again later.")
        return []

def analyze_movie_selections(movies: List[str], partner_num: int, client=None) -> Dict[str, str]:
    if not movies:
        return {}
    
    if not client:
        client = init_ai_client()
        if not client:
            show_error_once("Sorry, API service is unavailable at this time. Please check your API key configuration.")
            return {
                "partner": f"Movie Lover {partner_num}",
                "movies": ", ".join(movies),
                "analysis": "Analysis unavailable - API service error"
            }
    
    # Select model based on user choice
    model_name = "deepseek-chat" if st.session_state.use_deepseek else "gpt-4o-mini"
    
    # Sanitize movie titles to prevent prompt injection
    safe_movies = sanitize_movie_list(movies)
    
    system_message = "You are a knowledgeable film critic who can provide concise analysis of movie preferences. Only respond with movie analysis."
    user_message = f"""
    Analyze this list of favorite movies and provide a very brief analysis (2-3 sentences) focusing on:
    1. Common themes or genres
    2. Notable directors or actors
    3. Overall taste profile
    
    Movies: {", ".join(safe_movies)}
    
    Provide the analysis in a concise format.
    """
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        return {
            "partner": f"Movie Lover {partner_num}",
            "movies": ", ".join(movies),
            "analysis": response.choices[0].message.content.strip()
        }
    except Exception as e:
        current_model = "DeepSeek" if st.session_state.use_deepseek else "OpenAI"
        show_error_once(f"Sorry, {current_model} service is unavailable at this time. Try other model selection or try again later.")
        # Return a fallback structure instead of empty dict
        return {
            "partner": f"Movie Lover {partner_num}",
            "movies": ", ".join(movies),
            "analysis": f"Analysis unavailable - {current_model} service error"
        }

# Initialize session state for styling toggle and model selection
def init_session_state():
    if 'enable_styling' not in st.session_state:
        st.session_state.enable_styling = True
    if 'use_deepseek' not in st.session_state:
        st.session_state.use_deepseek = False
    if 'error_shown' not in st.session_state:
        st.session_state.error_shown = False
    if 'viewed_movies' not in st.session_state:
        st.session_state.viewed_movies = set()
    if 'all_recommendations' not in st.session_state:
        st.session_state.all_recommendations = []
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_displayed' not in st.session_state:
        st.session_state.current_displayed = []

# Helper function to show error toast only once per session
def show_error_once(message: str, icon: str = "⚠️"):
    if not st.session_state.error_shown:
        st.toast(message, icon=icon)
        st.session_state.error_shown = True

# Function to manage dynamic recommendations
def get_displayed_recommendations():
    """Get the current 5 recommendations to display, replacing viewed ones with remaining options"""
    if not st.session_state.all_recommendations:
        return []
    
    # Get movies that haven't been viewed yet
    available_movies = [movie for movie in st.session_state.all_recommendations 
                       if movie not in st.session_state.viewed_movies]
    
    # If we have 5 or more available, show first 5
    if len(available_movies) >= 5:
        return available_movies[:5]
    
    # If we have fewer than 5 available, show all available
    return available_movies

def mark_movie_as_viewed(movie_title: str):
    """Mark a movie as viewed and update the displayed recommendations"""
    if movie_title not in st.session_state.viewed_movies:
        st.session_state.viewed_movies.add(movie_title)
        remaining = len(st.session_state.all_recommendations) - len(st.session_state.viewed_movies)
        if remaining > 0:
            st.success(f"✅ Marked '{movie_title}' as viewed. Getting a new recommendation... ({remaining} remaining)")
        else:
            st.success(f"✅ Marked '{movie_title}' as viewed. No more recommendations available.")
        st.rerun()

# PDF generation function
def generate_movie_recommendations_pdf(partner1_movies: List[str], partner2_movies: List[str], 
                                     analysis1: Dict, analysis2: Dict, recommendations: List[str]) -> bytes:
    """Generate a PDF with movie recommendations and analysis"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#2E86AB')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#A23B72')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6
    )
    
    # Title
    story.append(Paragraph("🍿 Your Perfect Movie Matches", title_style))
    story.append(Spacer(1, 20))
    
    # Partner 1 Analysis
    story.append(Paragraph(f"🎭 {analysis1.get('partner', 'Movie Lover 1')}", heading_style))
    story.append(Paragraph(f"<b>Favorite Movies:</b> {analysis1.get('movies', 'No movies available')}", normal_style))
    story.append(Paragraph(f"<b>Taste Profile:</b> {analysis1.get('analysis', 'Analysis not available')}", normal_style))
    story.append(Spacer(1, 15))
    
    # Partner 2 Analysis
    story.append(Paragraph(f"🎬 {analysis2.get('partner', 'Movie Lover 2')}", heading_style))
    story.append(Paragraph(f"<b>Favorite Movies:</b> {analysis2.get('movies', 'No movies available')}", normal_style))
    story.append(Paragraph(f"<b>Taste Profile:</b> {analysis2.get('analysis', 'Analysis not available')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("🎬 Recommended Movies for Both Partners", heading_style))
    story.append(Spacer(1, 10))
    
    for i, movie in enumerate(recommendations, 1):
        story.append(Paragraph(f"{i}. {movie}", normal_style))
    
    story.append(Spacer(1, 30))
    
    # Footer
    story.append(Paragraph("Generated by Honey, I Love You But I Can't Watch That", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=10, 
                                       alignment=1, textColor=colors.grey)))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Cached function to load CSS only when needed
@st.cache_data
def load_css_cached():
    with open("style/tailwind_glassmorphism.css", "r") as f:
        return f.read()

# Optimized setup_app function
def setup_app_optimized():
    # Only load CSS if styling is enabled
    if st.session_state.enable_styling:
        css_content = load_css_cached()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    
    # Add clean toggle styling using CSS custom properties
    st.markdown("""
    <style>
    :root {
        --toggle-bg: #87CEEB;
        --toggle-bg-checked: #4682B4;
        --toggle-border: #4682B4;
        --toggle-knob: white;
        --toggle-hover: #B0E0E6;
    }
    
    /* Clean toggle styling using attribute selectors */
    [data-testid="stToggle"] > label > div {
        background-color: var(--toggle-bg) !important;
        border: 2px solid var(--toggle-border) !important;
        border-radius: 20px !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stToggle"] > label > div[aria-checked="true"] {
        background-color: var(--toggle-bg-checked) !important;
    }
    
    [data-testid="stToggle"] > label > div > div {
        background-color: var(--toggle-knob) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        border-radius: 50% !important;
    }
    
    [data-testid="stToggle"] > label > div:hover {
        background-color: var(--toggle-hover) !important;
        transform: scale(1.05);
    }
    
    /* Cute download button styling */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
        text-transform: none !important;
        letter-spacing: 0.02em !important;
    }
    
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
        background: linear-gradient(135deg, #FF5252, #26A69A) !important;
    }
    
    [data-testid="stDownloadButton"] > button:active {
        transform: translateY(0) scale(1.02) !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
    }
    
    /* Cute checkbox styling for "Viewed" positioned after recommendation cards */
    .recommendation + div [data-testid="stCheckbox"] {
        margin-top: -1rem !important;
        margin-bottom: 1rem !important;
    }
    
    .recommendation + div [data-testid="stCheckbox"] > label {
        font-size: 0.9rem !important;
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
        margin: 0 !important;
        padding: 0.4rem 0.8rem !important;
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        cursor: pointer !important;
    }
    
    .recommendation + div [data-testid="stCheckbox"] > label:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    .recommendation + div [data-testid="stCheckbox"] > label > div {
        background: linear-gradient(135deg, #FF6B6B, #4ECDC4) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 4px !important;
        transition: all 0.3s ease !important;
        width: 18px !important;
        height: 18px !important;
    }
    
    .recommendation + div [data-testid="stCheckbox"] > label > div[aria-checked="true"] {
        background: linear-gradient(135deg, #FF5252, #26A69A) !important;
        box-shadow: 0 0 8px rgba(255, 107, 107, 0.4) !important;
    }
    
    .recommendation + div [data-testid="stCheckbox"] > label > div > div {
        background: white !important;
        border-radius: 50% !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
        width: 12px !important;
        height: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Main app function
def main():
    # Initialize session state
    init_session_state()
    
    # Set page config first (must be first Streamlit command)
    st.set_page_config(
        page_title="Honey, I Love You But I Can't Watch That",
        page_icon="🎬",
        layout="wide"
    )
    
    # Apply optimized styling
    setup_app_optimized()
    
    # Check authentication first
    if not check_authentication():
        st.stop()
    
    # Add logout button to sidebar if authenticated
    add_logout_button()
    
    st.markdown('<h1 class="title">Honey, I Love You But I Can\'t Watch That</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Movie Recommendations for Couples</p>', unsafe_allow_html=True)
    
    # Toggles for app styling and model selection (below subtitle)
    col1, col2 = st.columns([1, 1])
    with col1:
        enable_styling = st.toggle(
            "🎨 Style: Plain or Pretty", 
            value=st.session_state.enable_styling, 
            help="Toggle to enable/disable the custom app styling and theme"
        )
        if enable_styling != st.session_state.enable_styling:
            st.session_state.enable_styling = enable_styling
            st.rerun()
    with col2:
        use_deepseek = st.toggle(
            "🤖 Model: OpenAI or DeepSeek", 
            value=st.session_state.use_deepseek, 
            help="Toggle between OpenAI (off) and DeepSeek (on) models"
        )
        if use_deepseek != st.session_state.use_deepseek:
            st.session_state.use_deepseek = use_deepseek
            st.session_state.error_shown = False  # Reset error flag when model changes
            st.rerun()
    
    # Show current model selection
    current_model = "DeepSeek" if st.session_state.use_deepseek else "OpenAI"
    st.sidebar.info(f"🤖 Using: {current_model} Model")
    
    # Introduction
    st.markdown("""
    <div class="content-card">
        <h3>Can't decide on a movie to watch together? Enter each partner's favorite movies below.
        We'll analyze your tastes and recommend films you'll both enjoy!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for partner inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="column-card column-card-1"><h3>🎭 Movie Lover 1\'s Favorites</h3>', unsafe_allow_html=True)
        # st.subheader("🎭 Movie Lover 1's Favorites")
        partner1_movies = [
            st.text_input(f"Movie {i+1}", key=f"p1_{i}", placeholder="Enter a movie title", max_chars=200).strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="column-card column-card-2"><h3>🎬 Movie Lover 2\'s Favorites</h3>', unsafe_allow_html=True)
        # st.subheader("🎬 Movie Lover 2's Favorites")
        partner2_movies = [
            st.text_input(f"Movie {i+1}", key=f"p2_{i}", placeholder="Enter a movie title", max_chars=200).strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)

    # Submit button
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        find_button = st.button("🎬 Find Our Perfect Movies!", type="primary", use_container_width=True)
    
    
    if find_button:
        # Check rate limit first
        is_allowed, rate_error = rate_limiter.check_rate_limit()
        if not is_allowed:
            st.error(rate_error)
            st.info("💡 Tip: This limit prevents abuse and keeps API costs reasonable. Try again in a moment!")
            st.stop()
        
        # Filter out empty entries
        partner1_filtered = [m for m in partner1_movies if m]
        partner2_filtered = [m for m in partner2_movies if m]
        
        # Validate all inputs before processing
        is_valid, error_message = validate_all_inputs(partner1_filtered, partner2_filtered)
        if not is_valid:
            st.error(f"❌ Invalid input: {error_message}")
            st.stop()
        
        if len(partner1_filtered) < 3 or len(partner2_filtered) < 3:
            st.warning("Please enter at least 3 movies for each partner for better recommendations!")
        else:
            with st.spinner("Analyzing your movie tastes..."):
                # Initialize AI client once
                ai_client = init_ai_client()
                if not ai_client:
                    show_error_once("Sorry, API service is unavailable at this time. Please check your API key configuration.")
                    return
                
                # Analyze each partner's selections using the same client
                analysis1 = analyze_movie_selections(partner1_filtered, 1, ai_client)
                analysis2 = analyze_movie_selections(partner2_filtered, 2, ai_client)
                
                # Add color coding for each partner
                analysis1['background'] = 'linear-gradient(135deg, rgb(64, 217, 141) 0%, rgba(64, 217, 141, 0.275) 100%);'  # lean to green
                analysis2['background'] = 'linear-gradient(135deg, rgb(15, 145, 161) 0%, rgba(15, 145, 161, 0.275) 100%); '  # lean to blue
                movie_data = [analysis1, analysis2]
                
                # Display analysis title
                st.markdown("""
                <div class="analysis-container">
                    <div class="analysis-title">🎬 Movie Taste Analysis</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Add custom CSS for responsive card design
                st.markdown("""
                <style>
                    /* Better spacing and shadows for cards */
                    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
                        transition: transform 0.2s;
                    }
                    
                    [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"]:hover {
                        transform: translateY(-2px);
                    }
                    
                    /* Mobile responsiveness - stack cards on small screens */
                    @media (max-width: 768px) {
                        [data-testid="column"] {
                            width: 100% !important;
                            flex: 100% !important;
                            max-width: 100% !important;
                        }
                    }
                    /* Style the download button - more specific selectors */
                    div.stDownloadButton > button[kind="secondary"],
                    div.stDownloadButton > button[kind="primary"],
                    div.stDownloadButton > button {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                        color: white !important;
                        border: none !important;
                        border-radius: 12px !important;
                        padding: 0.6rem 1.5rem !important;
                        font-weight: 600 !important;
                        transition: all 0.3s ease !important;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
                     }
    
                    div.stDownloadButton > button[kind="secondary"]:hover,
                    div.stDownloadButton > button[kind="primary"]:hover,
                    div.stDownloadButton > button:hover {
                        background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%) !important;
                        transform: translateY(-2px) !important;
                        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6) !important;
                    }
    
                    div.stDownloadButton > button[kind="secondary"]:active,
                    div.stDownloadButton > button[kind="primary"]:active,
                    div.stDownloadButton > button:active {
                        transform: translateY(0px) !important;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # Display analysis in responsive columns
                cols = st.columns(2)
                
                # Sanitize movie_data to prevent XSS
                sanitized_movie_data = [sanitize_dict(data) if data else {} for data in movie_data]
                
                for idx, (col, data) in enumerate(zip(cols, sanitized_movie_data)):
                    with col:
                        with st.container(border=True):
                            # Check if data has required keys
                            if not data or 'partner' not in data:
                                st.error(f"Error loading analysis for partner {idx + 1}")
                                continue
                                
                            # Custom colored header (background is safe CSS, not user input)
                            st.markdown(f"""
                            <div style="background: {data.get('background', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)')}
                                        padding: 15px; border-radius: 8px; margin-bottom: 15px; 
                                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0; color: #fff;">🎭 {data['partner']}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Movies section
                            st.markdown("**🎥 Favorite Movies:**")
                            st.caption(data.get('movies', 'No movies available'))
                            
                            st.divider()
                            
                            # Analysis section
                            st.markdown("**📊 Taste Profile:**")
                            st.write(data.get('analysis', 'Analysis not available'))
                
                # Get and display recommendations using the same client
                # Create a row with the heading and download button
                col_heading, col_button = st.columns([3, 1])
                with col_heading:
                    st.markdown("### 🍿 Your Perfect Movie Matches")
                with col_button:
                    # Store data in session state for PDF generation
                    st.session_state.pdf_data = {
                        'partner1_movies': partner1_filtered,
                        'partner2_movies': partner2_filtered,
                        'analysis1': analysis1,
                        'analysis2': analysis2
                    }
                
                recommendations = get_movie_recommendations(partner1_filtered, partner2_filtered, ai_client)
                
                # Store all 7 recommendations in session state
                if recommendations:
                    st.session_state.all_recommendations = recommendations
                    st.session_state.viewed_movies = set()  # Reset viewed movies
                    st.session_state.pdf_data['recommendations'] = recommendations
                
                # Add the cute download button
                with col_button:
                    if recommendations:
                        # Generate PDF
                        pdf_bytes = generate_movie_recommendations_pdf(
                            partner1_filtered, partner2_filtered, 
                            analysis1, analysis2, recommendations
                        )
                        
                        # Create download button with cute styling
                        st.download_button(
                            label="📥 Download Recommendations",
                            data=pdf_bytes,
                            file_name="movie_recommendations.pdf",
                            mime="application/pdf",
                            help="Download your movie recommendations as a PDF",
                            use_container_width=True,
                            type="primary"
                        )
            
            # Check if we have stored recommendations from a previous run
            if st.session_state.all_recommendations:
                # Get the current recommendations to display (5 out of 7)
                displayed_recommendations = get_displayed_recommendations()

                if displayed_recommendations:
                    # Initialize TMDB client
                    tmdb_client = TMDBClient()

                    for i, movie in enumerate(displayed_recommendations, 1):
                        # Get enhanced details from TMDB
                        movie_details = tmdb_client.get_movie_details(movie)
                        
                        # Sanitize movie details to prevent XSS
                        if movie_details:
                            movie_details = sanitize_dict(movie_details)

                        if movie_details:
                            # Get streaming availability from TMDB
                            streaming_html = ""
                            title = movie_details.get('title')
                            year = movie_details.get('year')
                            tmdb_id = movie_details.get('tmdb_id')

                            # Debug info
                            if st.session_state.get('debug_mode', False):
                                st.info(f"🔍 Debug - Movie: {title}")
                                st.write(f"   - Title: {title}")
                                st.write(f"   - Year: {year}")
                                st.write(f"   - TMDB ID: {tmdb_id}")
                                st.write(f"   - TMDB API Key configured: {bool(tmdb_client.api_key)}")

                            if tmdb_client.api_key and tmdb_id:
                                streaming_info = tmdb_client.get_streaming_providers(tmdb_id)

                                if st.session_state.get('debug_mode', False):
                                    st.write(f"   - Streaming info received: {bool(streaming_info)}")
                                    if streaming_info:
                                        st.json(streaming_info)

                                if streaming_info:
                                    # Build streaming providers HTML (with sanitization)
                                    providers_list = []

                                    # Flatrate (subscription services)
                                    if streaming_info.get('flatrate'):
                                        for provider in streaming_info['flatrate']:
                                            safe_name = sanitize_html(provider.get('provider_name', ''))
                                            providers_list.append(f"📺 {safe_name}")

                                    # Rent
                                    if streaming_info.get('rent'):
                                        for provider in streaming_info['rent'][:3]:  # Limit to 3
                                            safe_name = sanitize_html(provider.get('provider_name', ''))
                                            providers_list.append(f"🎬 {safe_name} (rent)")

                                    # Buy
                                    if streaming_info.get('buy'):
                                        for provider in streaming_info['buy'][:3]:  # Limit to 3
                                            safe_name = sanitize_html(provider.get('provider_name', ''))
                                            providers_list.append(f"🛒 {safe_name} (buy)")

                                    if providers_list:
                                        # Add link to JustWatch if available (sanitize URL)
                                        watch_link = streaming_info.get('link', '')
                                        # Validate URL to prevent javascript: or data: URLs
                                        if watch_link and (watch_link.startswith('http://') or watch_link.startswith('https://')):
                                            safe_link = sanitize_html(watch_link)
                                            streaming_html = f"<p><strong>🎥 Where to Watch:</strong> {' • '.join(providers_list)} <br/><a href='{safe_link}' target='_blank' rel='noopener noreferrer' style='color: #2563EB; text-decoration: none;'>→ View all options</a></p>"
                                        else:
                                            streaming_html = f"<p><strong>🎥 Where to Watch:</strong> {' • '.join(providers_list)}</p>"
                            elif not tmdb_client.api_key:
                                if st.session_state.get('debug_mode', False):
                                    st.warning("⚠️ TMDB API key not configured")

                            # Display enhanced recommendation with details and streaming
                            st.markdown(f"""
                            <div class="recommendation">
                                <h3>{i}. {movie_details.get('title', movie)} ({movie_details.get('year', '')})</h3>
                                <p><strong>Synopsis:</strong> {movie_details.get('plot', 'Plot not available')}</p>
                                <p><strong>Cast:</strong> {movie_details.get('actors', 'Cast not available')}</p>
                                <p><strong>Runtime:</strong> {movie_details.get('runtime', 'Runtime not available')}</p>
                                <p><strong>Genre:</strong> {movie_details.get('genre', 'Genre not available')}</p>
                                <p><strong>TMDB Rating:</strong> {movie_details.get('imdb_rating', 'Rating not available')}</p>
                                {streaming_html}
                            </div>
                            """, unsafe_allow_html=True)

                            # Add "Viewed" checkbox positioned inside the recommendation div
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col3:
                                if st.checkbox("Viewed", key=f"viewed_{movie}",
                                             help="Check if you've already seen this movie to get a new recommendation"):
                                    mark_movie_as_viewed(movie)
                        else:
                            # Fallback to basic display if TMDB details unavailable
                            st.markdown(f"""
                            <div class="recommendation">
                                <h3>{i}. {movie}</h3>
                                <p><em>Additional details unavailable - TMDB API may not be configured</em></p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Add "Viewed" checkbox positioned inside the recommendation div
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col3:
                                if st.checkbox("Viewed", key=f"viewed_{movie}",
                                             help="Check if you've already seen this movie to get a new recommendation"):
                                    mark_movie_as_viewed(movie)
            else:
                st.error("Couldn't generate recommendations. Please try again with different movies.")
    
    # Footer
    st.markdown("---")
    
    # Initialize debug mode in session state if not present
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; color: #666;">
        <p style="margin-bottom: 0.5rem;">
            <strong>🎬 Honey, I love You But I Can't Watch That</strong>
        </p>
        <p style="font-size: 0.8rem; margin-bottom: 0.5rem;">
            Powered by OpenAI/DeepSeek & TMDB API
        </p>
        <p style="font-size: 0.9rem; color: #888;">
             &copy; Made with ❤️ for movie lovers by LikeSugarAI 2025
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Only show debug toggle if ?debug is in the URL
    query_params = st.query_params
    if "debug" in query_params:
        # Subtle debug toggle - minimal styling, right-aligned
        st.markdown("""
        <style>
            div[data-testid="stCheckbox"] > label {
                font-size: 0.5rem !important;
                color: #ccc !important;
            }
            div[data-testid="stCheckbox"] > label > div {
                font-size: 0.5rem !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([4, 1])
        with col2:
            st.checkbox("debug", value=st.session_state.debug_mode, 
                       key="debug_mode_checkbox", 
                       on_change=lambda: setattr(st.session_state, 'debug_mode', 
                                                 st.session_state.debug_mode_checkbox))

if __name__ == "__main__":
    main()
