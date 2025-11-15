# Hugging Face API Integration Setup

This guide explains how to set up and use Hugging Face API tokens to avoid downloading large ML models locally.

## 🚀 **Quick Setup**

### 1. Get Your Hugging Face API Token

1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Click "New token"
3. Give it a name (e.g., "blogml-api")
4. Select "Read" permissions (sufficient for inference)
5. Copy the generated token

### 2. Configure the API Token

**Option A: Environment Variable (Recommended)**
```bash
export HUGGINGFACE_API_TOKEN=your_token_here
```

**Option B: .env File**
```bash
# Copy the example file
cp .env.example .env

# Edit the .env file and add your token
HUGGINGFACE_API_TOKEN=your_token_here
```

### 3. Test the Integration

```bash
cd ml-service
python test_hf_api.py
```

## 📋 **Benefits of Using API**

### ✅ **Advantages**
- **No large downloads** - Each model is 100MB-1.5GB
- **No GPU required** - Models run on Hugging Face's infrastructure
- **Always up-to-date** - Models are automatically updated
- **High performance** - Fast inference on optimized hardware
- **Easy setup** - Just need API token, no model management

### ⚠️ **Limitations**
- **Rate limits** - Free tier has usage limits
- **Internet required** - API calls need internet connection
- **Potential latency** - Network calls vs local processing
- **Cost considerations** - Excessive usage may incur charges

## 🔧 **How It Works**

The ML service now supports **dual mode** operation:

1. **API Mode** (when `HUGGINGFACE_API_TOKEN` is set)
   - Uses Hugging Face Inference API
   - No local model downloads
   - Faster setup and lower resource usage

2. **Local Mode** (when no token is configured)
   - Downloads and runs models locally
   - Requires more disk space and RAM
   - Works offline after initial download

## 📊 **Available Models**

### Sentiment Analysis
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Labels**: NEGATIVE, NEUTRAL, POSITIVE
- **Best for**: Social media content, blog comments

### Text Generation
- **Model**: `google/flan-t5-base`
- **Use case**: Content generation, summaries, outlines
- **Configurable**: Temperature, max length, sampling

### Image Classification
- **Model**: `microsoft/resnet-50`
- **Use case**: Image categorization, content analysis
- **Format**: Supports base64 image upload

## 🛠️ **Configuration Options**

### Environment Variables

```bash
# Hugging Face API Token (Required for API mode)
HUGGINGFACE_API_TOKEN=your_token_here

# Alternative token name (for compatibility)
HF_TOKEN=your_token_here

# Redis Configuration (Optional, for caching)
REDIS_HOST=localhost
REDIS_PORT=6379

# Force Local Models (Optional)
# Uncomment to always use local models even with API token
# FORCE_LOCAL_MODELS=true
```

### Model-Specific Settings

The service automatically handles different model formats and provides fallbacks:

```python
# Automatic label mapping
label_map = {
    'LABEL_0': 'NEGATIVE',  # Twitter RoBERTa format
    'LABEL_1': 'NEUTRAL',   # Twitter RoBERTa format
    'LABEL_2': 'POSITIVE',  # Twitter RoBERTa format
    'NEGATIVE': 'NEGATIVE', # Standard format
    'NEUTRAL': 'NEUTRAL',   # Standard format
    'POSITIVE': 'POSITIVE', # Standard format
}
```

## 🧪 **Testing the API**

### Test Script
```bash
# Run comprehensive tests
python test_hf_api.py
```

### Manual Testing
```bash
# Test sentiment analysis
curl -X POST "http://localhost:8000/sentiment/" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this blog post!"}'
```

### Expected Response
```json
{
  "sentiment": "POSITIVE",
  "confidence": 0.98,
  "cached": false
}
```

## 🔄 **Switching Between Modes**

### From Local to API
1. Set your API token
2. Restart the service
3. Service automatically detects and uses API mode

### From API to Local
1. Remove or unset `HUGGINGFACE_API_TOKEN`
2. Restart the service
3. Service will download and use local models

```bash
# Switch to API mode
export HUGGINGFACE_API_TOKEN=your_token_here
python -m uvicorn app.main:app --reload

# Switch to local mode
unset HUGGINGFACE_API_TOKEN
python -m uvicorn app.main:app --reload
```

## 🚨 **Troubleshooting**

### API Token Not Working
```bash
# Check if token is set
echo $HUGGINGFACE_API_TOKEN

# Test token with curl
curl -H "Authorization: Bearer your_token_here" \
     https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest \
     -d '{"inputs": "test"}'
```

### Service Still Downloading Models
1. Check that the token is correctly set
2. Restart the service completely
3. Check service logs for "Using Hugging Face API" message

### Rate Limit Errors
- Wait a few minutes between requests
- Consider upgrading to paid tier for heavy usage
- Implement caching on your end

### Network Issues
- Check internet connection
- Verify Hugging Face status: https://status.huggingface.co/
- Check if your token has the right permissions

## 📈 **Performance Optimization**

### Enable Redis Caching
```bash
# Start Redis
docker run -d -p 6379:6379 redis

# Configure service
REDIS_HOST=localhost
```

### Batch Processing
```bash
# Process multiple texts at once
curl -X POST "http://localhost:8000/sentiment/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Great post!", "Terrible content", "Not bad"]}'
```

## 💡 **Best Practices**

1. **Store tokens securely** - Never commit tokens to version control
2. **Use environment variables** - Better security than .env files
3. **Implement retry logic** - Handle network failures gracefully
4. **Cache responses** - Reduce API calls and improve performance
5. **Monitor usage** - Track API calls to avoid rate limits
6. **Fallback handling** - Provide local model fallbacks when possible

## 🔗 **Useful Links**

- [Hugging Face Inference API Docs](https://huggingface.co/docs/api-inference/index)
- [Available Models](https://huggingface.co/models)
- [API Pricing](https://huggingface.co/pricing)
- [Rate Limits](https://huggingface.co/docs/api-inference/index#rate-limits)

## 🆘 **Getting Help**

If you encounter issues:

1. Check the service logs for error messages
2. Verify your API token has the right permissions
3. Test with the provided test script
4. Check Hugging Face service status
5. Ensure all dependencies are up to date

For API-specific issues, refer to the [Hugging Face documentation](https://huggingface.co/docs/api-inference).