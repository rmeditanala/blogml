# BlogML Docker Swarm Deployment

This repository contains the complete Docker Swarm deployment configuration for BlogML, a modern microservices blogging platform with AI-powered features.

## 🏗️ Architecture Overview

BlogML is built as a scalable microservices architecture with the following components:

### Services

- **Frontend**: Vue.js 3 + Vite + Tailwind CSS
- **Backend**: Laravel 12 + PHP 8.2 + MySQL
- **ML Service**: Python FastAPI + PyTorch + Transformers
- **Database**: MySQL 8.0
- **Cache**: Redis 7
- **Reverse Proxy**: Nginx with SSL termination

### Infrastructure

- **Containerization**: Docker containers with multi-stage builds
- **Orchestration**: Docker Swarm for production deployment
- **Networking**: Overlay networks with service discovery
- **Security**: SSL/TLS encryption, secrets management, rate limiting
- **Monitoring**: Health checks and logging

## 📁 Project Structure

```
deployment/
├── README.md                           # This documentation
├── .env.example                       # Environment configuration template
├── .env.development                   # Development environment variables
├── docker-compose.yml                 # Local development setup
├── docker-stack.yml                   # Production Docker Stack
├── scripts/
│   └── generate-ssl.sh               # SSL certificate generator
├── frontend/
│   ├── Dockerfile                     # Frontend container definition
│   └── nginx.conf                     # Frontend nginx configuration
├── backend/
│   ├── Dockerfile                     # Backend container definition
│   ├── php.ini                        # PHP-FPM configuration
│   └── supervisord.conf              # Process supervisor config
├── ml-service/
│   └── Dockerfile                     # ML service container definition
├── nginx/
│   └── nginx.conf                     # Reverse proxy configuration
├── ssl/                              # SSL certificates (generated)
└── mysql/
    └── my.cnf                        # MySQL configuration
```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop 4.0+ (with Docker Swarm enabled)
- Docker Compose v2.0+
- Git
- OpenSSL (for SSL generation)
- Hugging Face token (for ML models)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd blogml/deployment
```

### 2. Environment Setup

Copy and configure the environment file:

```bash
cp .env.example .env
# Edit .env with your specific configuration
```

**Important variables to configure:**
- `HF_TOKEN`: Your Hugging Face token for model downloads
- `DB_PASSWORD`: Secure database password
- `APP_KEY`: Generate with `php artisan key:generate --show`

### 3. Generate SSL Certificates (Development)

```bash
./scripts/generate-ssl.sh
```

For production, use proper SSL certificates from a certificate authority.

### 4. Local Development

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

Access the application at:
- Frontend: http://localhost:80
- Backend API: http://localhost:9000
- ML Service: http://localhost:8000
- Nginx (with SSL): https://localhost:443

## 🏭 Production Deployment with Docker Swarm

### 1. Initialize Docker Swarm

```bash
# On the manager node
docker swarm init --advertise-addr <MANAGER-IP>

# On worker nodes (optional)
docker swarm join --token <TOKEN> <MANAGER-IP>:2377
```

### 2. Create Docker Secrets

Create secrets for production:

```bash
# Generate secure passwords and tokens
echo "your_secure_mysql_root_password" | docker secret create mysql_root_password -
echo "your_secure_mysql_password" | docker secret create mysql_password -
echo "your_secure_app_key" | docker secret create app_key -
echo "your_huggingface_token" | docker secret create hf_token -

# Generate or copy SSL certificates
cat path/to/your/cert.pem | docker secret create ssl_cert -
cat path/to/your/key.pem | docker secret create ssl_key -
```

### 3. Create Data Directories

```bash
# Create persistent data directories
sudo mkdir -p /opt/blogml/data/{mysql,redis,backend/storage,ml-models}
sudo mkdir -p /opt/blogml/logs/{backend,ml-service,nginx}
sudo chown -R $USER:$USER /opt/blogml/data
sudo chown -R $USER:$USER /opt/blogml/logs
```

### 4. Build and Deploy

```bash
# Build images (if needed)
docker build -t blogml/frontend:latest ../frontend -f frontend/Dockerfile
docker build -t blogml/backend:latest ../backend -f backend/Dockerfile
docker build -t blogml/ml-service:latest ../ml-service -f ml-service/Dockerfile

# Deploy the stack
docker stack deploy -c docker-stack.yml blogml
```

### 5. Monitor Deployment

```bash
# Check service status
docker service ls

# View service logs
docker service logs blogml_frontend
docker service logs blogml_backend
docker service logs blogml_ml-service

# Scale services
docker service scale blogml_backend=5
docker service scale blogml_frontend=3
```

## 📋 Service Configuration

### Frontend Service

- **Replicas**: 2 (production)
- **Memory**: 256MB limit
- **Port**: 80 (internal)
- **Features**: Vue.js SPA with Nginx serving

### Backend Service

- **Replicas**: 3 (production)
- **Memory**: 1GB limit
- **Port**: 9000
- **Features**: Laravel with PHP-FPM, queue workers, scheduler

### ML Service

- **Replicas**: 2 (production)
- **Memory**: 4GB limit
- **Port**: 8000
- **Features**: FastAPI with PyTorch models

### Database Service

- **Replicas**: 1
- **Memory**: 2GB limit
- **Port**: 3306
- **Features**: MySQL 8.0 with performance tuning

### Cache Service

- **Replicas**: 1
- **Memory**: 512MB limit
- **Port**: 6379
- **Features**: Redis with persistence

## 🔧 Configuration Details

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_NAME` | Application name | BlogML | No |
| `APP_ENV` | Environment | local | No |
| `APP_KEY` | Laravel app key | Generated | Yes |
| `APP_DEBUG` | Debug mode | false | No |
| `DB_PASSWORD` | Database password | - | Yes |
| `HF_TOKEN` | Hugging Face token | - | Yes |
| `VITE_API_URL` | Frontend API URL | http://localhost:9000 | No |

