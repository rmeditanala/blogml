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

        # Get prediction using either API or local model
        result = ModelLoader.analyze_sentiment(request.text)[0]

        # Map label to match our schema
        # Twitter RoBERTa model returns: 'LABEL_0': Negative, 'LABEL_1': Neutral, 'LABEL_2': Positive
        label_map = {
            'LABEL_0': 'NEGATIVE',
            'LABEL_1': 'NEUTRAL',
            'LABEL_2': 'POSITIVE',
            'POSITIVE': 'POSITIVE',
            'NEGATIVE': 'NEGATIVE',
            'NEUTRAL': 'NEUTRAL'
        }

        # Handle both the new Twitter model and fallback for old models
        if isinstance(result, dict) and 'label' in result:
            sentiment = label_map.get(result['label'].upper(), 'NEUTRAL')
            # Get score from either 'score' or if results is a list of dictionaries
            if 'score' in result:
                confidence = float(result['score'])
            else:
                # For models that return list of predictions
                confidence = 0.0
        else:
            # Fallback for unexpected format
            sentiment = 'NEUTRAL'
            confidence = 0.0

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