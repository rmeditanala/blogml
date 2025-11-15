# Sentiment Analysis Model Options

This document provides information about different sentiment analysis models you can use in the BlogML ML service.

## 🎯 **Current Model (Recommended)**
**Model:** `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Size:** ~300MB
- **Type:** Multi-label sentiment analysis
- **Labels:** `LABEL_0` (Negative), `LABEL_1` (Neutral), `LABEL_2` (Positive)
- **Accuracy:** High (trained on Twitter data)
- **Speed:** Fast
- **Best for:** Social media content, general text

## 🔄 **Alternative Models**

### **1. Original Model**
**Model:** `distilbert-base-uncased-finetuned-sst-2-english`
- **Size:** ~250MB
- **Type:** Binary/Negative/Positive classification
- **Labels:** `NEGATIVE`, `POSITIVE` (sometimes `NEUTRAL`)
- **Accuracy:** Good
- **Speed:** Very Fast
- **Best for:** General purpose, quick analysis

### **2. More Accurate Model**
**Model:** `siebert/sentiment-roberta-large-english`
- **Size:** ~1.4GB
- **Type:** Sentiment classification
- **Labels:** `NEGATIVE`, `NEUTRAL`, `POSITIVE`
- **Accuracy:** Very High
- **Speed:** Slower
- **Best for:** Critical applications requiring high accuracy

### **3. Emotion Classification**
**Model:** `bhadresh-savani/bert-base-uncased-emotion`
- **Size:** ~500MB
- **Type:** Emotion classification
- **Labels:** `sadness`, `joy`, `love`, `anger`, `fear`, `surprise`
- **Accuracy:** Good for emotions
- **Speed:** Medium
- **Best for:** Detailed emotional analysis

### **4. Multilingual Model**
**Model:** `nlptown/bert-base-multilingual-uncased-sentiment`
- **Size:** ~420MB
- **Type:** Multi-lingual sentiment
- **Labels:** 1-5 star ratings (converted to sentiment)
- **Accuracy:** Good
- **Speed:** Medium
- **Best for:** Multiple languages

### **5. Movie Reviews**
**Model:** `textattack/bert-base-uncased-imdb`
- **Size:** ~420MB
- **Type:** Movie review sentiment
- **Labels:** `NEGATIVE`, `POSITIVE`
- **Accuracy:** Very High (for reviews)
- **Speed:** Medium
- **Best for:** Review-style content

## 🛠️ **How to Change Models**

### Option 1: Edit Download Scripts
1. Open `ml-service/scripts/download_models.py`
2. Find the `sentiment` section
3. Change `model_name` to your desired model
4. Update `size_mb` estimate
5. Run the download script again

### Option 2: Edit Download Scripts (Simple)
1. Open `ml-service/scripts/download_models_simple.py`
2. Find the `sentiment` section
3. Change `model_name` to your desired model
4. Update `size_mb` estimate
5. Run: `python download_models_simple.py sentiment`

### Example: Switch to Original Model
```python
'sentiment': {
    'model_name': 'distilbert-base-uncased-finetuned-sst-2-english',
    'model_class': AutoModelForSequenceClassification,
    'description': 'Original sentiment analysis model',
    'size_mb': '~250MB'
},
```

## 🔧 **Code Updates Needed**

The sentiment analysis code in `app/routes/sentiment.py` already handles multiple model formats. However, if you use a model with different labels, you may need to update the `label_map`:

```python
# Update this in app/routes/sentiment.py
label_map = {
    'LABEL_0': 'NEGATIVE',    # Twitter RoBERTa
    'LABEL_1': 'NEUTRAL',     # Twitter RoBERTa
    'LABEL_2': 'POSITIVE',    # Twitter RoBERTa
    'POSITIVE': 'POSITIVE',   # Standard models
    'NEGATIVE': 'NEGATIVE',
    'NEUTRAL': 'NEUTRAL',
    # Add your model's labels here
}
```

## 📊 **Recommendations**

### **For Blog Comments:**
- ✅ **Current**: `cardiffnlp/twitter-roberta-base-sentiment-latest` (Great for social media text)
- ✅ **Alternative**: `distilbert-base-uncased-finetuned-sst-2-english` (Fast and reliable)

### **For High Accuracy:**
- ✅ **Best**: `siebert/sentiment-roberta-large-english` (Most accurate)
- ⚠️ **Trade-off**: Larger size, slower speed

### **For Multiple Languages:**
- ✅ **Best**: `nlptown/bert-base-multilingual-uncased-sentiment`

### **For Emotional Analysis:**
- ✅ **Best**: `bhadresh-savani/bert-base-uncased-emotion`

## 🚀 **Quick Start**

1. **Download preferred model:**
   ```bash
   cd ml-service
   python scripts/download_models_simple.py sentiment
   ```

2. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/sentiment/" \
     -H "Content-Type: application/json" \
     -d '{"text": "I love this blog post!"}'
   ```

3. **Expected Response:**
   ```json
   {
     "sentiment": "POSITIVE",
     "confidence": 0.98,
     "cached": false
   }
   ```