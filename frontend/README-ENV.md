# BlogML Frontend Environment Configuration

This document explains the environment variables and configuration options for the BlogML frontend application.

## Environment Variables

The frontend uses Vite's environment variable system. All variables must be prefixed with `VITE_` to be exposed to the frontend code.

### Core Configuration

```bash
# API Configuration
VITE_API_BASE_URL=/api                    # Base URL for Laravel backend API
VITE_ML_BASE_URL=/ml                      # Base URL for ML Service API

# Application Info
VITE_APP_NAME=BlogML                      # Application name
VITE_APP_VERSION=1.0.0                    # Application version
VITE_APP_DESCRIPTION=AI-powered blogging platform  # App description

# Environment
VITE_NODE_ENV=development                 # Node environment (development/production)
VITE_DEBUG=true                          # Enable debug mode
```

## Environment Files

- `.env` - Development environment variables (local development)
- `.env.production` - Production environment variables
- `.env.local` - Local overrides (not tracked in git)

## Development vs Production URLs

### Development (with nginx proxy)
```bash
VITE_API_BASE_URL=/api
VITE_ML_BASE_URL=/ml
```
- Routes through nginx proxy at `http://localhost`
- Uses relative paths for seamless development

### Development (direct access)
```bash
VITE_API_BASE_URL=http://localhost:9000/api
VITE_ML_BASE_URL=http://localhost:8000
```
- Direct access to development servers
- Bypasses nginx proxy

### Production
```bash
VITE_API_BASE_URL=/api
VITE_ML_BASE_URL=/ml
```
- Uses relative paths in production
- Works with nginx reverse proxy

## Vite Configuration

The `vite.config.js` file includes:

### Development Proxy
```javascript
proxy: {
  '/api': {
    target: 'http://localhost:80',
    changeOrigin: true,
    secure: false
  },
  '/ml': {
    target: 'http://localhost:80',
    changeOrigin: true,
    secure: false
  }
}
```

This proxy configuration ensures that:
- API requests (`/api/*`) are proxied to the nginx reverse proxy
- ML service requests (`/ml/*`) are proxied to the nginx reverse proxy
- CORS issues are avoided during development

## Usage in Components

```javascript
// Import environment variables
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
const mlBaseUrl = import.meta.env.VITE_ML_BASE_URL
const appName = import.meta.env.VITE_APP_NAME

// Import configured APIs
import { api, mlService, API_CONFIG } from '@/services'
```

## Available Services

### Backend API (`/api/v1/*`)
```javascript
import { api } from '@/services'

// Example usage
api.get('/posts')           // GET /api/v1/posts
api.post('/auth/login')     // POST /api/v1/auth/login
```

### ML Service (`/ml/*`)
```javascript
import { mlService } from '@/services'

// Example usage
mlService.analyzeSentiment("Great blog post!")
mlService.getUserRecommendations(123)
mlService.classifyImage("https://example.com/image.jpg")
```

## Docker Deployment

When building for Docker containers, ensure the environment variables are properly set:

### Development Docker
```dockerfile
ENV VITE_API_BASE_URL=/api
ENV VITE_ML_BASE_URL=/ml
ENV VITE_NODE_ENV=development
```

### Production Docker
```dockerfile
ENV VITE_API_BASE_URL=/api
ENV VITE_ML_BASE_URL=/ml
ENV VITE_NODE_ENV=production
ENV VITE_DEBUG=false
```

## Troubleshooting

### API Requests Not Working
1. Check that environment variables are set correctly
2. Verify nginx proxy is running on port 80
3. Ensure backend/ML services are accessible
4. Check browser console for CORS errors

### Environment Variables Not Loading
1. Ensure variables are prefixed with `VITE_`
2. Check that `.env` file exists in frontend root
3. Restart development server after changing environment variables
4. Verify `vite.config.js` has `envPrefix: 'VITE_'`

### Proxy Issues
1. Verify nginx configuration matches API routes
2. Check that services are running on expected ports
3. Ensure `changeOrigin: true` in proxy config
4. Check for SSL/TLS conflicts