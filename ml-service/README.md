# BlogML ML Service

FastAPI-based machine learning service for the BlogML platform. Provides sentiment analysis, image classification, text generation, and recommendation algorithms using **Hugging Face API** for optimal performance.

## Features

- **Sentiment Analysis**: Analyze text sentiment using Twitter RoBERTa via Hugging Face API
- **Image Classification**: Auto-classify and tag images using ResNet50 via Hugging Face API
- **Text Generation**: Generate blog posts and content using FLAN-T5 via Hugging Face API
- **Recommendations**: Content-based and collaborative filtering
- **API-First Approach**: No large model downloads required
- **Caching**: Redis-based caching for better performance
- **Batch Processing**: Handle multiple requests efficiently

## Quick Start (Recommended: Hugging Face API)

### Prerequisites

- Python 3.11+
- Redis (optional, for caching)
- Hugging Face API token (get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))

### Installation

1. **Clone and setup:**
   ```bash
   cd ml-service
   pip install -r requirements.txt
   ```

2. **Set up Hugging Face API:**
   ```bash
   # Option A: Environment variable
   export HUGGINGFACE_API_TOKEN=your_token_here

   # Option B: .env file
   cp .env.example .env
   # Edit .env and add your HUGGINGFACE_API_TOKEN
   ```

3. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

The service will automatically detect your API token and use Hugging Face's cloud infrastructure. The service will be available at `http://localhost:8000`

## Alternative: Local Models

If you prefer to run models locally (requires 2GB+ disk space):

```bash
# Remove API token to force local mode
unset HUGGINGFACE_API_TOKEN

# Download models (this may take a while)
python scripts/download_models.py

# Run server (will use local models)
uvicorn app.main:app --reload
```

**Note:** Local model downloads can be slow and may get stuck. Using the Hugging Face API is highly recommended for better performance and reliability.

### Docker Setup

```bash
# Build image
docker build -t blogml-ml-service .

# Run with Hugging Face API (Recommended)
docker run -p 8000:8000 \
  -e HUGGINGFACE_API_TOKEN=your_token_here \
  -e REDIS_HOST=host.docker.internal \
  blogml-ml-service

# Run with local models (slower, larger image)
docker run -p 8000:8000 \
  -e REDIS_HOST=host.docker.internal \
  blogml-ml-service
```

## API Endpoints

### Sentiment Analysis

```bash
# Single text analysis
curl -X POST "http://localhost:8000/sentiment/" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this blog post!"}'

# Batch analysis
curl -X POST "http://localhost:8000/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Great post", "Not helpful"]}'
```

### Image Classification

```bash
# Upload image file
curl -X POST "http://localhost:8000/image-classification/" \
  -F "file=@image.jpg" \
  -F "max_tags=10"

# Base64 image
curl -X POST "http://localhost:8000/image-classification/base64" \
  -H "Content-Type: application/json" \
  -d '{"image_data": "base64_encoded_image"}'
```

### Text Generation

```bash
# Generate text
curl -X POST "http://localhost:8000/text-generation/" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write about machine learning"}'

# Generate outline
curl -X POST "http://localhost:8000/text-generation/outline" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Getting started with AI", "num_sections": 5}'

# Generate blog post
curl -X POST "http://localhost:8000/text-generation/post" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Introduction to FastAPI", "tone": "informative"}'
```

### Recommendations

```bash
# User recommendations
curl -X POST "http://localhost:8000/recommendations/user" \
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

## Models Used (via Hugging Face API)

- **Sentiment**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Image Classification**: `microsoft/resnet-50`
- **Text Generation**: `google/flan-t5-base`

**Note**: Models are accessed via Hugging Face Inference API - no local downloads required when using API mode.

## Performance

### With Hugging Face API (Recommended)
- **API Response Time**: < 500ms (network dependent)
- **Startup Time**: ~5 seconds (no model loading)
- **Memory Usage**: ~200MB (service only)
- **Concurrent Requests**: Configurable (default: 10)

### With Local Models
- **API Response Time**: < 300ms (cached), < 2s (cold start)
- **Model Loading**: ~30 seconds on startup
- **Memory Usage**: ~2GB with all models loaded
- **Disk Space**: ~1.5GB for all models

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

### Hugging Face API Issues

```bash
# Test API token
curl -H "Authorization: Bearer your_token_here" \
     https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest \
     -d '{"inputs": "test"}'

# Check if token is set
echo $HUGGINGFACE_API_TOKEN

# Test mode detection
python test_api_mode.py
```

### Model Download Issues (Local Mode Only)

If you're having trouble with model downloads, we strongly recommend using the Hugging Face API instead:

```bash
# Set up API token
export HUGGINGFACE_API_TOKEN=your_token_here
# Restart service - it will automatically use API mode
```

If you must use local models:

```bash
# Download specific model
python scripts/download_models.py sentiment

# Check available disk space
df -h
```

### Memory Issues

- **API Mode**: Minimal memory usage (~200MB)
- **Local Mode**:
  - Reduce `MAX_CONCURRENT_REQUESTS` in environment
  - Use CPU instead of GPU: `TORCH_DEVICE=cpu`
  - Load only required models

### Performance Optimization

- **Use Hugging Face API**: No startup time, lower memory usage
- **Enable Redis caching**: Reduces API calls and improves response times
- **Use batch endpoints**: More efficient for multiple requests
- **Monitor API usage**: Check Hugging Face rate limits

### Getting Help

- **API Setup**: See [HF_API_SETUP.md](./HF_API_SETUP.md) for detailed instructions
- **Rate Limits**: Check [Hugging Face pricing](https://huggingface.co/pricing)
- **Service Status**: Monitor health endpoint: `/health`

## License

MIT License - see LICENSE file for details.