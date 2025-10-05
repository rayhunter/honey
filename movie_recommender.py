import streamlit as st
from openai import OpenAI
import os
import requests
import json
import re
from typing import List, Dict, Optional

# Load CSS
def load_css():
    with open("style/tailwind_glassmorphism.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Set up the app with Aceternity UI styling
def setup_app():
    st.set_page_config(
        page_title="Honey, I Love You But I Can't Watch That",
        page_icon="🎬",
        layout="wide"
    )
    load_css()

# Initialize OpenAI client
def init_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
    
    return OpenAI(api_key=api_key)

# TMDB client for streaming availability
class TMDBClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TMDB_API_KEY") or st.secrets.get("TMDB_API_KEY", "")
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
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("movie_results"):
                return data["movie_results"][0]["id"]
            return None
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.warning(f"TMDB lookup error: {e}")
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
                timeout=10
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
                st.warning(f"TMDB search error: {e}")
            return None
    
    def get_streaming_providers(self, tmdb_id: int, country: str = "US") -> Optional[Dict]:
        """Get streaming availability for a movie"""
        if not self.api_key or not tmdb_id:
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/movie/{tmdb_id}/watch/providers",
                params={"api_key": self.api_key},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Return streaming info for specified country
            return data.get("results", {}).get(country, {})
        except Exception as e:
            if st.session_state.get('debug_mode', False):
                st.warning(f"TMDB streaming info error: {e}")
            return None

# MCP client for OMDB server communication
class OMDBMCPClient:
    def __init__(self, mcp_server_url: str = "http://localhost:8081"):
        self.mcp_server_url = mcp_server_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _make_mcp_request(self, method: str, params: dict = None) -> Optional[dict]:
        """Make a JSON-RPC request to the MCP server"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": method,
            "params": params or {}
        }
        
        try:
            response = self.session.post(
                f"{self.mcp_server_url}/mcp",
                json=request_data,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Debug: Display the raw response (only if debug mode is enabled)
            if st.session_state.get('debug_mode', False):
                with st.expander("🔍 Debug: View MCP API Response"):
                    st.json(result)

            return result
        except Exception as e:
            st.warning(f"OMDB MCP server not available: {e}")
            return None
    
    def get_movie_details(self, title: str, year: Optional[str] = None) -> Optional[dict]:
        """Get detailed movie information from OMDB via MCP"""
        params = {
            "name": "get_movie_details",
            "arguments": {
                "title": title,
                "plot": "full"
            }
        }
        
        if year:
            params["arguments"]["year"] = year
        
        response = self._make_mcp_request("tools/call", params)
        if response and "result" in response:
            return self._parse_movie_details(response["result"])
        return None
    
    def _parse_movie_details(self, mcp_result: dict) -> dict:
        """Parse MCP response to extract movie details"""
        if "content" in mcp_result and mcp_result["content"]:
            content_text = mcp_result["content"][0].get("text", "")
            
            # Debug: Show raw OMDB response
            if st.session_state.get('debug_mode', False):
                with st.expander("🔍 Debug: Raw OMDB Text Response"):
                    st.code(content_text)

            # Extract key information from the formatted text response
            details = {
                "title": "",
                "year": "",
                "plot": "",
                "actors": "",
                "runtime": "",
                "genre": "",
                "director": "",
                "imdb_rating": "",
                "imdb_id": ""
            }

            lines = content_text.split('\n')
            plot_started = False
            plot_lines = []

            for i, line in enumerate(lines):
                line_stripped = line.strip()

                # If we're in plot mode, collect all remaining text
                if plot_started:
                    # Stop collecting at "Awards:" if present
                    if line_stripped.startswith('Awards:'):
                        break
                    plot_lines.append(line_stripped)
                    continue

                if line_stripped.startswith('🎬'):
                    # Extract title and year from header like "🎬 The Matrix (1999)"
                    title_year = line_stripped.replace('🎬', '').strip()
                    if '(' in title_year and title_year.endswith(')'):
                        details["title"] = title_year.split('(')[0].strip()
                        details["year"] = title_year.split('(')[1].replace(')', '').strip()
                elif line_stripped.startswith('Runtime:'):
                    details["runtime"] = line_stripped.replace('Runtime:', '').strip()
                elif line_stripped.startswith('Genre:'):
                    details["genre"] = line_stripped.replace('Genre:', '').strip()
                elif line_stripped.startswith('Director:'):
                    details["director"] = line_stripped.replace('Director:', '').strip()
                elif line_stripped.startswith('Cast:'):
                    details["actors"] = line_stripped.replace('Cast:', '').strip()
                elif line_stripped.startswith('IMDB Rating:'):
                    details["imdb_rating"] = line_stripped.replace('IMDB Rating:', '').strip().replace('/10', '')
                elif line_stripped.startswith('IMDB ID:'):
                    details["imdb_id"] = line_stripped.replace('IMDB ID:', '').strip()
                elif 'imdb.com/title/' in line_stripped:
                    # Extract IMDB ID from URL like "https://www.imdb.com/title/tt0133093/"
                    match = re.search(r'tt\d+', line_stripped)
                    if match:
                        details["imdb_id"] = match.group(0)
                elif line_stripped.startswith('Plot:'):
                    # Plot text starts on next lines
                    plot_started = True
                    # Check if there's text on the same line
                    plot_text = line_stripped.replace('Plot:', '').strip()
                    if plot_text:
                        plot_lines.append(plot_text)

            # Join all plot lines into a single paragraph
            if plot_lines:
                details["plot"] = ' '.join(plot_lines)
            
            # Debug: Show extracted details
            if st.session_state.get('debug_mode', False):
                with st.expander("🔍 Debug: Extracted Movie Details"):
                    st.json(details)

            return details

        return None

# Analyze movie preferences and get recommendations
def get_movie_recommendations(partner1_movies: List[str], partner2_movies: List[str]) -> List[str]:
    if not partner1_movies or not partner2_movies:
        return []
    
    client = init_openai()
    
    system_message = "You are a knowledgeable film critic who can identify cinematic commonalities between different movie preferences."
    user_message = f"""
    Analyze these two lists of favorite movies from partners in a relationship and identify 5 new movie recommendations 
    that would appeal to both based on common themes, genres, directors, or styles. 
    Return only the movie titles in a numbered list, nothing else.
    
    Partner 1's favorite movies: {", ".join(partner1_movies)}
    Partner 2's favorite movies: {", ".join(partner2_movies)}
    
    Recommendations:
    1. 
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
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
        st.error(f"Error getting recommendations: {e}")
        return []

def analyze_movie_selections(movies: List[str], partner_num: int) -> Dict[str, str]:
    if not movies:
        return {}
    
    client = init_openai()
    
    system_message = "You are a knowledgeable film critic who can provide concise analysis of movie preferences."
    user_message = f"""
    Analyze this list of favorite movies and provide a very brief analysis (2-3 sentences) focusing on:
    1. Common themes or genres
    2. Notable directors or actors
    3. Overall taste profile
    
    Movies: {", ".join(movies)}
    
    Provide the analysis in a concise format.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
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
        st.error(f"Error analyzing movie selections: {e}")
        return {}

# Main app function
def main():
    setup_app()
    
    # App Header
    # st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.markdown('<h1 class="title">Honey, I Love You But I Can\'t Watch That</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader">Movie Recommendations for Couples</p>', unsafe_allow_html=True)
    # st.markdown('</div>', unsafe_allow_html=True)
    
    
    # Introduction
    st.markdown("""
    <div class="content-card">
        <h2>Can't decide on a movie to watch together? Enter each partner's favorite movies below.
        We'll analyze your tastes and recommend films you'll both enjoy!</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for partner inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="column-card column-card-1"><h2>🎭 Movie Lover 1\'s Favorites</h2>', unsafe_allow_html=True)
        # st.subheader("🎭 Movie Lover 1's Favorites")
        partner1_movies = [
            st.text_input(f"Movie {i+1}", key=f"p1_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="column-card column-card-2"><h2>🎬 Movie Lover 2\'s Favorites</h2>', unsafe_allow_html=True)
        # st.subheader("🎬 Movie Lover 2's Favorites")
        partner2_movies = [
            st.text_input(f"Movie {i+1}", key=f"p2_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)

    # Submit button
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        find_button = st.button("🎬 Find Our Perfect Movies!", type="primary", use_container_width=True)
    
    
    if find_button:
        # Filter out empty entries
        partner1_filtered = [m for m in partner1_movies if m]
        partner2_filtered = [m for m in partner2_movies if m]
        
        if len(partner1_filtered) < 3 or len(partner2_filtered) < 3:
            st.warning("Please enter at least 3 movies for each partner for better recommendations!")
        else:
            with st.spinner("Analyzing your movie tastes..."):
                # Analyze each partner's selections
                analysis1 = analyze_movie_selections(partner1_filtered, 1)
                analysis2 = analyze_movie_selections(partner2_filtered, 2)
                
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
                </style>
                """, unsafe_allow_html=True)
                
                # Display analysis in responsive columns
                cols = st.columns(2)
                
                for idx, (col, data) in enumerate(zip(cols, movie_data)):
                    with col:
                        with st.container(border=True):
                            # Custom colored header
                            st.markdown(f"""
                            <div style="background: {data['background']}
                                        padding: 15px; border-radius: 8px; margin-bottom: 15px; 
                                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                                <h3 style="margin: 0; color: #fff;">🎭 {data['partner']}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Movies section
                            st.markdown("**🎥 Favorite Movies:**")
                            st.caption(data['movies'])
                            
                            st.divider()
                            
                            # Analysis section
                            st.markdown("**📊 Taste Profile:**")
                            st.write(data['analysis'])
                
                # Get and display recommendations
                st.markdown("### 🍿 Your Perfect Movie Matches")
                recommendations = get_movie_recommendations(partner1_filtered, partner2_filtered)
            
            if recommendations:
                # Initialize clients
                omdb_client = OMDBMCPClient()
                tmdb_client = TMDBClient()
                
                for i, movie in enumerate(recommendations, 1):
                    # Try to get enhanced details from OMDB
                    movie_details = omdb_client.get_movie_details(movie)
                    
                    if movie_details:
                        # Get streaming availability from TMDB
                        streaming_html = ""
                        title = movie_details.get('title')
                        year = movie_details.get('year')
                        imdb_id = movie_details.get('imdb_id')
                        
                        # Debug info
                        if st.session_state.get('debug_mode', False):
                            st.info(f"🔍 Debug - Movie: {title}")
                            st.write(f"   - Title: {title}")
                            st.write(f"   - Year: {year}")
                            st.write(f"   - IMDB ID: {imdb_id if imdb_id else 'Not available'}")
                            st.write(f"   - TMDB API Key configured: {bool(tmdb_client.api_key)}")
                        
                        tmdb_id = None
                        if tmdb_client.api_key:
                            # Try IMDB ID first if available
                            if imdb_id:
                                tmdb_id = tmdb_client.find_movie_by_imdb_id(imdb_id)
                                if st.session_state.get('debug_mode', False):
                                    st.write(f"   - TMDB ID from IMDB: {tmdb_id}")
                            
                            # Fallback to title+year search
                            if not tmdb_id and title:
                                tmdb_id = tmdb_client.find_movie_by_title(title, year)
                                if st.session_state.get('debug_mode', False):
                                    st.write(f"   - TMDB ID from title search: {tmdb_id}")
                            
                            if tmdb_id:
                                streaming_info = tmdb_client.get_streaming_providers(tmdb_id)
                                
                                if st.session_state.get('debug_mode', False):
                                    st.write(f"   - Streaming info received: {bool(streaming_info)}")
                                    if streaming_info:
                                        st.json(streaming_info)
                                
                                if streaming_info:
                                    # Build streaming providers HTML
                                    providers_list = []
                                    
                                    # Flatrate (subscription services)
                                    if streaming_info.get('flatrate'):
                                        for provider in streaming_info['flatrate']:
                                            providers_list.append(f"📺 {provider['provider_name']}")
                                    
                                    # Rent
                                    if streaming_info.get('rent'):
                                        for provider in streaming_info['rent'][:3]:  # Limit to 3
                                            providers_list.append(f"🎬 {provider['provider_name']} (rent)")
                                    
                                    # Buy
                                    if streaming_info.get('buy'):
                                        for provider in streaming_info['buy'][:3]:  # Limit to 3
                                            providers_list.append(f"🛒 {provider['provider_name']} (buy)")
                                    
                                    if providers_list:
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
                            <p><strong>IMDB Rating:</strong> {movie_details.get('imdb_rating', 'Rating not available')}</p>
                            {streaming_html}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Fallback to basic display if OMDB details unavailable
                        st.markdown(f"""
                        <div class="recommendation">
                            <h3>{i}. {movie}</h3>
                            <p><em>Additional details unavailable - OMDB MCP server may not be running</em></p>
                        </div>
                        """, unsafe_allow_html=True)
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
            <strong>🎬 Honey Movie Recommender</strong>
        </p>
        <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">
            Powered by OpenAI GPT-4 & OMDB MCP Server
        </p>
        <p style="font-size: 0.8rem; color: #888;">
            Made with ❤️ for movie lovers everywhere
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
