from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import io
import hashlib
import json
import tempfile
import os
from PIL import Image
import base64

from app.services.model_loader import ModelLoader

router = APIRouter()

class ImageClassificationResponse(BaseModel):
    tags: List[Dict[str, Any]]  # [{"tag": "dog", "confidence": 0.95}, ...]
    is_safe: bool
    nsfw_score: float
    cached: bool = False

class BatchImageClassificationResponse(BaseModel):
    results: List[ImageClassificationResponse]

# NSFW-related labels that might be in the model
NSFW_LABELS = {
    'nsfw', 'nudity', 'explicit', 'sexual', 'porn',
    'violence', 'gore', 'blood', 'weapon', 'gun'
}

def detect_nsfw_content(predictions: List[Dict], threshold: float = 0.5) -> tuple[bool, float]:
    """
    Detect if content is NSFW based on predictions
    """
    nsfw_score = 0.0
    for pred in predictions:
        label = pred.get('label', '').lower()
        score = pred.get('score', 0.0)

        if any(nsfw_word in label for nsfw_word in NSFW_LABELS):
            nsfw_score = max(nsfw_score, score)

    is_safe = nsfw_score < threshold
    return is_safe, nsfw_score

@router.post("/", response_model=ImageClassificationResponse)
async def classify_image(
    file: UploadFile = File(...),
    cache_key: Optional[str] = Form(None),
    max_tags: int = Form(10)
):
    """
    Classify uploaded image and return tags with confidence scores
    """
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize image if too large (to prevent memory issues)
        if image.size[0] > 1024 or image.size[1] > 1024:
            image.thumbnail((1024, 1024))

        # Try cache first
        redis_client = ModelLoader.get_redis_client()
        if cache_key and redis_client:
            cached_result = redis_client.get(f"image_class:{cache_key}")
            if cached_result:
                result = json.loads(cached_result)
                result["cached"] = True
                return ImageClassificationResponse(**result)

        # Get classification using Hugging Face API or local model
        # Save image to temporary file for API calls
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            image.save(temp_file, format='JPEG')
            temp_file_path = temp_file.name

        try:
            predictions = ModelLoader.classify_image(temp_file_path)
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

        # Filter to top N tags and format response
        top_predictions = predictions[:max_tags]
        tags = []
        for pred in top_predictions:
            tags.append({
                "tag": pred['label'].lower().replace('_', ' '),
                "confidence": float(pred['score']),
                "is_auto_generated": True
            })

        # NSFW detection
        is_safe, nsfw_score = detect_nsfw_content(predictions)

        response_data = {
            "tags": tags,
            "is_safe": is_safe,
            "nsfw_score": nsfw_score,
            "cached": False
        }

        # Cache the result
        if cache_key and redis_client:
            redis_client.setex(
                f"image_class:{cache_key}",
                3600,  # 1 hour cache
                json.dumps(response_data)
            )

        return ImageClassificationResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image classification failed: {str(e)}")

@router.post("/base64", response_model=ImageClassificationResponse)
async def classify_image_base64(
    image_data: str,
    cache_key: Optional[str] = None,
    max_tags: int = 10
):
    """
    Classify image from base64 string
    """
    try:
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if needed
        if image.size[0] > 1024 or image.size[1] > 1024:
            image.thumbnail((1024, 1024))

        # Try cache
        redis_client = ModelLoader.get_redis_client()
        if cache_key and redis_client:
            cached_result = redis_client.get(f"image_class:{cache_key}")
            if cached_result:
                result = json.loads(cached_result)
                result["cached"] = True
                return ImageClassificationResponse(**result)

        # Classification using Hugging Face API or local model
        # Save image to temporary file for API calls
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            image.save(temp_file, format='JPEG')
            temp_file_path = temp_file.name

        try:
            predictions = ModelLoader.classify_image(temp_file_path)
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)

        # Format response
        top_predictions = predictions[:max_tags]
        tags = []
        for pred in top_predictions:
            tags.append({
                "tag": pred['label'].lower().replace('_', ' '),
                "confidence": float(pred['score']),
                "is_auto_generated": True
            })

        # NSFW detection
        is_safe, nsfw_score = detect_nsfw_content(predictions)

        response_data = {
            "tags": tags,
            "is_safe": is_safe,
            "nsfw_score": nsfw_score,
            "cached": False
        }

        # Cache result
        if cache_key and redis_client:
            redis_client.setex(
                f"image_class:{cache_key}",
                3600,
                json.dumps(response_data)
            )

        return ImageClassificationResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Base64 image classification failed: {str(e)}")

@router.get("/labels")
async def get_available_labels():
    """
    Get available labels from the image classification model
    """
    try:
        classifier = ModelLoader.get_model('image_classifier')
        if hasattr(classifier.model.config, 'id2label'):
            labels = classifier.model.config.id2label
            return {"labels": list(labels.values())}
        else:
            return {"labels": ["ImageNet labels - model loaded but labels not accessible"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get labels: {str(e)}")