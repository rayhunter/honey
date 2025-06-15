import streamlit as st
from openai import OpenAI
import os
from typing import List, Dict

# Load CSS
def load_css():
    with open("style/aceternity_ui.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Add custom CSS for the analysis section
    st.markdown("""
    <style>
    .analysis-container {
        background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .analysis-title {
        color: #ffffff;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 20px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .analysis-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 10px;
    }
    .analysis-table th {
        background-color: #333333;
        color: #ffffff;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        border-radius: 8px;
    }
    .analysis-table td {
        background-color: #2a2a2a;
        color: #e0e0e0;
        padding: 12px;
        border-radius: 8px;
    }
    .analysis-table tr:hover td {
        background-color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

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
        st.subheader("Movie Lover 1 Favorite Movies")
        partner1_movies = [
            st.text_input(f"Movie {i+1}", key=f"p1_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="column-card">', unsafe_allow_html=True)
        st.subheader("Movie Lover 2 Favorite Movies")
        partner2_movies = [
            st.text_input(f"Movie {i+1}", key=f"p2_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Submit button
    st.markdown('<div style="display: flex; justify-content: center; margin-top: 20px;">', unsafe_allow_html=True)
    find_button = st.button("Find Our Perfect Movies!", type="primary")
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
                st.markdown("### Your Perfect Movie Matches")
                recommendations = get_movie_recommendations(partner1_filtered, partner2_filtered)
            
            if recommendations:
                for i, movie in enumerate(recommendations, 1):
                    st.markdown(f"""
                    <div class="recommendation">
                        <h3>{i}. {movie}</h3>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Couldn't generate recommendations. Please try again with different movies.")

if __name__ == "__main__":
    main()
