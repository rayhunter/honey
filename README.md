# Honey, I Love You But I Can't Watch That

A movie recommendation app for couples who have different tastes in films.

## About

This Streamlit app helps couples find movies they'll both enjoy by analyzing each partner's favorite films and suggesting compatible options.

## Features

- Each partner enters their top 5 favorite movies
- AI-powered analysis of movie preferences
- Recommendations based on common themes, genres, directors, or styles
- Beautiful Pacific Northwest-inspired UI

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key:
   - Create a `.streamlit/secrets.toml` file with:
     ```
     OPENAI_API_KEY = "your_api_key_here"
     ```
   - Or set it as an environment variable

   - verify conda env: honey

4. Run the app:
   ```
   streamlit run movie_recommender.py
   ```

## Technologies

- Python
- Streamlit
- OpenAI GPT-3.5 API 