#!/usr/bin/env python3
"""
Test script to verify Hugging Face API integration
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.model_loader import ModelLoader

def test_api_configuration():
    """Test that API configuration is working"""
    print("🧪 Testing Hugging Face API Configuration...")

    # Initialize the model loader
    ModelLoader.initialize_models()
    instance = ModelLoader._instance

    # Check API configuration
    print(f"📊 API Mode: {'✅ Hugging Face API' if instance.use_hf_api else '❌ Local Models'}")
    print(f"🔑 API Token: {'✅ Configured' if instance.hf_token else '❌ Not configured'}")

    if not instance.use_hf_api:
        print("\n⚠️  Hugging Face API token not found!")
        print("Please set HUGGINGFACE_API_TOKEN environment variable:")
        print("export HUGGINGFACE_API_TOKEN=your_token_here")
        print("Or create a .env file with the token.")
        return False

    return True

def test_sentiment_analysis():
    """Test sentiment analysis via API"""
    print("\n🧪 Testing Sentiment Analysis...")

    test_texts = [
        "I love this blog post! It's amazing.",
        "This is terrible and I hate it.",
        "The weather is okay today."
    ]

    for text in test_texts:
        try:
            result = ModelLoader.analyze_sentiment(text)
            if result and len(result) > 0:
                prediction = result[0]
                print(f"✅ '{text}' -> {prediction.get('label', 'UNKNOWN')} ({prediction.get('score', 0):.3f})")
            else:
                print(f"❌ '{text}' -> No result")
        except Exception as e:
            print(f"❌ '{text}' -> Error: {str(e)}")
            return False

    return True

def test_text_generation():
    """Test text generation via API"""
    print("\n🧪 Testing Text Generation...")

    try:
        result = ModelLoader.generate_text("The future of AI is", max_length=50)
        if isinstance(result, str) and result.strip():
            print(f"✅ Generated text: {result[:100]}...")
            return True
        else:
            print(f"❌ Unexpected result: {result}")
            return False
    except Exception as e:
        print(f"❌ Text generation failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Hugging Face API Integration")
    print("=" * 50)

    # Test configuration
    if not test_api_configuration():
        print("\n❌ Configuration test failed!")
        sys.exit(1)

    # Test sentiment analysis
    if not test_sentiment_analysis():
        print("\n❌ Sentiment analysis test failed!")
        sys.exit(1)

    # Test text generation
    if not test_text_generation():
        print("\n❌ Text generation test failed!")
        sys.exit(1)

    print("\n🎉 All tests passed!")
    print("✅ Hugging Face API integration is working correctly!")

if __name__ == "__main__":
    main()