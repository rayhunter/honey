#!/bin/bash

# Honey, I Love You But I Can't Watch That - Project Stop Script
# This script stops all running services (OMDB MCP server and Streamlit app)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
OMDB_PORT=8081
STREAMLIT_PORT=8501

# Function to print colored output
print_banner() {
    echo -e "${CYAN}"
    echo "╭─────────────────────────────────────────────────────╮"
    echo "│                                                     │"
    echo "│  🛑 Stopping Honey Movie Recommender Services      │"
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to stop Streamlit processes
stop_streamlit() {
    print_status "Stopping Streamlit app..."

    local stopped=0

    # Try to kill by port
    if port_in_use $STREAMLIT_PORT; then
        local pids=$(lsof -ti :$STREAMLIT_PORT)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null || true
            stopped=$((stopped + 1))
        fi
    fi

    # Try to kill by process name
    if pgrep -f "streamlit.*movie_recommender" >/dev/null 2>&1; then
        pkill -9 -f "streamlit.*movie_recommender" 2>/dev/null || true
        stopped=$((stopped + 1))
    fi

    # Clean up log file indicator
    if [ -f "streamlit.log" ]; then
        print_status "Streamlit logs saved in: streamlit.log"
    fi

    if [ $stopped -gt 0 ]; then
        print_success "Streamlit app stopped"
    else
        print_warning "No Streamlit app was running"
    fi
}

# Function to stop Docker Compose services
stop_docker_compose() {
    print_status "Checking for Docker Compose services..."

    if [ ! -f "docker-compose.yml" ]; then
        print_warning "No docker-compose.yml found"
        return 0
    fi

    if ! command_exists docker-compose; then
        print_warning "docker-compose not available"
        return 0
    fi

    # Check if any compose services are running
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        print_status "Stopping Docker Compose services..."
        docker-compose down 2>/dev/null
        print_success "Docker Compose services stopped"
    else
        print_warning "No Docker Compose services were running"
    fi
}

# Function to stop Docker container
stop_docker_container() {
    print_status "Checking for Docker containers..."

    if ! command_exists docker; then
        print_warning "Docker not available"
        return 0
    fi

    local stopped=0

    # Check for container by name
    if docker ps -q -f name=omdb-mcp-server | grep -q .; then
        print_status "Stopping Docker container: omdb-mcp-server"
        docker stop omdb-mcp-server >/dev/null 2>&1
        docker rm omdb-mcp-server >/dev/null 2>&1 || true
        stopped=$((stopped + 1))
    fi

    # Check for container by port
    local container_id=$(docker ps -q --filter "publish=$OMDB_PORT")
    if [ -n "$container_id" ]; then
        print_status "Stopping Docker container on port $OMDB_PORT: $container_id"
        docker stop $container_id >/dev/null 2>&1
        stopped=$((stopped + 1))
    fi

    if [ $stopped -gt 0 ]; then
        print_success "Docker container(s) stopped"
    else
        print_warning "No Docker containers were running"
    fi
}

# Function to stop local OMDB MCP server
stop_local_mcp() {
    print_status "Stopping local OMDB MCP Server..."

    local stopped=0

    # Try to kill by port
    if port_in_use $OMDB_PORT; then
        local pids=$(lsof -ti :$OMDB_PORT)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill -9 2>/dev/null || true
            stopped=$((stopped + 1))
        fi
    fi

    # Try to kill by process name
    if pgrep -f "spring-boot:run" >/dev/null 2>&1; then
        pkill -9 -f "spring-boot:run" 2>/dev/null || true
        stopped=$((stopped + 1))
    fi

    # Try to kill Java processes on OMDB port
    if pgrep -f "omdb-mcp-server" >/dev/null 2>&1; then
        pkill -9 -f "omdb-mcp-server" 2>/dev/null || true
        stopped=$((stopped + 1))
    fi

    # Clean up log file indicator
    if [ -f "omdb-mcp-server/mcp-server.log" ]; then
        print_status "MCP Server logs saved in: omdb-mcp-server/mcp-server.log"
    fi

    if [ -f "mcp-server.log" ]; then
        print_status "MCP Server logs saved in: mcp-server.log"
    fi

    if [ $stopped -gt 0 ]; then
        print_success "Local OMDB MCP Server stopped"
    else
        print_warning "No local OMDB MCP Server was running"
    fi
}

# Function to verify all services are stopped
verify_stopped() {
    print_status "Verifying all services are stopped..."

    local all_stopped=true

    if port_in_use $STREAMLIT_PORT; then
        print_warning "Port $STREAMLIT_PORT is still in use"
        all_stopped=false
    fi

    if port_in_use $OMDB_PORT; then
        print_warning "Port $OMDB_PORT is still in use"
        all_stopped=false
    fi

    if $all_stopped; then
        print_success "All services verified stopped"
    else
        print_warning "Some services may still be running"
        print_status "Run './stop.sh' again or manually kill the processes"
    fi
}

# Function to show final status
show_summary() {
    echo
    print_success "🛑 All services stopped!"
    echo
    echo -e "${CYAN}Service Status:${NC}"

    if port_in_use $STREAMLIT_PORT; then
        echo -e "  🔴 Streamlit App (port $STREAMLIT_PORT): ${YELLOW}Still running${NC}"
    else
        echo -e "  ✅ Streamlit App (port $STREAMLIT_PORT): ${GREEN}Stopped${NC}"
    fi

    if port_in_use $OMDB_PORT; then
        echo -e "  🔴 OMDB MCP Server (port $OMDB_PORT): ${YELLOW}Still running${NC}"
    else
        echo -e "  ✅ OMDB MCP Server (port $OMDB_PORT): ${GREEN}Stopped${NC}"
    fi

    echo
    echo -e "${CYAN}To start services again:${NC}"
    echo -e "  ${YELLOW}./start.sh${NC}                    # Auto-detect mode"
    echo -e "  ${YELLOW}./start_project.sh${NC}            # Local mode"
    echo -e "  ${YELLOW}./start_project_docker.sh${NC}     # Docker mode"
    echo -e "  ${YELLOW}./start_project_compose.sh${NC}    # Docker Compose mode"
    echo
}

# Main execution
main() {
    # Display banner
    print_banner

    # Change to script directory
    cd "$(dirname "$0")"
    print_status "Working directory: $(pwd)"
    echo

    # Stop all services
    stop_streamlit
    echo

    stop_docker_compose
    echo

    stop_docker_container
    echo

    stop_local_mcp
    echo

    # Verify everything is stopped
    verify_stopped

    # Show summary
    show_summary
}

# Run main function
main "$@"
