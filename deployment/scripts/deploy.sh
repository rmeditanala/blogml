#!/bin/bash

# =============================================================================
# BlogML Production Deployment Script
# =============================================================================
# This script automates the deployment of BlogML to Docker Swarm
# =============================================================================
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="blogml"
SCRIPT_DIR="$(dirname "$0")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REGISTRY="${DOCKER_REGISTRY:-}"  # Optional: Set your registry URL

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "========================================"
    print_header "BlogML Production Deployment"
    print_header "========================================"
    echo

    print_status "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check Docker Swarm
    if ! docker info | grep -q "Swarm: active"; then
        print_error "Docker Swarm is not initialized. Run 'docker swarm init' first."
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f "$PROJECT_DIR/.env" ]; then
        print_error ".env file not found. Copy .env.example to .env and configure it."
        exit 1
    fi

    # Load environment variables
    source "$PROJECT_DIR/.env"

    # Check required variables
    if [ -z "$HF_TOKEN" ]; then
        print_error "HF_TOKEN is not set in .env file."
        exit 1
    fi

    print_status "Prerequisites check passed!"
    echo
}

# Create Docker secrets
create_secrets() {
    print_header "Creating Docker Secrets..."

    # Function to create secret if it doesn't exist
    create_secret_if_not_exists() {
        local secret_name="$1"
        local secret_value="$2"

        if ! docker secret ls | grep -q "$secret_name"; then
            echo "$secret_value" | docker secret create "$secret_name" -
            print_status "Created secret: $secret_name"
        else
            print_warning "Secret $secret_name already exists, skipping..."
        fi
    }

    # Generate or use existing passwords
    MYSQL_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-$(openssl rand -base64 32)}"
    MYSQL_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 32)}"
    APP_KEY="${APP_KEY:-$(openssl rand -base64 32)}"

    # Create secrets
    create_secret_if_not_exists "mysql_root_password" "$MYSQL_ROOT_PASSWORD"
    create_secret_if_not_exists "mysql_password" "$MYSQL_PASSWORD"
    create_secret_if_not_exists "app_key" "$APP_KEY"
    create_secret_if_not_exists "hf_token" "$HF_TOKEN"

    # Create SSL secrets (optional - skip if files don't exist)
    if [ -f "$PROJECT_DIR/nginx/ssl/cert.pem" ]; then
        docker secret create ssl_cert "$PROJECT_DIR/nginx/ssl/cert.pem" 2>/dev/null || print_warning "SSL cert secret already exists"
    fi

    if [ -f "$PROJECT_DIR/nginx/ssl/key.pem" ]; then
        docker secret create ssl_key "$PROJECT_DIR/nginx/ssl/key.pem" 2>/dev/null || print_warning "SSL key secret already exists"
    fi

    print_status "Secrets setup complete!"
    echo
}

# Create data directories
create_directories() {
    print_header "Creating Data Directories..."

    local data_dirs=(
        "/opt/blogml/data/mysql"
        "/opt/blogml/data/redis"
        "/opt/blogml/data/backend/storage"
        "/opt/blogml/data/ml-models"
        "/opt/blogml/logs/backend"
        "/opt/blogml/logs/ml-service"
        "/opt/blogml/logs/nginx"
    )

    for dir in "${data_dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            sudo mkdir -p "$dir"
            sudo chown -R $USER:$USER /opt/blogml/data
            sudo chown -R $USER:$USER /opt/blogml/logs
            print_status "Created directory: $dir"
        else
            print_warning "Directory already exists: $dir"
        fi
    done

    print_status "Directories setup complete!"
    echo
}

