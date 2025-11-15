# BlogML - AI-Powered Blog Platform
## Product Requirements Document (Simplified for Solo Developer)

---

## 1. Project Overview

### Purpose
A portfolio project demonstrating machine learning integration in a full-stack web application with modern deployment practices.

### Tech Stack
- **Frontend:** Vue 3 + Vite + TailwindCSS
- **Backend:** Laravel 12 + PostgreSQL + Redis
- **ML Service:** FastAPI + Pre-trained Models
- **Deployment:** Docker Swarm & Kubernetes

### Timeline
8-10 weeks (solo developer, part-time)

---

## 2. Core Features

### 2.1 Sentiment Analysis
- Automatically analyze comment sentiment (positive/negative/neutral)
- Display sentiment badge on each comment
- Filter comments by sentiment
- Show post sentiment statistics

**ML Model:** DistilBERT (Hugging Face)

### 2.2 Post Recommendations
- "Recommended For You" on homepage
- "Related Posts" on post detail page
- Track user interactions (views, likes, comments)
- Personalized feed based on reading history

**ML Approach:** Content-based filtering + Collaborative filtering hybrid

### 2.3 Image Classification
- Auto-tag uploaded images
- Detect image content (objects, scenes)
- NSFW content detection
- Organize media library by tags

**ML Model:** ResNet50 or EfficientNet (pre-trained)

### 2.4 AI Post Generation
- Generate post drafts from prompts
- Create outlines and sections
- Expand paragraphs
- Improve/rewrite text

**ML Model:** FLAN-T5 or GPT-2 (local) / OpenAI API (optional)

---

## 3. Technical Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Vue 3     │────────▶│  Laravel 12 │────────▶│   FastAPI   │
│  (Port 80)  │  REST   │  (Port 9000)│  HTTP   │  (Port 8000)│
└─────────────┘         └─────────────┘         └─────────────┘
                               │
                        ┌──────┴──────┐
                        │  PostgreSQL │
                        │    Redis    │
                        └─────────────┘
```

### Data Flow Example
1. User posts comment → Vue sends to Laravel
2. Laravel queues sentiment analysis job
3. Job calls FastAPI `/predict/sentiment`
4. FastAPI returns sentiment score
5. Laravel saves to DB, updates UI

---

## 4. Database Schema (Core Tables)

```sql
users
- id, name, email, password

posts
- id, user_id, title, slug, content, status
- is_ai_generated, view_count

comments
- id, post_id, user_id, content
- sentiment_score, sentiment_label, confidence

user_interactions
- id, user_id, post_id, interaction_type
- (view, like, share, comment, bookmark)

media
- id, user_id, post_id, filename, path

media_tags
- id, media_id, tag, confidence, is_auto_generated

ai_generations
- id, user_id, prompt, generation_type, output_data
```

---

## 5. API Endpoints (Key Routes)

### Laravel Backend

**Posts:**
- `GET /api/posts` - List posts
- `GET /api/posts/{id}` - Post detail
- `POST /api/posts` - Create post
- `GET /api/recommendations/personalized` - Get recommendations

**Comments:**
- `POST /api/comments` - Create comment (auto sentiment analysis)
- `GET /api/posts/{id}/comments` - Get comments with sentiment

**Media:**
- `POST /api/media/upload` - Upload image (auto classification)

**AI:**
- `POST /api/ai/generate-post` - Generate post draft
- `POST /api/ai/generate-outline` - Generate outline

### FastAPI ML Service

**Sentiment:**
- `POST /predict/sentiment` - Analyze text sentiment

**Recommendations:**
- `POST /predict/recommendations/user` - Get user recommendations
- `POST /predict/recommendations/similar` - Get similar posts

**Image:**
- `POST /predict/image-classification` - Classify image

**Generation:**
- `POST /generate/post` - Generate blog post
- `POST /generate/outline` - Generate outline

---

## 6. Deployment Options

### Option 1: Docker Swarm (Simpler)
```yaml
Services:
- nginx (reverse proxy)
- frontend (Vue 3) - 2 replicas
- backend (Laravel) - 2 replicas
- ml-service (FastAPI) - 1 replica
- postgres - 1 replica
- redis - 1 replica
- worker (queue) - 1 replica
```

**Commands:**
```bash
docker swarm init
docker stack deploy -c docker-compose.swarm.yml blogml
```

### Option 2: Kubernetes (For Portfolio)
```yaml
Deployments:
- frontend-deployment (2 pods)
- backend-deployment (2 pods)
- ml-service-deployment (1 pod)
- postgres-statefulset (1 pod)
- redis-deployment (1 pod)

Services:
- frontend-service
- backend-service
- ml-service-service
- postgres-service
- redis-service

Ingress:
- blogml.example.com → frontend
- api.blogml.example.com → backend
```

**Commands:**
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl scale deployment backend --replicas=3
```

---

## 7. Project Structure

```
blogml/
├── frontend/              # Vue 3 app
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── views/         # Pages
│   │   ├── stores/        # Pinia stores
│   │   └── services/      # API calls
│   └── Dockerfile
│
├── backend/              # Laravel app
│   ├── app/
│   │   ├── Http/Controllers/
│   │   ├── Models/
│   │   ├── Services/     # ML client, business logic
│   │   └── Jobs/         # Queue jobs
│   ├── database/migrations/
│   └── Dockerfile
│
├── ml-service/           # FastAPI app
│   ├── app/
│   │   ├── models/       # ML model classes
│   │   ├── routes/       # API endpoints
│   │   └── services/     # Inference logic
│   ├── models/           # Pre-trained model files
│   └── Dockerfile
│
└── deployment/
    ├── docker-compose.yml
    ├── docker-compose.swarm.yml
    └── k8s/              # Kubernetes manifests
```

