from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Include routers (updated routes for API-first approach)
app.include_router(sentiment.router, prefix="/sentiment", tags=["sentiment"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(image_classification.router, prefix="/image-classification", tags=["image"])
app.include_router(text_generation.router, prefix="/text-generation", tags=["text-generation"])

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
            "sentiment": "/sentiment",
            "sentiment_batch": "/sentiment/batch",
            "recommendations": "/recommendations/user",
            "image_classification": "/image-classification",
            "text_generation": "/text-generation",
            "health": "/health"
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