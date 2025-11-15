# BlogML ML Service

FastAPI-based machine learning service for the BlogML platform. Provides sentiment analysis, image classification, text generation, and recommendation algorithms.

## Features

- **Sentiment Analysis**: Analyze text sentiment using DistilBERT
- **Image Classification**: Auto-classify and tag images using ResNet50
- **Text Generation**: Generate blog posts and content using FLAN-T5
- **Recommendations**: Content-based and collaborative filtering
- **Caching**: Redis-based caching for better performance
- **Batch Processing**: Handle multiple requests efficiently

## Quick Start

### Prerequisites

- Python 3.11+
- Redis (optional, for caching)
- 2GB+ disk space for models

### Installation

1. **Clone and setup:**
   ```bash
   cd ml-service
   pip install -r requirements.txt
   ```

2. **Download models:**
   ```bash
   python scripts/download_models.py
   ```

3. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

The service will be available at `http://localhost:8000`

### Docker Setup

```bash
# Build image
docker build -t blogml-ml-service .

# Run with environment variables
docker run -p 8000:8000 \
  -e REDIS_HOST=host.docker.internal \
  blogml-ml-service
```

## API Endpoints

### Sentiment Analysis

```bash
# Single text analysis
curl -X POST "http://localhost:8000/predict/sentiment/" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this blog post!"}'

# Batch analysis
curl -X POST "http://localhost:8000/predict/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Great post", "Not helpful"]}'
```

### Image Classification

```bash
# Upload image file
curl -X POST "http://localhost:8000/predict/image-classification/" \
  -F "file=@image.jpg" \
  -F "max_tags=10"

# Base64 image
curl -X POST "http://localhost:8000/predict/image-classification/base64" \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image"}'
```

### Text Generation

```bash
# Generate text
curl -X POST "http://localhost:8000/generate/text" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write about machine learning"}'

# Generate outline
curl -X POST "http://localhost:8000/generate/outline" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Getting started with AI", "num_sections": 5}'

# Generate blog post
curl -X POST "http://localhost:8000/generate/post" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Introduction to FastAPI", "tone": "informative"}'
```

### Recommendations

```bash
# User recommendations
curl -X POST "http://localhost:8000/predict/recommendations/user" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "user_id": 1,
      "read_posts": [1, 2, 3],
      "liked_posts": [1, 3]
    },
    "available_posts": [
      {"post_id": 4, "title": "AI Tutorial", "content": "...", "tags": ["ai", "tutorial"]},
      {"post_id": 5, "title": "Web Development", "content": "...", "tags": ["web", "dev"]}
    ]
  }'
```

## Architecture

```
ml-service/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/              # Pydantic models
│   ├── routes/              # API endpoints
│   │   ├── sentiment.py
│   │   ├── image_classification.py
│   │   ├── text_generation.py
│   │   └── recommendations.py
│   └── services/
│       └── model_loader.py  # Model management
├── models/                  # Downloaded ML models
├── scripts/
│   └── download_models.py  # Model download script
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Models Used

- **Sentiment**: `distilbert-base-uncased-finetuned-sst-2-english` (~250MB)
- **Image Classification**: `microsoft/resnet-50` (~100MB)
- **Text Generation**: `google/flan-t5-base` (~900MB)

## Performance

- **API Response Time**: < 300ms (cached), < 2s (cold start)
- **Model Loading**: ~30 seconds on startup
- **Memory Usage**: ~2GB with all models loaded
- **Concurrent Requests**: Configurable (default: 10)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black app/
flake8 app/
```

### Environment Variables

See `.env.example` for all available configuration options.

### Monitoring

The service includes:
- Health check endpoint: `/health`
- Request logging
- Model loading status
- Redis connection monitoring

## Production Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  ml-service:
    build: ./ml-service
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - ENVIRONMENT=production
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Kubernetes

See `../deployment/k8s/` for Kubernetes manifests.

## Troubleshooting

### Model Download Issues

```bash
# Download specific model
python scripts/download_models.py sentiment

# Check available disk space
df -h
```

### Memory Issues

- Reduce `MAX_CONCURRENT_REQUESTS` in environment
- Use CPU instead of GPU: `TORCH_DEVICE=cpu`
- Load only required models

### Performance Optimization

- Enable Redis caching
- Use batch endpoints for multiple requests
- Monitor model loading times

## License

MIT License - see LICENSE file for details.