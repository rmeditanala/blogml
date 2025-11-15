#!/usr/bin/env python3
"""
Script to download pre-trained models for BlogML ML Service
"""

import os
import sys
import logging
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
from transformers import pipeline
import torch

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configurations
MODELS = {
    'sentiment': {
        'model_name': 'distilbert-base-uncased-finetuned-sst-2-english',
        'model_class': AutoModelForSequenceClassification,
        'description': 'Sentiment analysis model',
        'size_mb': '~250MB'
    },
    'text_generation': {
        'model_name': 'google/flan-t5-base',
        'model_class': AutoModelForSeq2SeqLM,
        'description': 'Text generation model',
        'size_mb': '~900MB'
    },
    'image_classification': {
        'model_name': 'microsoft/resnet-50',
        'model_class': None,  # Using pipeline for this one
        'description': 'Image classification model',
        'size_mb': '~100MB'
    }
}

def check_disk_space():
    """Check if there's enough disk space"""
    import shutil

    total, used, free = shutil.disk_usage("/")
    free_gb = free // (1024**3)

    logger.info(f"Available disk space: {free_gb} GB")

    if free_gb < 2:
        logger.error("Insufficient disk space. At least 2 GB required for all models.")
        return False

    return True

def download_model(model_key, model_config, models_dir):
    """Download a specific model"""
    logger.info(f"Downloading {model_config['description']}...")
    logger.info(f"Model: {model_config['model_name']}")
    logger.info(f"Estimated size: {model_config['size_mb']}")

    try:
        if model_key == 'sentiment':
            # Download sentiment analysis model
            model_path = os.path.join(models_dir, 'sentiment')

            logger.info("Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_config['model_name'])
            tokenizer.save_pretrained(model_path)

            logger.info("Downloading model...")
            model = model_config['model_class'].from_pretrained(model_config['model_name'])
            model.save_pretrained(model_path)

            logger.info(f"✅ Sentiment model saved to: {model_path}")

        elif model_key == 'text_generation':
            # Download text generation model
            model_path = os.path.join(models_dir, 'text_generation')

            logger.info("Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_config['model_name'])
            tokenizer.save_pretrained(model_path)

            logger.info("Downloading model...")
            model = model_config['model_class'].from_pretrained(model_config['model_name'])
            model.save_pretrained(model_path)

            logger.info(f"✅ Text generation model saved to: {model_path}")

        elif model_key == 'image_classification':
            # Download image classification model using pipeline
            model_path = os.path.join(models_dir, 'image_classification')

            logger.info("Downloading image classification pipeline...")
            classifier = pipeline(
                "image-classification",
                model=model_config['model_name']
            )

            # Save the model and tokenizer
            classifier.model.save_pretrained(model_path)
            classifier.tokenizer.save_pretrained(model_path)

            logger.info(f"✅ Image classification model saved to: {model_path}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to download {model_key}: {str(e)}")
        return False

def verify_model(model_path):
    """Verify that a model was downloaded correctly"""
    required_files = ['config.json']

    for file in required_files:
        if not os.path.exists(os.path.join(model_path, file)):
            return False

    return True

def main():
    """Main function"""
    logger.info("🚀 Starting BlogML model download...")

    # Create models directory
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)

    logger.info(f"Models will be saved to: {models_dir}")

    # Check disk space
    if not check_disk_space():
        sys.exit(1)

    # Check if specific model requested
    if len(sys.argv) > 1:
        requested_model = sys.argv[1]
        if requested_model not in MODELS:
            logger.error(f"Unknown model: {requested_model}")
            logger.info(f"Available models: {', '.join(MODELS.keys())}")
            sys.exit(1)

        # Download only the requested model
        model_config = MODELS[requested_model]
        success = download_model(requested_model, model_config, models_dir)

        if success:
            logger.info(f"✅ Successfully downloaded {requested_model} model!")
        else:
            logger.error(f"❌ Failed to download {requested_model} model!")
            sys.exit(1)
    else:
        # Download all models
        logger.info("Downloading all models...")

        success_count = 0
        for model_key, model_config in MODELS.items():
            success = download_model(model_key, model_config, models_dir)
            if success:
                success_count += 1

        logger.info(f"\n🎉 Download complete! Successfully downloaded {success_count}/{len(MODELS)} models")

    # Verify all downloads
    logger.info("\n🔍 Verifying downloads...")

    for model_key in MODELS.keys():
        model_path = models_dir / model_key
        if model_path.exists() and verify_model(model_path):
            logger.info(f"✅ {model_key} model verified")
        else:
            logger.warning(f"⚠️  {model_key} model verification failed")

    # Create .gitignore for models directory
    gitignore_path = models_dir / ".gitignore"
    if not gitignore_path.exists():
        with open(gitignore_path, 'w') as f:
            f.write("# Ignore model files (too large for git)\n")
            f.write("*\n")
            f.write("!.gitignore\n")
        logger.info("Created .gitignore in models directory")

    logger.info("\n🎊 All done! Models are ready to use.")
    logger.info("Run the FastAPI server to start using the models.")

if __name__ == "__main__":
    main()