### SSL Configuration

The deployment includes SSL/TLS encryption:

- **Development**: Self-signed certificates (via `generate-ssl.sh`)
- **Production**: Use certificates from Let's Encrypt or your CA

### Security Features

- **Rate Limiting**: API endpoints limited to 10 requests/second
- **Security Headers**: XSS protection, content type options, frame options
- **CORS**: Configured for ML service endpoints
- **Secrets Management**: Docker secrets for sensitive data

### Monitoring & Health Checks

All services include health checks:

```bash
# Check service health
docker service ps blogml_backend --no-trunc
```

Health check endpoints:
- Frontend: `GET /`
- Backend: `GET /health`
- ML Service: `GET /health`
- Nginx: `GET /health`

## 🔄 Development Workflow

### 1. Local Development

```bash
# Start development environment
docker compose up -d

# Make changes to code
# Changes are hot-reloaded in containers

# View logs
docker compose logs -f <service-name>
```

### 2. Testing

```bash
# Run tests in containers
docker compose exec backend php artisan test
docker compose exec ml-service pytest
```

### 3. Building for Production

```bash
# Build production images
docker build -t blogml/backend:latest ../backend -f backend/Dockerfile
docker build -t blogml/frontend:latest ../frontend -f frontend/Dockerfile
docker build -t blogml/ml-service:latest ../ml-service -f ml-service/Dockerfile

# Push to registry (if using one)
docker push blogml/backend:latest
docker push blogml/frontend:latest
docker push blogml/ml-service:latest
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check Docker Swarm status
docker info

# Check service logs
docker service logs blogml_backend

# Check resource constraints
docker service inspect blogml_backend
```

#### 2. Database Connection Issues

```bash
# Check database service
docker service ps blogml_mysql

# Test connection
docker compose exec backend php artisan tinker
>>> DB::connection()->getPdo()
```

#### 3. SSL Certificate Issues

```bash
# Regenerate certificates
./scripts/generate-ssl.sh

# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout
```

#### 4. Memory Issues

```bash
# Check memory usage
docker stats

# Scale down services if needed
docker service scale blogml_ml-service=1
```

### Performance Tuning

#### Backend (Laravel)

- Adjust `php.ini` memory limits based on load
- Configure OPCache settings for better performance
- Tune database connection pool

#### ML Service

- Adjust `MAX_WORKERS` based on available CPU cores
- Monitor GPU usage if using GPU-enabled containers
- Implement model caching strategies

#### Database

- Tune MySQL configuration in `my.cnf`
- Monitor slow query logs
- Implement proper indexing

## 📊 Scaling Guide

### Horizontal Scaling

```bash
# Scale backend services
docker service scale blogml_backend=5

# Scale frontend services
docker service scale blogml_frontend=3

# Scale ML services
docker service scale blogml_ml-service=3
```

### Vertical Scaling

Update resource limits in `docker-stack.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 2G  # Increased from 1G
    reservations:
      memory: 1G  # Increased from 512M
```

## 🔒 Security Best Practices

### 1. Network Security

- Use overlay networks for service communication
- Expose only necessary ports
- Implement proper firewall rules

### 2. Secrets Management

- Never commit secrets to version control
- Use Docker secrets for sensitive data
- Rotate secrets regularly

### 3. Container Security

- Use non-root users in containers
- Keep base images updated
- Scan images for vulnerabilities

### 4. Application Security

- Implement proper authentication/authorization
- Validate all user inputs
- Use HTTPS in production
- Monitor security logs

## 📈 Monitoring & Logging

### Logs Collection

```bash
# View real-time logs
docker service logs -f blogml_backend

# Collect logs from all services
docker service ls | awk 'NR>1 {print $2}' | xargs -I {} docker service logs --tail 100 {}
```

### Metrics Collection

Consider integrating with:
- **Prometheus**: For metrics collection
- **Grafana**: For visualization
- **ELK Stack**: For log aggregation
- **Sentry**: For error tracking

## 🔄 Backup & Recovery

### Database Backup

```bash
# Create backup
docker compose exec mysql mysqldump -u root -p blogml > backup.sql

# Restore backup
docker compose exec -T mysql mysql -u root -p blogml < backup.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v blogml_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql-backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v blogml_mysql_data:/data -v $(pwd):/backup alpine tar xzf /backup/mysql-backup.tar.gz -C /data
```

## 🆘 Support

For issues and questions:

1. Check this documentation first
2. Review service logs for error messages
3. Verify configuration against templates
4. Test with a minimal setup if needed

## 📝 License

This deployment configuration is part of the BlogML project. See the main project license for details.

---

**Happy Deploying! 🚀**