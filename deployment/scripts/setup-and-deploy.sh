#!/bin/bash

# =============================================================================
# BlogML Complete Setup and Deployment Script
# =============================================================================
# This script handles everything from Docker installation to full deployment
# =============================================================================
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="blogml"
SCRIPT_DIR="$(dirname "$0")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"

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

print_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${CYAN}✅ $1${NC}"
}

# Show animation
show_spinner() {
    local pid=$!
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

# Print welcome message
print_welcome() {
    clear
    print_header "╔══════════════════════════════════════════════════════════════╗"
    print_header "║                  BlogML Automated Setup                   ║"
    print_header "║              Docker Swarm Deployment Script                ║"
    print_header "╚══════════════════════════════════════════════════════════════╝"
    echo
    print_status "This script will automatically:"
    echo "  🔍 Check and install Docker if needed"
    echo "  🐳 Initialize Docker Swarm"
    echo "  🔐 Setup environment and secrets"
    echo "  🏗️  Build all Docker images"
    echo "  📦 Deploy to Docker Swarm"
    echo "  ✅ Monitor and verify deployment"
    echo
    print_warning "⚠️  This will require sudo privileges for system setup"
    echo
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled."
        exit 0
    fi
}

# Install Docker if not present
install_docker() {
    print_step "Installing Docker..."

    if command -v docker &> /dev/null; then
        print_success "Docker is already installed"
        docker --version
    else
        print_status "Installing Docker..."

        # Detect OS
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            if command -v apt-get &> /dev/null; then
                # Ubuntu/Debian
                curl -fsSL https://get.docker.com -o get-docker.sh &
                show_spinner
                wait
                sudo sh get-docker.sh
                sudo usermod -aG docker $USER
                rm get-docker.sh
            elif command -v yum &> /dev/null; then
                # CentOS/RHEL
                sudo yum install -y yum-utils
                sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
                sudo systemctl start docker
                sudo systemctl enable docker
                sudo usermod -aG docker $USER
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            print_error "Please install Docker Desktop for Mac from: https://www.docker.com/products/docker-desktop"
            exit 1
        else
            print_error "Unsupported operating system. Please install Docker manually."
            exit 1
        fi

        print_success "Docker installation completed!"
    fi
}

# Initialize Docker Swarm
init_docker_swarm() {
    print_step "Initializing Docker Swarm..."

    # Check if Swarm is already active
    if docker info | grep -q "Swarm: active"; then
        print_success "Docker Swarm is already active"
    else
        # Get the IP address
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            IP_ADDR=$(hostname -I | awk '{print $1}')
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            IP_ADDR=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
        fi

        print_status "Initializing Docker Swarm with IP: $IP_ADDR"
        docker swarm init --advertise-addr $IP_ADDR || {
            print_error "Failed to initialize Docker Swarm"
            exit 1
        }

        print_success "Docker Swarm initialized successfully!"
    fi
}

# Setup environment
setup_environment() {
    print_step "Setting up environment..."

    # Create .env file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        print_status "Creating .env file from template..."
        cp "$PROJECT_DIR/.env.example" "$ENV_FILE"

        # Generate random passwords and keys
        MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        MYSQL_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        APP_KEY=$(openssl rand -base64 32)

        # Update .env file
        sed -i.bak "s/DB_ROOT_PASSWORD=.*/DB_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD/" "$ENV_FILE"
        sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=$MYSQL_PASSWORD/" "$ENV_FILE"
        sed -i.bak "s/root.*/$MYSQL_ROOT_PASSWORD/" "$ENV_FILE"
        sed -i.bak "s/blogml_password.*/$MYSQL_PASSWORD/" "$ENV_FILE"
        sed -i.bak "s#APP_KEY=.*#APP_KEY=base64:$APP_KEY#" "$ENV_FILE"

        print_warning "⚠️  Please edit $ENV_FILE and set your HF_TOKEN"
        print_warning "⚠️  Your Hugging Face token is required for ML models"

        read -p "Do you want to edit the .env file now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} "$ENV_FILE"
        fi
    else
        print_success "Environment file already exists"
    fi

    # Source environment variables
    source "$ENV_FILE"

    # Verify HF_TOKEN is set
    if [ -z "$HF_TOKEN" ]; then
        print_error "HF_TOKEN is not set in .env file. Please edit it before continuing."
        exit 1
    fi

    print_success "Environment setup completed!"
}

# Generate SSL certificates
generate_ssl() {
    print_step "Generating SSL certificates..."

    if [ -f "$PROJECT_DIR/nginx/ssl/cert.pem" ] && [ -f "$PROJECT_DIR/nginx/ssl/key.pem" ]; then
        print_success "SSL certificates already exist"
    else
        print_status "Running SSL generation script..."
        "$PROJECT_DIR/scripts/generate-ssl.sh"
        print_success "SSL certificates generated!"
    fi
}

# Create data directories
create_directories() {
    print_step "Creating data directories..."

    local dirs=(
        "/opt/blogml/data/mysql"
        "/opt/blogml/data/redis"
        "/opt/blogml/data/backend/storage"
        "/opt/blogml/data/ml-models"
        "/opt/blogml/logs/backend"
        "/opt/blogml/logs/ml-service"
        "/opt/blogml/logs/nginx"
    )

    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            sudo mkdir -p "$dir"
            sudo chown -R $USER:$USER /opt/blogml/data 2>/dev/null || true
            sudo chown -R $USER:$USER /opt/blogml/logs 2>/dev/null || true
            print_status "Created directory: $dir"
        fi
    done

    print_success "Data directories created!"
}

# Create Docker secrets
create_secrets() {
    print_step "Creating Docker secrets..."

    # Function to create secret if it doesn't exist
    create_secret() {
        local secret_name="$1"
        local secret_value="$2"

        if ! docker secret ls | grep -q "$secret_name"; then
            echo "$secret_value" | docker secret create "$secret_name" - 2>/dev/null
            print_status "Created secret: $secret_name"
        else
            print_status "Secret already exists: $secret_name"
        fi
    }

    # Create secrets
    create_secret "mysql_root_password" "$DB_ROOT_PASSWORD"
    create_secret "db_password" "$DB_PASSWORD"
    create_secret "mail_password" "$MAIL_PASSWORD"
    create_secret "app_key" "$APP_KEY"
    create_secret "hf_token" "$HF_TOKEN"

    # Create SSL secrets
    if [ -f "$PROJECT_DIR/nginx/ssl/cert.pem" ]; then
        docker secret create ssl_cert "$PROJECT_DIR/nginx/ssl/cert.pem" 2>/dev/null || print_status "SSL cert secret exists"
    fi

    if [ -f "$PROJECT_DIR/nginx/ssl/key.pem" ]; then
        docker secret create ssl_key "$PROJECT_DIR/nginx/ssl/key.pem" 2>/dev/null || print_status "SSL key secret exists"
    fi

    print_success "Docker secrets created!"
}

# Build Docker images
build_images() {
    print_step "Building Docker images..."

    # Build frontend image
    print_status "Building frontend image..."
    docker build -t blogml/frontend:latest "$PROJECT_DIR/../frontend" -f "$PROJECT_DIR/frontend/Dockerfile" &
    show_spinner
    wait
    print_success "Frontend image built!"

    # Build backend image
    print_status "Building backend image..."
    docker build -t blogml/backend:latest "$PROJECT_DIR/../backend" -f "$PROJECT_DIR/backend/Dockerfile" &
    show_spinner
    wait
    print_success "Backend image built!"

    # Build ML service image
    print_status "Building ML service image..."
    docker build -t blogml/ml-service:latest "$PROJECT_DIR/../ml-service" -f "$PROJECT_DIR/ml-service/Dockerfile" &
    show_spinner
    wait
    print_success "ML service image built!"

    print_success "All Docker images built successfully!"
}

# Deploy to Docker Swarm
deploy_stack() {
    print_step "Deploying to Docker Swarm..."

    cd "$PROJECT_DIR"

    # Remove existing stack if it exists
    if docker stack ls | grep -q "$STACK_NAME"; then
        print_warning "Removing existing stack..."
        docker stack rm "$STACK_NAME"
        sleep 10
    fi

    # Deploy the stack
    print_status "Deploying stack: $STACK_NAME"
    docker stack deploy -c docker-stack.yml "$STACK_NAME"

    print_success "Stack deployment started!"
}

# Monitor deployment
monitor_deployment() {
    print_step "Monitoring deployment..."

    print_status "Waiting for services to start..."
    sleep 15

    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        local services_ready=true

        echo "Checking service status (attempt $((attempt + 1))/$max_attempts)..."

        while IFS= read -r service; do
            local service_name=$(echo "$service" | awk '{print $1}')
            local replicas=$(echo "$service" | awk '{print $4}')
            local current=$(echo "$replicas" | cut -d'/' -f1)
            local desired=$(echo "$replicas" | cut -d'/' -f2)

            if [ "$current" != "$desired" ] || [ "$desired" = "0" ]; then
                services_ready=false
                print_status "$service_name: $replicas ⏳"
            else
                print_success "$service_name: $replicas ✅"
            fi
        done <<< "$(docker service ls --filter label=com.docker.stack.namespace="$STACK_NAME" --format "{{.Name}} {{.Replicas}}")"

        if $services_ready; then
            break
        fi

        sleep 10
        ((attempt++))
    done

    if [ $attempt -eq $max_attempts ]; then
        print_warning "Deployment monitoring timeout. Services may still be starting."
    else
        print_success "All services are ready!"
    fi
}

# Show final status and access information
show_final_status() {
    print_header "🎉 Deployment Complete!"
    echo
    print_status "BlogML has been successfully deployed to Docker Swarm!"
    echo

    print_header "📋 Service Status:"
    docker service ls --filter label=com.docker.stack.namespace="$STACK_NAME"
    echo

    print_header "🌐 Access URLs:"
    print_status "Frontend:        https://localhost"
    print_status "Backend API:     https://localhost/api"
    print_status "ML Service:      https://localhost/ml"
    print_status "Health Check:    https://localhost/health"
    echo

    print_header "🔧 Useful Commands:"
    echo "  View logs:       docker service logs $STACK_NAME_backend"
    echo "  Scale backend:   docker service scale $STACK_NAME_backend=5"
    echo "  Scale frontend:  docker service scale $STACK_NAME_frontend=3"
    echo "  Scale ML:        docker service scale $STACK_NAME_ml-service=2"
    echo "  Remove stack:    docker stack rm $STACK_NAME"
    echo "  List services:   docker service ls"
    echo

    print_header "📊 Monitoring:"
    print_status "Stack name: $STACK_NAME"
    print_status "Monitor with: docker service ps $STACK_NAME"
    echo

    print_success "🚀 Your BlogML application is now running!"
}

# Main execution
main() {
    print_welcome
    install_docker
    init_docker_swarm
    setup_environment
    generate_ssl
    create_directories
    create_secrets
    build_images
    deploy_stack
    monitor_deployment
    show_final_status
}

# Error handling
trap 'print_error "Script failed at line $LINENO"' ERR

# Run main function
main "$@"