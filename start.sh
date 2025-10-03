#!/bin/bash

# Honey, I Love You But I Can't Watch That - Unified Project Startup Script
# This script provides multiple startup modes for the complete project

set -e  # Exit on any error

# Script version and info
SCRIPT_VERSION="1.0.0"
PROJECT_NAME="Honey Movie Recommender"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
OMDB_PORT=8081
STREAMLIT_PORT=8501
CONDA_ENV_NAME="honey"
PYTHON_VERSION="3.11"
MAX_STARTUP_WAIT=60
CHECK_INTERVAL=2

# Global variables for cleanup
STREAMLIT_PID=""
MCP_SERVER_PID=""
CONTAINER_ID=""
STARTUP_MODE=""

# Function to print colored output
print_banner() {
    echo -e "${CYAN}"
    echo "╭─────────────────────────────────────────────────────╮"
    echo "│                                                     │"
    echo "│  🎬 Honey, I Love You But I Can't Watch That 🎬     │"
    echo "│                                                     │"
    echo "│         Movie Recommendations for Couples          │"
    echo "│                 v${SCRIPT_VERSION}                        │"
    echo "│                                                     │"
    echo "╰─────────────────────────────────────────────────────╯"
    echo -e "${NC}"
}

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

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Function to display usage
show_usage() {
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 [MODE] [OPTIONS]"
    echo
    echo -e "${CYAN}Startup Modes:${NC}"
    echo "  compose, docker-compose    Start using Docker Compose (recommended)"
    echo "  docker                     Start OMDB server in Docker container"
    echo "  local, native             Start everything locally (requires Java & Maven)"
    echo "  auto                      Auto-detect best available mode (default)"
    echo
    echo -e "${CYAN}Options:${NC}"
    echo "  -h, --help                Show this help message"
    echo "  -v, --version             Show version information"
    echo "  --check                   Check prerequisites without starting"
    echo "  --cleanup                 Stop all services and cleanup"
    echo "  --logs                    Show logs from running services"
    echo "  --status                  Show status of all services"
    echo
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0                        # Start with auto-detected mode"
    echo "  $0 compose                # Start with Docker Compose"
    echo "  $0 local                  # Start everything locally"
    echo "  $0 --status              # Check service status"
    echo "  $0 --cleanup             # Stop all services"
    echo
    echo -e "${CYAN}Environment Variables:${NC}"
    echo "  OMDB_API_KEY             OMDB API key (required for movie details)"
    echo "  OPENAI_API_KEY           OpenAI API key (for recommendations)"
    echo
    echo -e "${CYAN}Services:${NC}"
    echo "  • OMDB MCP Server: http://localhost:${OMDB_PORT}"
    echo "  • Streamlit App:   http://localhost:${STREAMLIT_PORT}"
    echo "  • API Docs:        http://localhost:${OMDB_PORT}/swagger-ui"
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
    local max_attempts=$((MAX_STARTUP_WAIT / CHECK_INTERVAL))
    local attempt=1
    
    print_status "Waiting for $service_name to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if port_in_use $port; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep $CHECK_INTERVAL
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within ${MAX_STARTUP_WAIT} seconds"
    return 1
}

