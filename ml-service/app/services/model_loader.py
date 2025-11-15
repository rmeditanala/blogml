import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForSeq2SeqLM,
    pipeline
)
from PIL import Image
import redis
import logging

logger = logging.getLogger(__name__)

class ModelLoader:
    """Singleton class to load and manage ML models"""

    _instance = None
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize_models(cls):
        """Initialize all required models"""
        if cls._instance is None:
            cls._instance = cls()

        instance = cls._instance

        try:
            # Initialize sentiment analysis model
            logger.info("Loading sentiment analysis model...")
            instance._models['sentiment'] = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=0 if torch.cuda.is_available() else -1
            )

            # Initialize text generation model
            logger.info("Loading text generation model...")
            model_name = "google/flan-t5-base"  # More manageable size than gpt-2
            instance._models['text_tokenizer'] = AutoTokenizer.from_pretrained(model_name)
            instance._models['text_generator'] = AutoModelForSeq2SeqLM.from_pretrained(model_name)

            # Initialize image classification model
            logger.info("Loading image classification model...")
            instance._models['image_classifier'] = pipeline(
                "image-classification",
                model="microsoft/resnet-50",
                device=0 if torch.cuda.is_available() else -1
            )

            # Initialize Redis client for caching
            logger.info("Connecting to Redis...")
            instance._models['redis'] = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0,
                decode_responses=True
            )

            logger.info("All models loaded successfully!")

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    @classmethod
    def get_model(cls, model_name: str):
        """Get a loaded model by name"""
        if cls._instance is None:
            cls.initialize_models()

        return cls._instance._models.get(model_name)

    @classmethod
    def get_redis_client(cls):
        """Get Redis client"""
        return cls.get_model('redis')