import streamlit as st
import openai
import os
from typing import List

# Set up the app with Pacific Northwest color palette
def setup_app():
    st.set_page_config(
        page_title="Honey, I Love You But I Can't Watch That",
        page_icon="🎬",
        layout="wide"
    )
    
    # Pacific Northwest color palette (forest greens, ocean blues, misty grays)
    st.markdown("""
    <style>
    :root {
        --primary: #3a5a40;
        --secondary: #588157;
        --accent1: #a3b18a;
        --accent2: #dad7cd;
        --text: #344e41;
        --light: #f8f9fa;
    }
    
    .stApp {
        background-color: var(--light);
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: var(--accent2) !important;
        border: 1px solid var(--primary) !important;
    }
    
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 1rem;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary) !important;
    }
    
    .title {
        color: var(--primary);
        font-size: 2.5rem !important;
        font-weight: 700;
    }
    
    .subheader {
        color: var(--secondary);
        font-size: 1.5rem !important;
    }
    
    .recommendation {
        background-color: var(--accent1);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: var(--text);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize OpenAI client
def init_openai():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

# Analyze movie preferences and get recommendations
def get_movie_recommendations(partner1_movies: List[str], partner2_movies: List[str]) -> List[str]:
    if not partner1_movies or not partner2_movies:
        return []
    
    prompt = f"""
    Analyze these two lists of favorite movies from partners in a relationship and identify 5 new movie recommendations 
    that would appeal to both based on common themes, genres, directors, or styles. 
    Return only the movie titles in a numbered list, nothing else.
    
    Partner 1's favorite movies: {", ".join(partner1_movies)}
    Partner 2's favorite movies: {", ".join(partner2_movies)}
    
    Recommendations:
    1. 
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a knowledgeable film critic who can identify cinematic commonalities between different movie preferences."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        recommendations = response.choices[0].message.content.strip()
        return [line.split(". ", 1)[1] for line in recommendations.split("\n") if ". " in line]
    except Exception as e:
        st.error(f"Error getting recommendations: {e}")
        return []

# Main app function
def main():
    setup_app()
    init_openai()
    
    st.markdown('<h1 class="title">Honey, I Love You But I Can\'t Watch That</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Movie Recommendations for Couples</h2>', unsafe_allow_html=True)
    
    st.write("""
    Can't decide on a movie to watch together? Each partner enters 5 favorite movies below. 
    We'll analyze your tastes and recommend films you'll both enjoy!
    """)
    
    # Create two columns for partner inputs
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Partner 1's Favorite Movies")
        partner1_movies = [
            st.text_input(f"Movie {i+1}", key=f"p1_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
    
    with col2:
        st.subheader("Partner 2's Favorite Movies")
        partner2_movies = [
            st.text_input(f"Movie {i+1}", key=f"p2_{i}", placeholder="Enter a movie title").strip()
            for i in range(5)
        ]
    
    if st.button("Find Our Perfect Movies!", type="primary"):
        # Filter out empty entries
        partner1_filtered = [m for m in partner1_movies if m]
        partner2_filtered = [m for m in partner2_movies if m]
        
        if len(partner1_filtered) < 3 or len(partner2_filtered) < 3:
            st.warning("Please enter at least 3 movies for each partner for better recommendations!")
        else:
            with st.spinner("Analyzing your movie tastes and finding perfect matches..."):
                recommendations = get_movie_recommendations(partner1_filtered, partner2_filtered)
            
            if recommendations:
                st.success("Here are 5 movies we think you'll both enjoy!")
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