# Function to check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    local errors=0
    
    # Check Python
    if command_exists python3; then
        local python_version=$(python3 --version | grep -oE '[0-9]+\.[0-9]+')
        print_success "Python ${python_version} is available"
    else
        print_error "Python 3 is not installed"
        errors=$((errors + 1))
    fi
    
    # Check conda
    if command_exists conda; then
        print_success "Conda is available"
        CONDA_AVAILABLE=true
    else
        print_warning "Conda not found, will use system Python"
        CONDA_AVAILABLE=false
    fi
    
    # Check Docker (for compose/docker modes)
    if command_exists docker; then
        if docker info >/dev/null 2>&1; then
            print_success "Docker is available and running"
            DOCKER_AVAILABLE=true
        else
            print_warning "Docker is installed but not running"
            DOCKER_AVAILABLE=false
        fi
    else
        print_warning "Docker is not installed"
        DOCKER_AVAILABLE=false
    fi
    
    # Check docker-compose
    if command_exists docker-compose; then
        print_success "docker-compose is available"
        COMPOSE_AVAILABLE=true
    else
        print_warning "docker-compose is not available"
        COMPOSE_AVAILABLE=false
    fi
    
    # Check Java (for local mode)
    if command_exists java; then
        local java_version=$(java -version 2>&1 | head -n 1 | grep -oE '[0-9]+' | head -n 1)
        if [ "$java_version" -ge 17 ]; then
            print_success "Java ${java_version} is available"
            JAVA_AVAILABLE=true
        else
            print_warning "Java ${java_version} detected, but Java 17+ is recommended"
            JAVA_AVAILABLE=true
        fi
    else
        print_warning "Java is not installed (required for local mode)"
        JAVA_AVAILABLE=false
    fi
    
    # Check Maven (for local mode)
    if command_exists mvn; then
        print_success "Maven is available"
        MAVEN_AVAILABLE=true
    else
        print_warning "Maven is not available (required for local mode)"
        MAVEN_AVAILABLE=false
    fi
    
    # Check environment variables
    if [ -f ".env" ]; then
        print_success "Found .env file"
        source .env
    fi
    
    if [ -n "$OMDB_API_KEY" ] && [ "$OMDB_API_KEY" != "your-api-key-here" ]; then
        print_success "OMDB API key is configured"
    else
        print_warning "OMDB_API_KEY is not set or using placeholder"
        print_warning "Movie details may not be available"
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        print_success "OpenAI API key is configured"
    else
        print_warning "OPENAI_API_KEY is not set"
        print_warning "Will look for key in .streamlit/secrets.toml"
    fi
    
    return $errors
}

# Function to determine best startup mode
auto_detect_mode() {
    if [ "$DOCKER_AVAILABLE" = true ] && [ "$COMPOSE_AVAILABLE" = true ]; then
        echo "compose"
    elif [ "$DOCKER_AVAILABLE" = true ]; then
        echo "docker"
    elif [ "$JAVA_AVAILABLE" = true ] && [ "$MAVEN_AVAILABLE" = true ]; then
        echo "local"
    else
        print_error "No suitable startup mode available"
        print_error "Install Docker or Java+Maven to continue"
        exit 1
    fi
}

# Function to setup Python environment
setup_python_env() {
    print_step "Setting up Python environment..."
    
    if [ "$CONDA_AVAILABLE" = true ]; then
        print_status "Using conda environment '$CONDA_ENV_NAME'..."
        
        # Initialize conda for bash/zsh
        if [ -f "$(conda info --base)/etc/profile.d/conda.sh" ]; then
            source "$(conda info --base)/etc/profile.d/conda.sh"
        fi
        
        # Check if environment exists
        if conda env list | grep -q "^${CONDA_ENV_NAME}"; then
            print_status "Activating existing conda environment '$CONDA_ENV_NAME'..."
            conda activate "$CONDA_ENV_NAME"
        else
            print_status "Creating new conda environment '$CONDA_ENV_NAME'..."
            conda create -n "$CONDA_ENV_NAME" python="$PYTHON_VERSION" -y
            conda activate "$CONDA_ENV_NAME"
            print_success "Conda environment '$CONDA_ENV_NAME' created and activated"
        fi
    else
        print_status "Using system Python..."
    fi
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    if pip install -r requirements.txt -q; then
        print_success "Python dependencies installed successfully"
    else
        print_error "Failed to install Python dependencies"
        return 1
    fi
}

# Function to start OMDB MCP Server with Docker Compose
start_omdb_compose() {
    print_step "Starting OMDB MCP Server with Docker Compose..."
    
    if port_in_use $OMDB_PORT; then
        print_warning "Port $OMDB_PORT is already in use"
        return 0
    fi
    
    # Export environment variable for docker-compose
    export OMDB_API_KEY="${OMDB_API_KEY:-your-api-key-here}"
    
    print_status "Building and starting services with docker-compose..."
    if docker-compose up -d --build omdb-mcp-server; then
        print_success "Docker Compose services started"
        
        if wait_for_service $OMDB_PORT "OMDB MCP Server"; then
            print_success "OMDB MCP Server is running on port $OMDB_PORT"
        else
            print_error "OMDB MCP Server failed to start"
            return 1
        fi
    else
        print_error "Failed to start Docker Compose services"
        return 1
    fi
}

