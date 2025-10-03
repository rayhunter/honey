#!/bin/bash

# Honey, I Love You But I Can't Watch That - Docker Startup Script
# This script starts the OMDB MCP server in Docker and the Streamlit movie recommender app

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local port=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if port_in_use $port; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within expected time"
    return 1
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    
    # Stop Docker container
    if [ ! -z "$CONTAINER_ID" ]; then
        docker stop $CONTAINER_ID >/dev/null 2>&1 || true
        print_status "Docker container stopped"
    fi
    
    # Kill Streamlit process
    if [ ! -z "$STREAMLIT_PID" ]; then
        kill $STREAMLIT_PID 2>/dev/null || true
        print_status "Streamlit app stopped"
    fi
    
    print_success "All services stopped. Goodbye!"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Docker is installed and running
if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker Desktop or Docker Engine."
    exit 1
fi

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running. Please start Docker Desktop or Docker Engine."
    exit 1
fi
print_success "Docker is available and running"

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3."
    exit 1
fi
print_success "Python 3 is available"

# Check if conda is available
if command_exists conda; then
    print_success "Conda is available"
    CONDA_AVAILABLE=true
else
    print_warning "Conda not found, will use system Python"
    CONDA_AVAILABLE=false
fi

# Check if required environment variables are set
if [ -z "$OMDB_API_KEY" ]; then
    print_warning "OMDB_API_KEY environment variable is not set"
    print_warning "The MCP server will use a placeholder API key"
    print_warning "Set OMDB_API_KEY for full functionality"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    print_warning "OPENAI_API_KEY environment variable is not set"
    print_warning "The Streamlit app will look for it in .streamlit/secrets.toml"
fi

# Change to project directory
cd "$(dirname "$0")"
print_status "Working directory: $(pwd)"

# Start OMDB MCP Server in Docker
print_status "Starting OMDB MCP Server in Docker..."

# Check if MCP server is already running
if port_in_use 8081; then
    print_warning "Port 8081 is already in use. Assuming MCP server is running."
else
    # Build Docker image
    cd omdb-mcp-server
    
    print_status "Building Docker image for OMDB MCP Server..."
    if docker build -t omdb-mcp-server .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
    
    # Start Docker container
    print_status "Starting Docker container..."
    CONTAINER_ID=$(docker run -d \
        --name omdb-mcp-server \
        -p 8081:8081 \
        -e OMDB_API_KEY=${OMDB_API_KEY:-your-api-key-here} \
        omdb-mcp-server)
    
    cd ..
    
    # Wait for MCP server to be ready
    if wait_for_service 8081 "OMDB MCP Server"; then
        print_success "OMDB MCP Server started successfully on port 8081"
        print_status "Container ID: $CONTAINER_ID"
        print_status "View logs: docker logs $CONTAINER_ID"
    else
        print_error "Failed to start OMDB MCP Server"
        exit 1
    fi
fi

# Start Streamlit App
print_status "Starting Streamlit Movie Recommender App..."

# Check if Streamlit is already running
if port_in_use 8501; then
    print_warning "Port 8501 is already in use. Assuming Streamlit app is running."
else
    # Activate conda environment if available
    if [ "$CONDA_AVAILABLE" = true ]; then
        print_status "Activating conda environment 'honey'..."
        source $(conda info --base)/etc/profile.d/conda.sh
        if conda activate honey 2>/dev/null; then
            print_success "Conda environment 'honey' activated"
        else
            print_warning "Conda environment 'honey' not found, creating it..."
            conda create -n honey python=3.11 -y
            conda activate honey
            print_success "Conda environment 'honey' created and activated"
        fi
    fi
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    if pip install -r requirements.txt -q; then
        print_success "Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        exit 1
    fi
    
    # Start Streamlit app in background
    print_status "Starting Streamlit app..."
    streamlit run movie_recommender.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    
    # Wait for Streamlit to be ready
    if wait_for_service 8501 "Streamlit App"; then
        print_success "Streamlit Movie Recommender App started successfully on port 8501"
        print_status "Streamlit logs: streamlit.log"
    else
        print_error "Failed to start Streamlit app"
        exit 1
    fi
fi

# Display startup summary
echo
print_success "🎬 Project startup complete!"
echo
echo -e "${BLUE}Services running:${NC}"
echo -e "  • OMDB MCP Server (Docker): ${GREEN}http://localhost:8081${NC}"
echo -e "  • Streamlit App: ${GREEN}http://localhost:8501${NC}"
echo -e "  • OpenAPI Docs: ${GREEN}http://localhost:8081/swagger-ui${NC}"
echo
echo -e "${BLUE}Docker commands:${NC}"
echo -e "  • View MCP server logs: ${YELLOW}docker logs omdb-mcp-server${NC}"
echo -e "  • Stop MCP server: ${YELLOW}docker stop omdb-mcp-server${NC}"
echo -e "  • Remove container: ${YELLOW}docker rm omdb-mcp-server${NC}"
echo
echo -e "${BLUE}Logs:${NC}"
echo -e "  • Streamlit: ${YELLOW}streamlit.log${NC}"
echo
echo -e "${BLUE}To stop all services:${NC} Press Ctrl+C"
echo

# Keep script running and monitor services
print_status "Monitoring services... (Press Ctrl+C to stop)"
while true; do
    sleep 10
    
    # Check if Docker container is still running
    if [ ! -z "$CONTAINER_ID" ] && ! docker ps | grep -q $CONTAINER_ID; then
        print_error "OMDB MCP Server Docker container has stopped unexpectedly"
        break
    fi
    
    # Check if Streamlit is still running
    if [ ! -z "$STREAMLIT_PID" ] && ! kill -0 $STREAMLIT_PID 2>/dev/null; then
        print_error "Streamlit app has stopped unexpectedly"
        break
    fi
done

cleanup

