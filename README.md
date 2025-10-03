# Honey, I Love You But I Can't Watch That 🎬

A movie recommendation app for couples who have different tastes in films.

## About

This Streamlit app helps couples find movies they'll both enjoy by analyzing each partner's favorite films and suggesting compatible options. The app features enhanced movie details powered by an integrated OMDB MCP (Model Context Protocol) server that provides rich metadata including cast, plot, ratings, and more.

## ✨ Features

- 🎭 **Dual Partner Input**: Each partner enters their top 5 favorite movies
- 🤖 **AI-Powered Analysis**: GPT-4 analyzes movie preferences and taste profiles
- 🎯 **Smart Recommendations**: Suggestions based on common themes, genres, directors, or styles
- 🎬 **Enhanced Movie Details**: Rich metadata via OMDB MCP server including:
  - Full plot synopses
  - Cast and crew information
  - Runtime and genre details
  - IMDB ratings and awards
  - Director and production info
- 🎨 **Beautiful UI**: Modern glassmorphism design with dynamic gradients
- 🔍 **Intelligent Caching**: Optimized movie data retrieval and caching

## 🚀 Quick Start

### One-Command Startup (Recommended)

Use the unified startup script that automatically handles everything:

```bash
./start.sh
```

That's it! The script will:
- ✅ Check all prerequisites (Python, Docker, Java, etc.)
- ✅ Auto-detect the best startup method
- ✅ Set up the conda `honey` environment
- ✅ Start the OMDB MCP server (Docker/local)
- ✅ Launch the Streamlit app
- ✅ Monitor services and handle cleanup

### Startup Options

**Auto-detect best mode:**
```bash
./start.sh
```

**Docker Compose (recommended):**
```bash
./start.sh compose
```

**Local Java execution:**
```bash
./start.sh local
```

**Docker container:**
```bash
./start.sh docker
```

**Check system status:**
```bash
./start.sh --status
```

**Stop all services:**
```bash
./start.sh --cleanup
```

**View help:**
```bash
./start.sh --help
```

## 🛠 Manual Setup (Optional)

If you prefer manual setup:

### Prerequisites

- **Python 3.11+** (with conda recommended)
- **Docker & Docker Compose** (for enhanced mode) OR **Java 17+ & Maven** (for local mode)
- **OMDB API Key** (free from [omdbapi.com](http://www.omdbapi.com/apikey.aspx))
- **OpenAI API Key** (for AI recommendations)

### Environment Setup

1. **Clone this repository:**
   ```bash
   git clone <repository-url>
   cd honey
   ```

2. **Configure environment variables:**
   Create a `.env` file:
   ```bash
   # OMDB API Key for enhanced movie details
   OMDB_API_KEY=your-omdb-api-key-here
   
   # OMDB MCP Server URL (default: http://localhost:8081)
   OMDB_MCP_SERVER_URL=http://localhost:8081
   ```

3. **Set up OpenAI API key:**
   - Create `.streamlit/secrets.toml`:
     ```toml
     OPENAI_API_KEY = "your_openai_api_key_here"
     ```
   - Or set as environment variable:
     ```bash
     export OPENAI_API_KEY="your_openai_api_key_here"
     ```

4. **Create conda environment:**
   ```bash
   conda create -n honey python=3.11 -y
   conda activate honey
   pip install -r requirements.txt
   ```

### Manual Service Startup

**Option 1: Docker Compose (Recommended)**
```bash
# Start OMDB MCP server
export OMDB_API_KEY=your-api-key
docker-compose up -d omdb-mcp-server

# Start Streamlit app
conda activate honey
streamlit run movie_recommender.py
```

**Option 2: Local Java Execution**
```bash
# Start OMDB MCP server locally
cd omdb-mcp-server
export OMDB_API_KEY=your-api-key
mvn spring-boot:run

# In another terminal, start Streamlit app
conda activate honey
streamlit run movie_recommender.py
```

## 🌐 Services

Once started, the following services will be available:

- **🎬 Streamlit App**: http://localhost:8501 - Main movie recommender interface
- **🔌 OMDB MCP Server**: http://localhost:8081 - Movie database API server
- **📚 API Documentation**: http://localhost:8081/swagger-ui - Interactive API docs

## 🏗 Architecture

The application consists of three main components:

### 1. Streamlit Movie Recommender (`movie_recommender.py`)
- Web interface for partner movie input
- AI-powered preference analysis using GPT-4
- Recommendation display with enhanced movie details
- Modern glassmorphism UI with responsive design

### 2. OMDB MCP Server (`omdb-mcp-server/`)
- Spring Boot application implementing Model Context Protocol
- Three MCP tools: `search_movies`, `get_movie_details`, `get_movie_by_imdb_id`
- Intelligent caching system for API optimization
- RESTful API with OpenAPI documentation

### 3. Unified Startup Script (`start.sh`)
- Multi-mode startup system (Docker/local/auto)
- Prerequisite checking and environment setup
- Service monitoring and graceful shutdown
- Comprehensive error handling and logging

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `OMDB_API_KEY` | OMDB API key for movie data | Required |
| `OPENAI_API_KEY` | OpenAI API key for recommendations | Required |
| `OMDB_MCP_SERVER_URL` | MCP server URL | `http://localhost:8081` |
| `SERVER_PORT` | MCP server port override | `8081` |

### Conda Environment

The app uses a conda environment named `honey` with Python 3.11. This is automatically created and managed by the startup script.

### Docker Configuration

The project includes:
- `docker-compose.yml` - Multi-service orchestration
- `omdb-mcp-server/Dockerfile` - MCP server containerization
- Health checks and restart policies

## 📋 Troubleshooting

### Common Issues

**"Connection refused" error:**
- Ensure OMDB MCP server is running: `./start.sh --status`
- Check Docker is running: `docker info`
- Restart services: `./start.sh --cleanup && ./start.sh`

**Input field text not visible:**
- This has been fixed in the latest version with improved CSS styling

**Missing API key errors:**
- Check `.env` file contains valid OMDB_API_KEY
- Verify `.streamlit/secrets.toml` has OPENAI_API_KEY

### Service Status

```bash
# Check all services
./start.sh --status

# View logs
./start.sh --logs

# Manual service checks
curl http://localhost:8081/actuator/health  # MCP server health
curl http://localhost:8501                   # Streamlit app
```

## 🤝 Development

### Project Structure

```
honey/
├── start.sh                     # Unified startup script
├── movie_recommender.py         # Main Streamlit application
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Service orchestration
├── .env                         # Environment variables
├── style/
│   └── tailwind_glassmorphism.css # UI styling
├── omdb-mcp-server/            # MCP server source
│   ├── src/main/java/          # Java source code
│   ├── Dockerfile              # Container configuration
│   └── pom.xml                 # Maven configuration
└── .streamlit/
    └── secrets.toml            # Streamlit secrets
```

### Running in Development

```bash
# Start in local development mode
./start.sh local

# Monitor logs
tail -f streamlit.log
tail -f mcp-server.log

# Restart individual services
docker-compose restart omdb-mcp-server
# or
pkill -f streamlit && streamlit run movie_recommender.py
```

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- [OMDB API](http://www.omdbapi.com/) for movie database access
- [OpenAI](https://openai.com/) for GPT-4 AI recommendations
- [Streamlit](https://streamlit.io/) for the web framework
- [Spring AI](https://docs.spring.io/spring-ai/) for MCP server implementation
- [OMDB MCP Server](https://github.com/tyrell/omdb-mcp-server) by [@tyrell](https://github.com/tyrell) - vendored and integrated for enhanced movie metadata
