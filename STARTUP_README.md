# 🎬 Project Startup Guide

This guide explains how to start your "Honey, I Love You But I Can't Watch That" movie recommendation project.

## 🚀 Quick Start (Recommended)

Use the Docker Compose startup script for the easiest experience:

```bash
./start_project_compose.sh
```

This will:
- Start the OMDB MCP server in Docker
- Start the Streamlit movie recommender app
- Handle all dependencies automatically

## 🔧 Alternative Startup Methods

### Option 1: Docker Compose (Recommended)
```bash
./start_project_compose.sh
```

### Option 2: Manual Docker
```bash
./start_project_docker.sh
```

### Option 3: Manual (requires Java/Maven)
```bash
./start_project.sh
```

## 📋 Prerequisites

### Required
- **Docker Desktop** or **Docker Engine** (for MCP server)
- **Python 3.8+** (for Streamlit app)
- **Conda** (recommended for Python environment management)

### Optional
- **OMDB_API_KEY** environment variable (for full OMDB API functionality)
- **OPENAI_API_KEY** environment variable (for AI-powered recommendations)

## 🌐 Services

Once started, you'll have access to:

- **Streamlit App**: http://localhost:8501
- **OMDB MCP Server**: http://localhost:8081
- **OpenAPI Documentation**: http://localhost:8081/swagger-ui

## 🛑 Stopping Services

### Graceful Shutdown
Press `Ctrl+C` in the terminal running the startup script.

### Manual Stop
```bash
# Stop Docker services
docker-compose down

# Stop Streamlit (if running separately)
pkill -f streamlit
```

## 📊 Monitoring

### View Logs
```bash
# MCP Server logs
docker-compose logs -f omdb-mcp-server

# Streamlit logs
tail -f streamlit.log
```

### Check Status
```bash
# Docker services status
docker-compose ps

# Port usage
lsof -i :8081  # MCP Server
lsof -i :8501  # Streamlit
```

## 🔍 Troubleshooting

### Port Already in Use
If you see "Port already in use" errors:
```bash
# Find what's using the port
lsof -i :8081
lsof -i :8501

# Stop conflicting services
docker-compose down
pkill -f streamlit
```

### Docker Issues
```bash
# Restart Docker Desktop
# Or restart Docker daemon on Linux
sudo systemctl restart docker

# Clean up Docker
docker system prune -f
```

### Conda Environment Issues
```bash
# Recreate conda environment
conda env remove -n honey
conda create -n honey python=3.11
conda activate honey
pip install -r requirements.txt
```

## 🐳 Docker Commands

### Build and Start
```bash
docker-compose up -d --build
```

### View Logs
```bash
docker-compose logs -f omdb-mcp-server
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

## 🔑 Environment Variables

Set these for full functionality:

```bash
export OMDB_API_KEY="your-omdb-api-key"
export OPENAI_API_KEY="your-openai-api-key"
```

Or create a `.env` file:
```bash
OMDB_API_KEY=your-omdb-api-key
OPENAI_API_KEY=your-openai-api-key
```

## 📁 Project Structure

```
honey/
├── start_project_compose.sh    # 🚀 Recommended startup script
├── start_project_docker.sh     # Manual Docker startup
├── start_project.sh            # Manual startup (requires Java/Maven)
├── docker-compose.yml          # Docker Compose configuration
├── movie_recommender.py        # Main Streamlit app
├── omdb-mcp-server/            # OMDB MCP server (Java/Spring Boot)
│   ├── Dockerfile
│   └── src/
└── requirements.txt             # Python dependencies
```

## 🎯 What Each Script Does

### `start_project_compose.sh` (Recommended)
- Uses Docker Compose for MCP server
- Starts Streamlit app in conda environment
- Automatic dependency management
- Clean shutdown handling

### `start_project_docker.sh`
- Manual Docker commands for MCP server
- Starts Streamlit app in conda environment
- More control over Docker operations

### `start_project.sh`
- Requires Java 17+ and Maven
- Builds MCP server from source
- Starts Streamlit app in conda environment
- Useful for development/debugging

## 🚨 Common Issues

1. **"Docker daemon not running"** → Start Docker Desktop
2. **"Port already in use"** → Stop conflicting services
3. **"Conda environment not found"** → Script will create it automatically
4. **"MCP server failed to start"** → Check Docker logs with `docker-compose logs`

## 💡 Tips

- Always use the same terminal session for starting and stopping services
- Check logs if services don't start properly
- Use `docker-compose down` to clean up Docker resources
- The startup scripts handle most edge cases automatically

---

**Happy movie watching! 🍿✨**

