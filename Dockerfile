FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including SSL certificates
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY movie_recommender.py .
COPY style/ style/

# Create .streamlit directory and copy config
RUN mkdir -p .streamlit
COPY .streamlit/config.toml .streamlit/config.toml

# Expose port for Railway
EXPOSE 8501

# Health check - Railway sets $PORT dynamically
HEALTHCHECK CMD curl --fail http://localhost:${PORT:-8501}/_stcore/health || exit 1

# Start Streamlit with proper configuration for Railway
CMD streamlit run movie_recommender.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