# Function to start OMDB MCP Server with Docker
start_omdb_docker() {
    print_step "Starting OMDB MCP Server with Docker..."
    
    if port_in_use $OMDB_PORT; then
        print_warning "Port $OMDB_PORT is already in use"
        return 0
    fi
    
    # Remove existing container if it exists
    docker rm -f omdb-mcp-server 2>/dev/null || true
    
    # Build Docker image
    print_status "Building Docker image..."
    cd omdb-mcp-server
    if docker build -t omdb-mcp-server .; then
        print_success "Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        cd ..
        return 1
    fi
    cd ..
    
    # Start container
    print_status "Starting Docker container..."
    CONTAINER_ID=$(docker run -d \
        --name omdb-mcp-server \
        -p ${OMDB_PORT}:${OMDB_PORT} \
        -e OMDB_API_KEY="${OMDB_API_KEY:-your-api-key-here}" \
        omdb-mcp-server)
    
    if wait_for_service $OMDB_PORT "OMDB MCP Server"; then
        print_success "OMDB MCP Server is running in container: $CONTAINER_ID"
    else
        print_error "OMDB MCP Server failed to start"
        return 1
    fi
}

# Function to start OMDB MCP Server locally
start_omdb_local() {
    print_step "Starting OMDB MCP Server locally..."
    
    if port_in_use $OMDB_PORT; then
        print_warning "Port $OMDB_PORT is already in use"
        return 0
    fi
    
    cd omdb-mcp-server
    
    # Set environment variable
    export OMDB_API_KEY="${OMDB_API_KEY:-your-api-key-here}"
    
    print_status "Building MCP server with Maven..."
    if mvn clean compile -q; then
        print_success "MCP server built successfully"
    else
        print_error "Failed to build MCP server"
        cd ..
        return 1
    fi
    
    print_status "Starting MCP server..."
    mvn spring-boot:run -Dspring-boot.run.jvmArguments="-Dserver.port=${OMDB_PORT}" > ../mcp-server.log 2>&1 &
    MCP_SERVER_PID=$!
    
    cd ..
    
    if wait_for_service $OMDB_PORT "OMDB MCP Server"; then
        print_success "OMDB MCP Server is running locally (PID: $MCP_SERVER_PID)"
    else
        print_error "OMDB MCP Server failed to start"
        return 1
    fi
}

# Function to start Streamlit app
start_streamlit() {
    print_step "Starting Streamlit Movie Recommender App..."
    
    if port_in_use $STREAMLIT_PORT; then
        print_warning "Port $STREAMLIT_PORT is already in use"
        return 0
    fi
    
    # Setup Python environment
    if ! setup_python_env; then
        return 1
    fi
    
    print_status "Starting Streamlit app..."
    streamlit run movie_recommender.py \
        --server.port $STREAMLIT_PORT \
        --server.address 0.0.0.0 \
        --server.headless true \
        --server.enableCORS false \
        --server.enableXsrfProtection false \
        > streamlit.log 2>&1 &
    STREAMLIT_PID=$!
    
    if wait_for_service $STREAMLIT_PORT "Streamlit App"; then
        print_success "Streamlit App is running (PID: $STREAMLIT_PID)"
    else
        print_error "Streamlit App failed to start"
        return 1
    fi
}

# Function to show service status
show_status() {
    print_step "Checking service status..."
    
    echo
    echo -e "${CYAN}Service Status:${NC}"
    
    if port_in_use $OMDB_PORT; then
        echo -e "  🟢 OMDB MCP Server: ${GREEN}Running${NC} on http://localhost:${OMDB_PORT}"
    else
        echo -e "  🔴 OMDB MCP Server: ${RED}Not Running${NC}"
    fi
    
    if port_in_use $STREAMLIT_PORT; then
        echo -e "  🟢 Streamlit App: ${GREEN}Running${NC} on http://localhost:${STREAMLIT_PORT}"
    else
        echo -e "  🔴 Streamlit App: ${RED}Not Running${NC}"
    fi
    
    echo
    
    # Check Docker containers
    if command_exists docker; then
        local containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(omdb|honey)" || true)
        if [ -n "$containers" ]; then
            echo -e "${CYAN}Docker Containers:${NC}"
            echo "$containers"
            echo
        fi
    fi
    
    # Check processes
    local processes=$(ps aux | grep -E "(streamlit|spring-boot)" | grep -v grep || true)
    if [ -n "$processes" ]; then
        echo -e "${CYAN}Running Processes:${NC}"
        echo "$processes" | awk '{print "  " $2 " - " $11 " " $12 " " $13}'
        echo
    fi
}

