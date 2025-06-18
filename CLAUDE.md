# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is "Honey, I Love You But I Can't Watch That" - a Streamlit-based movie recommendation app for couples with different movie tastes. The app analyzes each partner's favorite movies using OpenAI's GPT-4 API and suggests compatible films.

## Development Environment

- **Python Environment**: Uses conda environment named `honey`
- **Main Framework**: Streamlit for the web interface
- **AI Integration**: OpenAI GPT-4.1 API for movie analysis and recommendations

## Commands

### Setup and Installation
```bash
# Activate conda environment
conda activate honey

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the Streamlit app
streamlit run movie_recommender.py
```

### Development
- No specific build, test, or lint commands are configured
- The app runs directly with Streamlit's development server

## Architecture

### Core Components
- **movie_recommender.py**: Main application file containing all logic
  - `setup_app()`: Configures Streamlit page settings and loads CSS
  - `init_openai()`: Initializes OpenAI client with API key from secrets or environment
  - `get_movie_recommendations()`: Analyzes movie preferences and generates recommendations
  - `analyze_movie_selections()`: Provides analysis of individual partner's movie tastes
  - `main()`: Primary app interface and user interaction flow

### UI Styling
- **style/aceternity_ui.css**: Custom CSS for modern UI styling
- **Inline CSS**: Additional styling for analysis containers and tables in movie_recommender.py
- Uses Pacific Northwest-inspired design theme

### Configuration
- **OpenAI API Key**: Retrieved from `.streamlit/secrets.toml` file or `OPENAI_API_KEY` environment variable
- **Dependencies**: Listed in requirements.txt (Streamlit, OpenAI, python-dotenv)

## Key Features
- Dual partner movie input (5 favorites each)
- AI-powered preference analysis using GPT-4.1
- Styled recommendation cards with custom CSS
- Responsive two-column layout for partner inputs

## File Structure Notes
- `index.html`: Appears to be unrelated NutriPro nutrition portal (likely leftover from another project)
- `todo.txt`: Contains feature requests for results display and messaging functionality