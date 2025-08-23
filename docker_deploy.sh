#!/bin/bash

# Docker Deployment Script for AI Customer Finder
# This script helps deploy and manage the application using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_status "Docker is installed ✓"
}

# Check if docker-compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_warning "docker-compose is not installed. Trying 'docker compose' command..."
        if ! docker compose version &> /dev/null; then
            print_error "Neither docker-compose nor 'docker compose' is available."
            exit 1
        fi
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
    print_status "Docker Compose is available ✓"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_status "Created .env file. Please edit it with your API keys."
            print_warning "Edit .env file and add your SERPER_API_KEY before running the application."
        else
            print_error ".env file not found and no .env.example available."
            print_status "Creating a basic .env file..."
            cat > .env << EOF
# Serper.dev API Key (Required for search operations)
SERPER_API_KEY=your_api_key_here

# LLM Provider Configuration (Optional, for better content extraction)
LLM_PROVIDER=none

# OpenAI API Configuration
OPENAI_API_KEY=

# Anthropic API Configuration
ANTHROPIC_API_KEY=

# Google API Configuration
GOOGLE_API_KEY=

# Huoshan/Volcano API Configuration (for Chinese users)
ARK_API_KEY=
ARK_BASE_URL=
ARK_MODEL=

# Browser Configuration
HEADLESS=true
TIMEOUT=15000
VISIT_CONTACT_PAGE=false
EOF
            print_warning "Please edit .env file and add your API keys."
        fi
    else
        print_status ".env file exists ✓"
        # Check if SERPER_API_KEY is configured
        if grep -q "^SERPER_API_KEY=your_api_key_here" .env || grep -q "^SERPER_API_KEY=$" .env; then
            print_warning "SERPER_API_KEY is not configured in .env file!"
            print_warning "Please add your Serper.dev API key before starting the application."
        fi
    fi
}

# Create output directories
create_directories() {
    print_status "Creating output directories..."
    mkdir -p output/company output/contact output/employee
    print_status "Output directories created ✓"
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t ai-customer-finder .
    print_status "Docker image built successfully ✓"
}

# Start services
start_services() {
    print_status "Starting services with Docker Compose..."
    $COMPOSE_CMD up -d
    print_status "Services started successfully ✓"
    print_status "Application is running at: http://localhost:8501"
    print_status "To view logs: $COMPOSE_CMD logs -f"
}

# Stop services
stop_services() {
    print_status "Stopping services..."
    $COMPOSE_CMD down
    print_status "Services stopped ✓"
}

# View logs
view_logs() {
    print_status "Viewing application logs..."
    $COMPOSE_CMD logs -f
}

# Restart services
restart_services() {
    print_status "Restarting services..."
    $COMPOSE_CMD restart
    print_status "Services restarted ✓"
}

# Main menu
main_menu() {
    echo ""
    echo "======================================"
    echo "   AI Customer Finder - Docker Deploy"
    echo "======================================"
    echo ""
    echo "Select an option:"
    echo "1) Full deployment (build and start)"
    echo "2) Start services"
    echo "3) Stop services"
    echo "4) Restart services"
    echo "5) View logs"
    echo "6) Rebuild image"
    echo "7) Exit"
    echo ""
    read -p "Enter your choice (1-7): " choice
    
    case $choice in
        1)
            check_docker
            check_docker_compose
            check_env_file
            create_directories
            build_image
            start_services
            ;;
        2)
            check_docker_compose
            start_services
            ;;
        3)
            check_docker_compose
            stop_services
            ;;
        4)
            check_docker_compose
            restart_services
            ;;
        5)
            check_docker_compose
            view_logs
            ;;
        6)
            check_docker
            build_image
            ;;
        7)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid option. Please select 1-7."
            main_menu
            ;;
    esac
}

# Script entry point
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  --start      Start services"
    echo "  --stop       Stop services"
    echo "  --restart    Restart services"
    echo "  --logs       View logs"
    echo "  --build      Build Docker image"
    echo "  --help       Show this help message"
    echo ""
    echo "Without options, interactive menu will be shown."
    exit 0
fi

# Handle command line arguments
case "$1" in
    --start)
        check_docker_compose
        start_services
        ;;
    --stop)
        check_docker_compose
        stop_services
        ;;
    --restart)
        check_docker_compose
        restart_services
        ;;
    --logs)
        check_docker_compose
        view_logs
        ;;
    --build)
        check_docker
        build_image
        ;;
    "")
        main_menu
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac