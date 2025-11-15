from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from app.routes import sentiment, recommendations, image_classification, text_generation
from app.services.model_loader import ModelLoader

app = FastAPI(
    title="BlogML ML Service",
    description="Machine Learning service for BlogML platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sentiment.router, prefix="/predict/sentiment", tags=["sentiment"])
app.include_router(recommendations.router, prefix="/predict/recommendations", tags=["recommendations"])
app.include_router(image_classification.router, prefix="/predict/image-classification", tags=["image"])
app.include_router(text_generation.router, prefix="/generate", tags=["text-generation"])

@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup"""
    ModelLoader.initialize_models()

@app.get("/")
async def root():
    return {
        "message": "BlogML ML Service",
        "version": "1.0.0",
        "endpoints": {
            "sentiment": "/predict/sentiment",
            "recommendations": "/predict/recommendations",
            "image_classification": "/predict/image-classification",
            "text_generation": "/generate"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development"
    )