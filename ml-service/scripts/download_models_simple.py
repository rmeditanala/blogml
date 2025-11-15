#!/usr/bin/env python3
"""
Simple alternative script to download pre-trained models for BlogML ML Service
This version uses basic huggingface download without progress bars but with better error handling

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
        'model_name': 'google/flan-t5-small',  # Smaller model for faster download
        'model_class': AutoModelForSeq2SeqLM,
        'description': 'Text generation model (small)',
        'size_mb': '~300MB'
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

def download_model_simple(model_key, model_config, models_dir):
    """Download a specific model using simple approach"""
    logger.info(f"📥 Downloading {model_config['description']}...")
    logger.info(f"Model: {model_config['model_name']}")
    logger.info(f"Estimated size: {model_config['size_mb']}")
    logger.info("⏳ This may take several minutes. Please be patient...")

    try:
        if model_key == 'sentiment':
            # Download sentiment analysis model
            model_path = os.path.join(models_dir, 'sentiment')

            logger.info("🔧 Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_config['model_name'],
                trust_remote_code=True,
                resume_download=True
            )
            tokenizer.save_pretrained(model_path)
            logger.info("✅ Tokenizer downloaded successfully")

            logger.info("🧠 Downloading model...")
            model = model_config['model_class'].from_pretrained(
                model_config['model_name'],
                trust_remote_code=True,
                resume_download=True
            )
            model.save_pretrained(model_path)
            logger.info("✅ Model downloaded successfully")

            logger.info(f"🎉 Sentiment model saved to: {model_path}")

        elif model_key == 'text_generation':
            # Download text generation model
            model_path = os.path.join(models_dir, 'text_generation')

            logger.info("🔧 Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(
                model_config['model_name'],
                trust_remote_code=True,
                resume_download=True
            )
            tokenizer.save_pretrained(model_path)
            logger.info("✅ Tokenizer downloaded successfully")

            logger.info("🧠 Downloading model...")
            model = model_config['model_class'].from_pretrained(
                model_config['model_name'],
                trust_remote_code=True,
                resume_download=True
            )
            model.save_pretrained(model_path)
            logger.info("✅ Model downloaded successfully")

            logger.info(f"🎉 Text generation model saved to: {model_path}")

        elif model_key == 'image_classification':
            # Download image classification model using pipeline
            model_path = os.path.join(models_dir, 'image_classification')

            logger.info("🖼️  Downloading image classification pipeline...")
            classifier = pipeline(
                "image-classification",
                model=model_config['model_name'],
                trust_remote_code=True
            )

            # Save the model and tokenizer
            if hasattr(classifier, 'model') and classifier.model:
                classifier.model.save_pretrained(model_path)
            if hasattr(classifier, 'image_processor') and classifier.image_processor:
                classifier.image_processor.save_pretrained(model_path)

            logger.info("✅ Image classification model downloaded successfully")
            logger.info(f"🎉 Image classification model saved to: {model_path}")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to download {model_key}: {str(e)}")

        # Provide helpful troubleshooting tips
        logger.error("\n🔧 Troubleshooting tips:")
        logger.error("1. Check your internet connection")
        logger.error("2. Try downloading a smaller model first: python download_models_simple.py sentiment")
        logger.error("3. Make sure you have enough disk space")
        logger.error("4. Try running the script again (it may resume partial downloads)")

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
    logger.info("🚀 Starting BlogML model download (Simple Mode)...")

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
            logger.info("Example usage: python download_models_simple.py sentiment")
            sys.exit(1)

        # Download only the requested model
        model_config = MODELS[requested_model]
        success = download_model_simple(requested_model, model_config, models_dir)

        if success:
            logger.info(f"✅ Successfully downloaded {requested_model} model!")
        else:
            logger.error(f"❌ Failed to download {requested_model} model!")
            sys.exit(1)
    else:
        # Download all models
        logger.info("Downloading all models...")
        logger.info("💡 Tip: You can download models individually: python download_models_simple.py <model_name>")

        success_count = 0
        for model_key, model_config in MODELS.items():
            logger.info(f"\n{'='*50}")
            success = download_model_simple(model_key, model_config, models_dir)
            if success:
                success_count += 1
            logger.info(f"{'='*50}")

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
    logger.info("💡 If you had issues, try: pip install --upgrade transformers torch")

if __name__ == "__main__":
    main()