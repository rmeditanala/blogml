from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import hashlib
import json

from app.services.model_loader import ModelLoader

router = APIRouter()

class SentimentRequest(BaseModel):
    text: str
    cache_key: Optional[str] = None

class SentimentResponse(BaseModel):
    sentiment: str  # POSITIVE, NEGATIVE, NEUTRAL
    confidence: float
    cached: bool = False

class BatchSentimentRequest(BaseModel):
    texts: List[str]

class BatchSentimentResponse(BaseModel):
    results: List[SentimentResponse]

@router.post("/", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment of a given text
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Try cache first
        redis_client = ModelLoader.get_redis_client()
        cache_key = request.cache_key or hashlib.md5(request.text.encode()).hexdigest()
        cached_result = None

        if redis_client:
            cached_result = redis_client.get(f"sentiment:{cache_key}")

        if cached_result:
            result = json.loads(cached_result)
            result["cached"] = True
            return SentimentResponse(**result)

        # Get prediction
        sentiment_model = ModelLoader.get_model('sentiment')
        result = sentiment_model(request.text)[0]

        # Map label to match our schema
        label_map = {
            'POSITIVE': 'POSITIVE',
            'NEGATIVE': 'NEGATIVE',
            'NEUTRAL': 'NEUTRAL'
        }

        sentiment = label_map.get(result['label'].upper(), 'NEUTRAL')
        confidence = float(result['score'])

        response_data = {
            "sentiment": sentiment,
            "confidence": confidence,
            "cached": False
        }

        # Cache the result
        if redis_client:
            redis_client.setex(
                f"sentiment:{cache_key}",
                3600,  # 1 hour cache
                json.dumps(response_data)
            )

        return SentimentResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/batch", response_model=BatchSentimentResponse)
async def analyze_batch_sentiment(request: BatchSentimentRequest):
    """
    Analyze sentiment for multiple texts
    """
    if not request.texts:
        raise HTTPException(status_code=400, detail="Texts list cannot be empty")

    if len(request.texts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 texts allowed per batch")

    results = []

    try:
        for text in request.texts:
            if not text.strip():
                results.append(SentimentResponse(
                    sentiment="NEUTRAL",
                    confidence=0.0,
                    cached=False
                ))
                continue

            # Create individual request
            individual_request = SentimentRequest(text=text)
            result = await analyze_sentiment(individual_request)
            results.append(result)

        return BatchSentimentResponse(results=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch sentiment analysis failed: {str(e)}")