# Function to show logs
show_logs() {
    print_step "Showing service logs..."
    
    echo -e "${CYAN}Available log files:${NC}"
    
    if [ -f "streamlit.log" ]; then
        echo -e "  📄 Streamlit: ${YELLOW}streamlit.log${NC}"
    fi
    
    if [ -f "mcp-server.log" ]; then
        echo -e "  📄 MCP Server: ${YELLOW}mcp-server.log${NC}"
    fi
    
    if docker ps | grep -q omdb-mcp-server; then
        echo -e "  🐳 Docker MCP Server: ${YELLOW}docker logs omdb-mcp-server${NC}"
    fi
    
    if docker-compose ps | grep -q omdb-mcp-server; then
        echo -e "  🐳 Docker Compose: ${YELLOW}docker-compose logs omdb-mcp-server${NC}"
    fi
    
    echo
    echo -e "${CYAN}To view logs:${NC}"
    echo "  tail -f streamlit.log"
    echo "  tail -f mcp-server.log"
    echo "  docker logs -f omdb-mcp-server"
    echo "  docker-compose logs -f omdb-mcp-server"
}

# Function to cleanup and stop services
cleanup() {
    print_step "Shutting down services..."
    
    # Stop Streamlit
    if [ -n "$STREAMLIT_PID" ]; then
        if kill $STREAMLIT_PID 2>/dev/null; then
            print_status "Streamlit app stopped (PID: $STREAMLIT_PID)"
        fi
    fi
    
    # Stop local MCP server
    if [ -n "$MCP_SERVER_PID" ]; then
        if kill $MCP_SERVER_PID 2>/dev/null; then
            print_status "Local MCP server stopped (PID: $MCP_SERVER_PID)"
        fi
    fi
    
    # Stop Docker container
    if [ -n "$CONTAINER_ID" ]; then
        if docker stop $CONTAINER_ID >/dev/null 2>&1; then
            print_status "Docker container stopped"
        fi
    fi
    
    # Stop Docker Compose services
    if [ -f "docker-compose.yml" ] && docker-compose ps | grep -q Up; then
        docker-compose down >/dev/null 2>&1
        print_status "Docker Compose services stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "streamlit.*movie_recommender" 2>/dev/null || true
    pkill -f "spring-boot:run" 2>/dev/null || true
    
    print_success "All services stopped. Goodbye! 👋"
    exit 0
}

# Function to start services based on mode
start_services() {
    local mode=$1
    
    STARTUP_MODE=$mode
    print_step "Starting services in '$mode' mode..."
    
    case $mode in
        "compose"|"docker-compose")
            if ! start_omdb_compose; then
                return 1
            fi
            ;;
        "docker")
            if ! start_omdb_docker; then
                return 1
            fi
            ;;
        "local"|"native")
            if ! start_omdb_local; then
                return 1
            fi
            ;;
        *)
            print_error "Unknown startup mode: $mode"
            return 1
            ;;
    esac
    
    # Start Streamlit app
    if ! start_streamlit; then
        return 1
    fi
}