# Build Docker images
build_images() {
    print_header "Building Docker Images..."

    # Build frontend
    print_status "Building frontend image..."
    docker build -t blogml/frontend:latest "$PROJECT_DIR/../frontend" -f "$PROJECT_DIR/frontend/Dockerfile"

    # Build backend
    print_status "Building backend image..."
    docker build -t blogml/backend:latest "$PROJECT_DIR/../backend" -f "$PROJECT_DIR/backend/Dockerfile"

    # Build ML service
    print_status "Building ML service image..."
    docker build -t blogml/ml-service:latest "$PROJECT_DIR/../ml-service" -f "$PROJECT_DIR/ml-service/Dockerfile"

    # Tag for registry if provided
    if [ -n "$REGISTRY" ]; then
        print_status "Tagging images for registry: $REGISTRY"
        docker tag blogml/frontend:latest "$REGISTRY/blogml/frontend:latest"
        docker tag blogml/backend:latest "$REGISTRY/blogml/backend:latest"
        docker tag blogml/ml-service:latest "$REGISTRY/blogml/ml-service:latest"

        # Push to registry
        print_status "Pushing images to registry..."
        docker push "$REGISTRY/blogml/frontend:latest"
        docker push "$REGISTRY/blogml/backend:latest"
        docker push "$REGISTRY/blogml/ml-service:latest"
    fi

    print_status "Image build complete!"
    echo
}

# Deploy stack
deploy_stack() {
    print_header "Deploying Docker Stack..."

    cd "$PROJECT_DIR"

    # Remove existing stack if it exists
    if docker stack ls | grep -q "$STACK_NAME"; then
        print_warning "Removing existing stack: $STACK_NAME"
        docker stack rm "$STACK_NAME"
        print_status "Waiting for stack to be removed..."
        sleep 30
    fi

    # Deploy new stack
    print_status "Deploying new stack: $STACK_NAME"
    docker stack deploy -c docker-stack.yml "$STACK_NAME"

    print_status "Stack deployment initiated!"
    echo
}

# Monitor deployment
monitor_deployment() {
    print_header "Monitoring Deployment..."

    print_status "Waiting for services to start..."
    sleep 10

    # Check service status
    while true; do
        local services=$(docker service ls --filter label=com.docker.stack.namespace="$STACK_NAME" --format "{{.Name}} {{.Replicas}}")
        local all_ready=true

        echo "$services" | while read -r service replicas; do
            local service_name=$(echo "$service" | cut -d' ' -f1)
            local replica_count=$(echo "$replicas" | cut -d'/' -f1)
            local total_replicas=$(echo "$replicas" | cut -d'/' -f2)

            if [ "$replica_count" != "$total_replicas" ] || [ "$total_replicas" = "0" ]; then
                all_ready=false
                print_status "$service_name: $replicas"
            else
                print_status "$service_name: $replicas ✓"
            fi
        done

        if $all_ready; then
            break
        fi

        print_status "Waiting for all services to be ready..."
        sleep 10
    done

    print_status "All services are ready!"
    echo
}

# Show service information
show_info() {
    print_header "Deployment Information"
    echo
    print_status "Services:"
    docker service ls --filter label=com.docker.stack.namespace="$STACK_NAME"
    echo

    print_status "Stack Name: $STACK_NAME"
    print_status "Access URLs:"
    print_status "  - Frontend: https://localhost"
    print_status "  - Backend API: https://localhost/api"
    print_status "  - ML Service: https://localhost/ml"
    print_status "  - Health Check: https://localhost/health"
    echo

    print_status "Useful Commands:"
    print_status "  - View logs: docker service logs $STACK_NAME_backend"
    print_status "  - Scale services: docker service scale $STACK_NAME_backend=5"
    print_status "  - Remove stack: docker stack rm $STACK_NAME"
    print_status "  - List services: docker service ls"
    echo

    print_header "Deployment Complete! 🎉"
}

# Main execution
main() {
    check_prerequisites
    create_secrets
    create_directories
    build_images
    deploy_stack
    monitor_deployment
    show_info
}

# Handle script arguments
case "${1:-}" in
    --build-only)
        check_prerequisites
        build_images
        ;;
    --secrets-only)
        check_prerequisites
        create_secrets
        ;;
    --deploy-only)
        check_prerequisites
        deploy_stack
        monitor_deployment
        ;;
    *)
        main
        ;;
esac