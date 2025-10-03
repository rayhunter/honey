import streamlit as st
from openai import OpenAI
import os
import requests
import json
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
            return response.json()
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
            
            # Extract key information from the formatted text response
            details = {
                "title": "",
                "year": "",
                "plot": "",
                "actors": "",
                "runtime": "",
                "genre": "",
                "director": "",
                "imdb_rating": ""
            }
            
            lines = content_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('🎬'):
                    # Extract title and year from header like "🎬 The Matrix (1999)"
                    title_year = line.replace('🎬', '').strip()
                    if '(' in title_year and title_year.endswith(')'):
                        details["title"] = title_year.split('(')[0].strip()
                        details["year"] = title_year.split('(')[1].replace(')', '').strip()
                elif line.startswith('Runtime:'):
                    details["runtime"] = line.replace('Runtime:', '').strip()
                elif line.startswith('Genre:'):
                    details["genre"] = line.replace('Genre:', '').strip()
                elif line.startswith('Director:'):
                    details["director"] = line.replace('Director:', '').strip()
                elif line.startswith('Cast:'):
                    details["actors"] = line.replace('Cast:', '').strip()
                elif line.startswith('IMDB Rating:'):
                    details["imdb_rating"] = line.replace('IMDB Rating:', '').strip()
                elif line.startswith('Plot:'):
                    details["plot"] = line.replace('Plot:', '').strip()
            
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
        <p>Can't decide on a movie to watch together? Enter each partner's favorite movies below.
        We'll analyze your tastes and recommend films you'll both enjoy!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for partner inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="column-card">', unsafe_allow_html=True)
        st.subheader("🎭 Movie Lover 1's Favorites")
        partner1_movies = [
            st.text_input(f"Movie {i+1}", key=f"p1_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="column-card">', unsafe_allow_html=True)
        st.subheader("🎬 Movie Lover 2's Favorites")
        partner2_movies = [
            st.text_input(f"Movie {i+1}", key=f"p2_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    find_button = st.button("🎬 Find Our Perfect Movies!", type="primary")
    st.markdown('</div>', unsafe_allow_html=True)
    
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
                
                # Display analysis in a styled container
                st.markdown("""
                <div class="analysis-container">
                    <div class="analysis-title">Movie Taste Analysis</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Convert analysis data to DataFrame for better styling
                import pandas as pd
                analysis_data = pd.DataFrame([analysis1, analysis2])
                st.markdown(analysis_data.to_html(classes='analysis-table', index=False), unsafe_allow_html=True)
                
                # Get and display recommendations
                st.markdown("### 🍿 Your Perfect Movie Matches")
                recommendations = get_movie_recommendations(partner1_filtered, partner2_filtered)
            
            if recommendations:
                # Initialize OMDB MCP client
                omdb_client = OMDBMCPClient()
                
                for i, movie in enumerate(recommendations, 1):
                    # Try to get enhanced details from OMDB
                    movie_details = omdb_client.get_movie_details(movie)
                    
                    if movie_details:
                        # Display enhanced recommendation with details
                        st.markdown(f"""
                        <div class="recommendation">
                            <h3>{i}. {movie_details.get('title', movie)} ({movie_details.get('year', '')})</h3>
                            <p><strong>Synopsis:</strong> {movie_details.get('plot', 'Plot not available')}</p>
                            <p><strong>Cast:</strong> {movie_details.get('actors', 'Cast not available')}</p>
                            <p><strong>Runtime:</strong> {movie_details.get('runtime', 'Runtime not available')}</p>
                            <p><strong>Genre:</strong> {movie_details.get('genre', 'Genre not available')}</p>
                            <p><strong>IMDB Rating:</strong> {movie_details.get('imdb_rating', 'Rating not available')}</p>
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

if __name__ == "__main__":
    main()