# Function to display startup summary
show_summary() {
    echo
    print_success "🎬 $PROJECT_NAME startup complete!"
    echo
    echo -e "${CYAN}Services Running:${NC}"
    echo -e "  🌐 Streamlit App:    ${GREEN}http://localhost:${STREAMLIT_PORT}${NC}"
    echo -e "  🔌 OMDB MCP Server: ${GREEN}http://localhost:${OMDB_PORT}${NC}"
    echo -e "  📚 API Docs:        ${GREEN}http://localhost:${OMDB_PORT}/swagger-ui${NC}"
    echo
    echo -e "${CYAN}Log Files:${NC}"
    [ -f "streamlit.log" ] && echo -e "  📄 Streamlit:    ${YELLOW}streamlit.log${NC}"
    [ -f "mcp-server.log" ] && echo -e "  📄 MCP Server:   ${YELLOW}mcp-server.log${NC}"
    echo
    echo -e "${CYAN}Commands:${NC}"
    echo -e "  📊 Check status:  ${YELLOW}$0 --status${NC}"
    echo -e "  📋 View logs:     ${YELLOW}$0 --logs${NC}"
    echo -e "  🛑 Stop services: ${YELLOW}$0 --cleanup${NC} or ${YELLOW}Ctrl+C${NC}"
    echo
    
    case $STARTUP_MODE in
        "compose"|"docker-compose")
            echo -e "${CYAN}Docker Compose Commands:${NC}"
            echo -e "  📊 Service status: ${YELLOW}docker-compose ps${NC}"
            echo -e "  📋 View logs:      ${YELLOW}docker-compose logs -f omdb-mcp-server${NC}"
            echo -e "  🔄 Restart:        ${YELLOW}docker-compose restart${NC}"
            ;;
        "docker")
            echo -e "${CYAN}Docker Commands:${NC}"
            echo -e "  📋 View logs:  ${YELLOW}docker logs omdb-mcp-server${NC}"
            echo -e "  🔄 Restart:    ${YELLOW}docker restart omdb-mcp-server${NC}"
            ;;
    esac
    echo
}

# Function to monitor services
monitor_services() {
    print_status "Monitoring services... (Press Ctrl+C to stop)"
    
    while true; do
        sleep 10
        
        # Check Streamlit
        if [ -n "$STREAMLIT_PID" ] && ! kill -0 $STREAMLIT_PID 2>/dev/null; then
            print_error "Streamlit app stopped unexpectedly"
            break
        fi
        
        # Check local MCP server
        if [ -n "$MCP_SERVER_PID" ] && ! kill -0 $MCP_SERVER_PID 2>/dev/null; then
            print_error "Local MCP server stopped unexpectedly"
            break
        fi
        
        # Check Docker container
        if [ -n "$CONTAINER_ID" ] && ! docker ps -q --no-trunc | grep -q $CONTAINER_ID; then
            print_error "Docker MCP server stopped unexpectedly"
            break
        fi
        
        # Check Docker Compose
        if [ "$STARTUP_MODE" = "compose" ] && ! docker-compose ps | grep -q Up; then
            print_error "Docker Compose services stopped unexpectedly"
            break
        fi
    done
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

# Change to script directory
cd "$(dirname "$0")"

# Main script logic
main() {
    # Parse command line arguments
    case "${1:-}" in
        "-h"|"--help")
            show_usage
            exit 0
            ;;
        "-v"|"--version")
            echo "$PROJECT_NAME v$SCRIPT_VERSION"
            exit 0
            ;;
        "--check")
            print_banner
            check_prerequisites
            exit $?
            ;;
        "--cleanup")
            print_banner
            cleanup
            ;;
        "--status")
            print_banner
            show_status
            exit 0
            ;;
        "--logs")
            print_banner
            show_logs
            exit 0
            ;;
        "compose"|"docker-compose"|"docker"|"local"|"native")
            MODE="$1"
            ;;
        "auto"|"")
            MODE="auto"
            ;;
        *)
            print_error "Unknown option: $1"
            echo
            show_usage
            exit 1
            ;;
    esac
    
    # Display banner
    print_banner
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Auto-detect mode if needed
    if [ "$MODE" = "auto" ]; then
        MODE=$(auto_detect_mode)
        print_status "Auto-detected startup mode: $MODE"
    fi
    
    echo
    print_step "Starting $PROJECT_NAME in '$MODE' mode..."
    echo
    
    # Start services
    if start_services "$MODE"; then
        show_summary
        monitor_services
    else
        print_error "Failed to start services"
        cleanup
        exit 1
    fi
}

# Run main function
main "$@"
