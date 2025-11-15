#!/usr/bin/env python3
"""
Script to download pre-trained models for BlogML ML Service

⚠️  IMPORTANT: This script downloads large ML models locally (1.5GB+ total).
    For better performance and easier setup, we recommend using Hugging Face API:

    # Set up API token (recommended):
    export HUGGINGFACE_API_TOKEN=your_token_here

    # Start service - will automatically use API:
    uvicorn app.main:app --reload

    See HF_API_SETUP.md for detailed instructions.

Use this script only if you need offline functionality or prefer local models.
"""

import os
import sys
import logging
import time
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
from transformers import pipeline
import torch
from tqdm import tqdm
import requests
import tempfile

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model configurations
MODELS = {
    'sentiment': {
        'model_name': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
        'model_class': AutoModelForSequenceClassification,
        'description': 'Twitter sentiment analysis model (multi-label)',
        'size_mb': '~300MB'
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

def download_with_progress(url, filename, description):
    """Download file with progress bar"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1KB chunks

        with open(filename, 'wb') as file:
            with tqdm(total=total_size, unit='iB', unit_scale=True, desc=description) as pbar:
                for data in response.iter_content(block_size):
                    size = file.write(data)
                    pbar.update(size)

        return True
    except Exception as e:
        logger.error(f"Download failed: {str(e)}")
        if os.path.exists(filename):
            os.remove(filename)
        return False

def download_model(model_key, model_config, models_dir, max_retries=3):
    """Download a specific model with progress tracking and retry logic"""
    logger.info(f"📥 Downloading {model_config['description']}...")
    logger.info(f"Model: {model_config['model_name']}")
    logger.info(f"Estimated size: {model_config['size_mb']}")

    model_path = os.path.join(models_dir, model_key)
    os.makedirs(model_path, exist_ok=True)

    for attempt in range(max_retries):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt + 1}/{max_retries}...")

            if model_key == 'sentiment':
                # Download sentiment analysis model
                logger.info("🔧 Downloading tokenizer...")
                with tqdm(desc="Downloading tokenizer", unit="files") as pbar:
                    tokenizer = AutoTokenizer.from_pretrained(
                        model_config['model_name'],
                        cache_dir=model_path,
                        local_files_only=False
                    )
                    tokenizer.save_pretrained(model_path)
                    pbar.update(1)

                logger.info("🧠 Downloading model (this may take a while)...")
                with tqdm(desc="Downloading model", unit="files") as pbar:
                    model = model_config['model_class'].from_pretrained(
                        model_config['model_name'],
                        cache_dir=model_path,
                        local_files_only=False
                    )
                    model.save_pretrained(model_path)
                    pbar.update(1)

                logger.info(f"✅ Sentiment model saved to: {model_path}")

            elif model_key == 'text_generation':
                # Download text generation model
                logger.info("🔧 Downloading tokenizer...")
                with tqdm(desc="Downloading tokenizer", unit="files") as pbar:
                    tokenizer = AutoTokenizer.from_pretrained(
                        model_config['model_name'],
                        cache_dir=model_path,
                        local_files_only=False
                    )
                    tokenizer.save_pretrained(model_path)
                    pbar.update(1)

                logger.info("🧠 Downloading model (this may take a while - it's a large model!)...")
                with tqdm(desc="Downloading model", unit="files") as pbar:
                    model = model_config['model_class'].from_pretrained(
                        model_config['model_name'],
                        cache_dir=model_path,
                        local_files_only=False
                    )
                    model.save_pretrained(model_path)
                    pbar.update(1)

                logger.info(f"✅ Text generation model saved to: {model_path}")

            elif model_key == 'image_classification':
                # Download image classification model using pipeline
                logger.info("🖼️  Downloading image classification pipeline...")
                with tqdm(desc="Downloading pipeline", unit="files") as pbar:
                    classifier = pipeline(
                        "image-classification",
                        model=model_config['model_name'],
                        cache_dir=model_path
                    )

                    # Save the model and tokenizer
                    if hasattr(classifier, 'model') and classifier.model:
                        classifier.model.save_pretrained(model_path)
                    if hasattr(classifier, 'image_processor') and classifier.image_processor:
                        classifier.image_processor.save_pretrained(model_path)
                    elif hasattr(classifier, 'tokenizer') and classifier.tokenizer:
                        classifier.tokenizer.save_pretrained(model_path)

                    pbar.update(1)

                logger.info(f"✅ Image classification model saved to: {model_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Attempt {attempt + 1} failed for {model_key}: {str(e)}")

            # Clean up partial download
            if os.path.exists(model_path):
                import shutil
                try:
                    shutil.rmtree(model_path)
                    os.makedirs(model_path, exist_ok=True)
                except:
                    pass

            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5  # Exponential backoff
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ All {max_retries} attempts failed for {model_key}")
                return False

    return False

def verify_model(model_path):
    """Verify that a model was downloaded correctly"""
    required_files = ['config.json']

    for file in required_files:
        if not os.path.exists(os.path.join(model_path, file)):
            return False

    return True

def check_requirements():
    """Check if required packages are installed"""
    try:
        import tqdm
        import requests
        return True
    except ImportError as e:
        logger.error(f"❌ Missing required package: {str(e)}")
        logger.info("Please install missing packages with: pip install tqdm requests")
        return False

def main():
    """Main function"""
    logger.info("🚀 Starting BlogML model download...")

    # Check requirements
    if not check_requirements():
        sys.exit(1)

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