# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BlogML is a full-stack AI-powered blog platform that demonstrates machine learning integration in web applications. The project is currently in the planning phase with only the product requirements document available.

### Architecture

This is a microservices-based application with three main components:
- **Frontend**: Vue 3 + Vite + TailwindCSS (Port 80/5173)
- **Backend**: Laravel 12 + PostgreSQL + Redis (Port 9000/8000)
- **ML Service**: FastAPI with pre-trained models (Port 8000)

### Core ML Features

1. **Sentiment Analysis**: DistilBERT for comment sentiment (positive/negative/neutral)
2. **Post Recommendations**: Hybrid content-based + collaborative filtering
3. **Image Classification**: ResNet50 for auto-tagging uploaded images
4. **AI Post Generation**: FLAN-T5 or GPT-2 for content generation

## Development Commands

### Local Development (once services are created)
```bash
# Frontend
cd frontend
npm install
npm run dev  # http://localhost:5173

# Backend
cd backend
composer install
php artisan serve  # http://localhost:8000

# ML Service
cd ml-service
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000
```

### Docker Development (recommended)
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend php artisan migrate --seed

# Access services
# Frontend: http://localhost
# Backend API: http://localhost:9000
# ML Service: http://localhost:8001
```

## Data Flow Pattern

The application follows a queue-based architecture for ML processing:
1. User actions (comments, uploads) → Vue sends to Laravel
2. Laravel queues ML processing jobs
3. Jobs call FastAPI prediction endpoints
4. Results stored in database, UI updated

### Key Integration Points

- **Sentiment Analysis**: Comments auto-analyzed via `/predict/sentiment`
- **Image Classification**: Uploads processed via `/predict/image-classification`
- **Recommendations**: Personalized content via `/predict/recommendations/user`
- **AI Generation**: Content creation via `/generate/post` endpoints

## Database Schema (Core Tables)

- `users`, `posts`, `comments` (standard blog tables)
- `comments` includes: `sentiment_score`, `sentiment_label`, `confidence`
- `user_interactions`: Tracks views, likes, shares for recommendations
- `media` + `media_tags`: Auto-classified image storage
- `ai_generations`: Logs AI content generation requests

## Project Structure (Planned)

```
blogml/
├── frontend/              # Vue 3 app
├── backend/              # Laravel app
├── ml-service/           # FastAPI app
└── deployment/           # Docker/K8s configs
```

## Development Phases

1. **Phase 1**: Foundation (CRUD, auth, basic setup)
2. **Phase 2**: ML Integration (sentiment, image, recommendations)
3. **Phase 3**: AI Generation (text generation, writing assistant)
4. **Phase 4**: Deployment (Docker Swarm + Kubernetes)
5. **Phase 5**: Polish (UI/UX, testing, documentation)

## Performance Targets

- API response: < 300ms
- ML inference: < 500ms
- Page load: < 2s
- Sentiment accuracy: > 85%
- Recommendation relevance: > 70%

## Key Technical Decisions

- **Separate codebases** for independent scaling and technology flexibility
- **FastAPI** for ML due to Python ecosystem and async performance
- **Queue jobs** for non-blocking ML processing
- **Both Docker Swarm and Kubernetes** (easier setup + industry standard)

## ML Models

- Stored in `ml-service/models/`
- Download via `python scripts/download_models.py`
- Models: DistilBERT (sentiment), ResNet50 (images), FLAN-T5 (generation)