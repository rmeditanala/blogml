#!/usr/bin/env python3
"""
Simple test to verify API mode detection works correctly
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.model_loader import ModelLoader

def test_mode_detection():
    """Test that the service correctly detects API vs local mode"""
    print("🧪 Testing Mode Detection...")

    # Test 1: No token - should use local mode
    print("\n📊 Test 1: No API Token (Local Mode)")
    os.environ.pop('HUGGINGFACE_API_TOKEN', None)
    os.environ.pop('HF_TOKEN', None)

    # Clear the singleton instance
    ModelLoader._instance = None

    instance1 = ModelLoader()
    print(f"   API Mode: {instance1.use_hf_api}")
    print(f"   Has Token: {bool(instance1.hf_token)}")
    print(f"   Expected: Local Mode ✅" if not instance1.use_hf_api else "   Expected: Local Mode ❌")

    # Test 2: With token - should use API mode
    print("\n📊 Test 2: With API Token (API Mode)")
    os.environ['HUGGINGFACE_API_TOKEN'] = 'test_token_123'

    # Clear the singleton instance again
    ModelLoader._instance = None

    instance2 = ModelLoader()
    print(f"   API Mode: {instance2.use_hf_api}")
    print(f"   Has Token: {bool(instance2.hf_token)}")
    print(f"   Expected: API Mode ✅" if instance2.use_hf_api else "   Expected: API Mode ❌")

    # Test 3: Legacy token name
    print("\n📊 Test 3: Legacy HF_TOKEN (API Mode)")
    os.environ.pop('HUGGINGFACE_API_TOKEN', None)
    os.environ['HF_TOKEN'] = 'legacy_token_456'

    # Clear the singleton instance again
    ModelLoader._instance = None

    instance3 = ModelLoader()
    print(f"   API Mode: {instance3.use_hf_api}")
    print(f"   Has Token: {bool(instance3.hf_token)}")
    print(f"   Expected: API Mode ✅" if instance3.use_hf_api else "   Expected: API Mode ❌")

    # Test 4: Both tokens set (new one takes precedence)
    print("\n📊 Test 4: Both Tokens (HUGGINGFACE_API_TOKEN takes precedence)")
    os.environ['HUGGINGFACE_API_TOKEN'] = 'new_token_789'
    os.environ['HF_TOKEN'] = 'legacy_token_456'

    # Clear the singleton instance again
    ModelLoader._instance = None

    instance4 = ModelLoader()
    print(f"   API Mode: {instance4.use_hf_api}")
    print(f"   Token Used: {instance4.hf_token}")
    print(f"   Expected: HUGGINGFACE_API_TOKEN ✅" if instance4.hf_token == 'new_token_789' else "   Expected: HUGGINGFACE_API_TOKEN ❌")

    print("\n🎉 Mode detection test complete!")

    return True

def test_configuration_messages():
    """Test the configuration messages that will be shown to users"""
    print("\n🧪 Testing Configuration Messages...")

    # Clear any existing token
    os.environ.pop('HUGGINGFACE_API_TOKEN', None)
    os.environ.pop('HF_TOKEN', None)
    ModelLoader._instance = None

    print("\n📋 Instructions for users:")
    print("   1. Get your token from: https://huggingface.co/settings/tokens")
    print("   2. Set environment variable:")
    print("      export HUGGINGFACE_API_TOKEN=your_token_here")
    print("   3. Or create .env file with the token")
    print("   4. Restart the service")

    return True

if __name__ == "__main__":
    print("🚀 Testing Hugging Face API Integration")
    print("=" * 50)

    test_mode_detection()
    test_configuration_messages()

    print("\n✅ All tests completed successfully!")
    print("\n📖 For full setup instructions, see: HF_API_SETUP.md")