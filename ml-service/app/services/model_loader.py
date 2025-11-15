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
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class ModelLoader:
    """Singleton class to load and manage ML models"""

    _instance = None
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def use_hf_api(self) -> bool:
        """Check if we should use Hugging Face API"""
        return bool(os.getenv('HUGGINGFACE_API_TOKEN') or os.getenv('HF_TOKEN'))

    @property
    def hf_token(self) -> Optional[str]:
        """Get Hugging Face API token"""
        return os.getenv('HUGGINGFACE_API_TOKEN') or os.getenv('HF_TOKEN')

    def call_hf_api(self, model_name: str, inputs: dict):
        """Call Hugging Face API with conditional URL routing"""
        if not self.use_hf_api:
            raise ValueError("Hugging Face API token not configured")

        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }

        # Use router URL for sentiment and image analysis models
        # Use inference API URL for text generation models
        if any(model in model_name.lower() for model in ['sentiment', 'roberta', 'resnet', 'image']):
            api_url = f"https://router.huggingface.co/hf-inference/models/{model_name}"
            timeout = 30
        else:
            # Text generation models use inference API
            # api_url = f"https://api-inference.huggingface.co/models/{model_name}"
            api_url = "https://router.huggingface.co/v1/chat/completions"
            timeout = 60

        try:
            response = requests.post(api_url, headers=headers, json=inputs, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Hugging Face API call failed: {e}")
            raise

    @classmethod
    def initialize_models(cls):
        """Initialize all required models"""
        if cls._instance is None:
            cls._instance = cls()

        instance = cls._instance

        try:
            # Check if using Hugging Face API
            if instance.use_hf_api:
                logger.info("🤖 Using Hugging Face API (no local downloads needed)")
                logger.info(f"Token configured: {'✅' if instance.hf_token else '❌'}")

                # Create API wrappers instead of loading local models
                instance._models['sentiment_api'] = {
                    'model': 'cardiffnlp/twitter-roberta-base-sentiment-latest'
                }
                instance._models['text_generation_api'] = {
                    # 'model': 'katanemo/Arch-Router-1.5B'
                    'model': 'openai/gpt-oss-120b:fastest'
                }
                instance._models['image_classification_api'] = {
                    'model': 'microsoft/resnet-50'
                }

                logger.info("✅ Hugging Face API configuration loaded!")
            else:
                logger.info("📁 Using local models (download required)")

                # Initialize sentiment analysis model locally
                logger.info("Loading sentiment analysis model...")
                instance._models['sentiment'] = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )

                # Initialize text generation model locally
                logger.info("Loading text generation model...")
                model_name = "google/flan-t5-small"  # Smaller for local use
                instance._models['text_tokenizer'] = AutoTokenizer.from_pretrained(model_name)
                instance._models['text_generator'] = AutoModelForSeq2SeqLM.from_pretrained(model_name)

                # Initialize image classification model locally
                logger.info("Loading image classification model...")
                instance._models['image_classifier'] = pipeline(
                    "image-classification",
                    model="microsoft/resnet-50",
                    device=0 if torch.cuda.is_available() else -1
                )

                logger.info("✅ Local models loaded successfully!")

            # Initialize Redis client for caching
            logger.info("Connecting to Redis...")
            try:
                instance._models['redis'] = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=0,
                    decode_responses=True
                )
                # Test Redis connection
                instance._models['redis'].ping()
                logger.info("✅ Redis connected successfully!")
            except redis.ConnectionError:
                logger.warning("⚠️  Redis connection failed, caching disabled")
                instance._models['redis'] = None

            logger.info("🎉 Model initialization complete!")

        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
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

    @classmethod
    def analyze_sentiment(cls, text: str):
        """Analyze sentiment using either local model or Hugging Face API"""
        if cls._instance is None:
            cls.initialize_models()

        instance = cls._instance

        if instance.use_hf_api:
            # Use Hugging Face API
            try:
                api_config = instance._models.get('sentiment_api')
                if not api_config:
                    raise ValueError("Sentiment API not configured")

                response = instance.call_hf_api(
                    api_config['model'],
                    {"inputs": text}
                )

                # Format API response to match expected structure
                if isinstance(response, list) and len(response) > 0:
                    # Handle nested list structure: [[{'label': 'positive', 'score': 0.97}, ...]]
                    if len(response) == 1 and isinstance(response[0], list):
                        predictions = response[0]
                    else:
                        predictions = response

                    # Take the highest scoring prediction
                    # API returns: [{'label': 'positive', 'score': 0.97}, {'label': 'neutral', 'score': 0.02}, ...]
                    best_prediction = max(predictions, key=lambda x: x.get('score', 0.0))
                    return [{
                        'label': best_prediction.get('label', 'NEUTRAL'),
                        'score': best_prediction.get('score', 0.0)
                    }]
                else:
                    return [{'label': 'NEUTRAL', 'score': 0.0}]
            except Exception as e:
                logger.error(f"Hugging Face API sentiment analysis failed: {e}")
                # Fallback to neutral
                return [{'label': 'NEUTRAL', 'score': 0.0}]
        else:
            # Use local model
            sentiment_model = cls.get_model('sentiment')
            if sentiment_model:
                return sentiment_model(text)
            else:
                raise ValueError("No sentiment model available")

    @classmethod
    def generate_text(cls, prompt: str, max_length: int = 100):
        """Generate text using either local model or Hugging Face API"""
        if cls._instance is None:
            cls.initialize_models()

        instance = cls._instance

        if instance.use_hf_api:
            # Use Hugging Face Router API (chat completions format)
            try:
                api_config = instance._models.get('text_generation_api')
                if not api_config:
                    raise ValueError("Text generation API not configured")

                # For text generation, use the router chat completions API
                api_url = "https://router.huggingface.co/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {instance.hf_token}",
                    "Content-Type": "application/json"
                }

                payload = {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "model": api_config['model'],
                    "stream": False,
                    "max_tokens": max_length,
                    "temperature": 0.7
                }

                response = requests.post(api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                result = response.json()
                # print('result', result)

                # Extract the generated content from chat completion response
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    # print('choice', choice)
                    if 'message' in choice:
                        message = choice['message']
                        # print('message', message)
                        # Try content field first, then reasoning as fallback
                        content = message.get('content', '')
                        # print('content', content)
                        if not content:
                            # Use reasoning field if content is missing
                            reasoning = message.get('reasoning', '')
                            if reasoning:
                                # Extract the actual generated text from reasoning (usually at the end)
                                # Look for patterns that indicate the actual answer
                                lines = reasoning.split('\n')

                                # Look for quoted text (actual alt text is often in quotes)
                                import re
                                for line in lines:
                                    # Find quoted content
                                    quotes = re.findall(r'"([^"]+)"', line)
                                    if quotes:
                                        content = quotes[0]
                                        break

                                # If no quotes found, look for lines that don't start with analysis words
                                if not content:
                                    for line in reversed(lines):
                                        line = line.strip()
                                        # Skip analysis/metadata lines
                                        skip_words = ['User', 'The user', 'Let', 'We', 'They', 'I', 'count:', 'F(', 'reasoning:', 'analysis']
                                        if (line and len(line) > 10 and len(line) < 150 and
                                            not any(skip_word in line for skip_word in skip_words) and
                                            not line.isdigit() and
                                            not '(' in line and ')' in line):
                                            content = line
                                            break

                                # If still no good content, look for the last sentence
                                if not content:
                                    sentences = reasoning.split('.')
                                    for sentence in reversed(sentences):
                                        sentence = sentence.strip()
                                        if (len(sentence) > 10 and len(sentence) < 150 and
                                            not sentence.startswith('User') and
                                            not sentence.startswith('The user')):
                                            content = sentence
                                            break

                                # Final fallback - last 100 chars
                                if not content:
                                    content = reasoning.strip()[-100:]
                            else:
                                content = "Generated content was empty or incomplete"

                        # Final fallback if still empty
                        if not content or content.strip() == "":
                            content = "Generated content was empty or incomplete"
                        return {
                            'generated_text': content.strip(),
                            'prompt_used': prompt,
                            'generation_params': {
                                'model': api_config['model'],
                                'max_tokens': max_length,
                                'temperature': 0.7
                            },
                            'cached': False
                        }
                    else:
                        logger.error(f"Invalid response structure: {choice}")
                        return {
                            'generated_text': "Text generation failed - invalid message structure",
                            'prompt_used': prompt,
                            'generation_params': {'error': True, 'response': choice},
                            'cached': False
                        }
                else:
                    logger.error(f"Invalid response format: {result}")
                    return {
                        'generated_text': "Text generation failed - no choices in response",
                        'prompt_used': prompt,
                        'generation_params': {'error': True, 'response': result},
                        'cached': False
                    }

            except Exception as e:
                logger.error(f"Hugging Face API text generation failed: {e}")
                return {
                    'generated_text': "Text generation unavailable",
                    'prompt_used': prompt,
                    'generation_params': {'error': True},
                    'cached': False
                }
        else:
            # Use local model
            tokenizer = cls.get_model('text_tokenizer')
            generator = cls.get_model('text_generator')
            if tokenizer and generator:
                inputs = tokenizer(prompt, return_tensors="pt")
                outputs = generator.generate(
                    inputs,
                    max_length=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
                return tokenizer.decode(outputs[0], skip_special_tokens=True)
            else:
                return "Text generation not available locally. Configure HUGGINGFACE_API_TOKEN to use cloud API."

    @classmethod
    def classify_image(cls, image_path: str):
        """Classify image using either local model or Hugging Face API"""
        if cls._instance is None:
            cls.initialize_models()

        instance = cls._instance

        if instance.use_hf_api:
            # Use Hugging Face API
            try:
                api_config = instance._models.get('image_classification_api')
                if not api_config:
                    raise ValueError("Image classification API not configured")

                # For API, we need to send image as base64
                import base64

                with open(image_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')

                response = instance.call_hf_api(
                    api_config['model'],
                    {
                        "inputs": image_data
                    }
                )

                return response
            except Exception as e:
                logger.error(f"Hugging Face API image classification failed: {e}")
                return [{"label": "unknown", "score": 0.0}]
        else:
            # Use local model
            classifier = cls.get_model('image_classifier')
            if classifier:
                # Open image with PIL
                image = Image.open(image_path)
                return classifier(image)
            else:
                return [{"label": "unknown", "score": 0.0}]