---

## 8. Development Phases

### Phase 1: Foundation (2 weeks)
- Setup projects (Vue, Laravel, FastAPI)
- Basic authentication
- CRUD for posts and comments
- Docker Compose for local dev

### Phase 2: ML Integration (3 weeks)
- Sentiment analysis feature
- Image classification feature
- Recommendation system (basic)
- FastAPI endpoints

### Phase 3: AI Generation (2 weeks)
- Text generation integration
- AI writing assistant UI
- Prompt templates

### Phase 4: Deployment (1-2 weeks)
- Docker Swarm setup
- Kubernetes configuration
- CI/CD pipeline (GitHub Actions)
- Documentation

### Phase 5: Polish (1 week)
- UI/UX improvements
- Performance optimization
- Testing and bug fixes
- Portfolio documentation

---

## 9. ML Models Setup

### Download Pre-trained Models
```bash
# In ml-service directory
python scripts/download_models.py
```

**Models:**
1. **Sentiment:** `distilbert-base-uncased-finetuned-sst-2-english` (~250MB)
2. **Image:** `resnet50` (~100MB)
3. **Text Gen:** `flan-t5-base` (~900MB) or use OpenAI API

**Storage:** Models stored in `ml-service/models/` directory

---

## 10. Key Technical Decisions

### Why Separate Codebases?
- Independent scaling
- Technology flexibility
- Clear separation of concerns
- Easier to showcase in portfolio

### Why FastAPI for ML?
- Python ecosystem for ML
- Fast async performance
- Auto API documentation
- Easy model serving

### Why Queue Jobs?
- Non-blocking ML requests
- Better user experience
- Retry failed jobs
- Resource management

### Why Two Deployment Options?
- Docker Swarm: Easier to learn and demo
- Kubernetes: Industry standard, better for portfolio

---

## 11. Environment Setup

### Local Development
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

### Docker Compose (All Services)
```bash
docker-compose up -d
# Frontend: http://localhost
# Backend API: http://localhost:9000
# ML Service: http://localhost:8001
```

---

## 12. Performance Targets

| Metric | Target |
|--------|--------|
| API response time | < 300ms |
| ML inference time | < 500ms |
| Page load time | < 2s |
| Recommendation accuracy | > 70% relevance |
| Sentiment accuracy | > 85% |

---

## 13. Portfolio Highlights

### What This Project Demonstrates

**Full-Stack Skills:**
- Modern frontend (Vue 3 Composition API)
- RESTful API design (Laravel)
- Microservices architecture

**Machine Learning:**
- ML model integration
- Pre-trained model usage
- ML API development

**DevOps:**
- Containerization (Docker)
- Orchestration (Swarm + K8s)
- CI/CD pipelines
- Cloud deployment

**Best Practices:**
- Clean code architecture
- API documentation
- Testing (unit + integration)
- Security considerations

---

## 14. Success Metrics

### Technical
- All 4 ML features working
- < 1s response time (cached)
- 99% uptime
- Automated deployment

### Portfolio
- GitHub stars/forks
- Live demo accessible
- Complete documentation
- Clean, readable code

---

## 15. MVP vs Full Features

### MVP (First Deploy)
- ✅ User authentication
- ✅ Create/read posts
- ✅ Comment with sentiment
- ✅ Basic recommendations
- ✅ Image upload with tags
- ✅ Simple AI generation

### Future Enhancements
- ⏳ Advanced recommendations
- ⏳ Real-time updates (WebSocket)
- ⏳ Social features (likes, shares)
- ⏳ Analytics dashboard
- ⏳ Multi-language support

---

## 16. Cost Estimation (Monthly)

### Development (Free)
- GitHub (free tier)
- Local development (your machine)

### Deployment (Minimal)
- VPS (DigitalOcean/Linode): $20-40/month
- Domain: $10-15/year
- **Total: ~$25/month**

### Alternative (Free Tier)
- Frontend: Vercel/Netlify (free)
- Backend: Railway/Fly.io (free tier)
- Database: Supabase (free tier)
- ML Service: Railway (free tier with limits)

---

## 17. Testing Strategy (Simplified)

### Frontend
- Component tests (Vitest)
- E2E user flows (Cypress) - optional

### Backend
- Feature tests (PHPUnit)
- API endpoint tests

### ML Service
- Unit tests (pytest)
- Model inference tests

**Coverage Target:** 60-70% (sufficient for portfolio)

---

## 18. Documentation Checklist

- [ ] README.md with setup instructions
- [ ] API documentation (Postman collection)
- [ ] Architecture diagram
- [ ] Deployment guide
- [ ] Demo video/screenshots
- [ ] Blog post explaining the project

---

## 19. Learning Outcomes

By completing this project, you'll master:
- ML model integration in web apps
- Microservices architecture
- Container orchestration
- Modern full-stack development
- DevOps practices
- Production deployment

---

## 20. Quick Start Command

```bash
# Clone and setup
git clone [repo-url]
cd blogml

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend php artisan migrate --seed

# Access app
open http://localhost
```

---

## Appendix: Tech Stack Justification

**Vue 3:** Modern, reactive, great ecosystem
**Laravel 12:** Robust, batteries-included, rapid development
**FastAPI:** Fast, async, perfect for ML serving
**PostgreSQL:** Reliable, feature-rich, great for complex queries
**Redis:** Fast caching, queue management
**Docker:** Consistent environments, easy deployment
**Kubernetes:** Industry standard, scalable, impressive for portfolio

---

**Document Version:** 1.0 (Solo Developer Edition)
**Last Updated:** November 15, 2025
**Estimated Completion:** 8-10 weeks part-time