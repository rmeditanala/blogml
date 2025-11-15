from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import hashlib

from app.services.model_loader import ModelLoader

router = APIRouter()

class UserProfile(BaseModel):
    user_id: int
    read_posts: List[int] = []
    liked_posts: List[int] = []
    interaction_history: List[Dict[str, Any]] = []

class PostContent(BaseModel):
    post_id: int
    title: str
    content: str
    tags: List[str] = []

class RecommendationRequest(BaseModel):
    user_profile: UserProfile
    available_posts: List[PostContent]
    num_recommendations: int = 10

class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    explanation: Optional[str] = None

class SimilarPostsRequest(BaseModel):
    post_id: int
    post_content: PostContent
    similar_posts: List[PostContent]
    num_similar: int = 5

class SimilarPostsResponse(BaseModel):
    similar_posts: List[Dict[str, Any]]

class RecommendationEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )

    def extract_features(self, posts: List[PostContent]) -> np.ndarray:
        """Extract TF-IDF features from posts"""
        texts = []
        for post in posts:
            # Combine title, content, and tags
            text = f"{post.title} {post.content} {' '.join(post.tags)}"
            texts.append(text.lower())

        return self.vectorizer.fit_transform(texts)

    def collaborative_filtering(self, user_profile: UserProfile, available_posts: List[PostContent]) -> Dict[int, float]:
        """
        Simple collaborative filtering based on user interactions
        """
        scores = {}

        # Boost scores based on user's liked similar content
        liked_tags = set()
        for post_id in user_profile.liked_posts:
            # This would normally fetch from database
            liked_tags.update(['technology', 'programming', 'web'])  # Example tags

        for post in available_posts:
            score = 0.5  # Base score

            # Boost if post has tags similar to liked content
            for tag in post.tags:
                if tag.lower() in liked_tags:
                    score += 0.3

            # Boost based on interaction patterns
            if len(user_profile.read_posts) > 0:
                # Simple recency boost - newer content gets slight boost
                score *= 1.1

            scores[post.post_id] = min(score, 1.0)

        return scores

    def content_based_filtering(self, user_profile: UserProfile, available_posts: List[PostContent]) -> Dict[int, float]:
        """
        Content-based filtering using text similarity
        """
        if not user_profile.read_posts:
            # No history, return diversity-based scores
            return {post.post_id: 0.5 for post in available_posts}

        # This would normally fetch the user's read posts content
        # For demo, we'll use a simple approach
        user_interest_text = "technology programming web development"  # Based on typical user

        scores = {}
        for post in available_posts:
            post_text = f"{post.title} {post.content} {' '.join(post.tags)}".lower()

            # Simple keyword matching
            common_words = set(user_interest_text.split()) & set(post_text.split())
            score = len(common_words) * 0.1
            scores[post.post_id] = min(score + 0.3, 1.0)

        return scores

recommendation_engine = RecommendationEngine()

@router.post("/user", response_model=RecommendationResponse)
async def get_user_recommendations(request: RecommendationRequest):
    """
    Get personalized recommendations for a user
    """
    if not request.available_posts:
        raise HTTPException(status_code=400, detail="No available posts provided")

    try:
        # Get collaborative filtering scores
        cf_scores = recommendation_engine.collaborative_filtering(
            request.user_profile,
            request.available_posts
        )

        # Get content-based scores
        cb_scores = recommendation_engine.content_based_filtering(
            request.user_profile,
            request.available_posts
        )

        # Combine scores (weighted average)
        combined_scores = {}
        for post_id in cf_scores:
            combined_scores[post_id] = (cf_scores[post_id] * 0.6 + cb_scores[post_id] * 0.4)

        # Sort by score and get top recommendations
        sorted_posts = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_posts = sorted_posts[:request.num_recommendations]

        recommendations = []
        for post_id, score in top_posts:
            post = next((p for p in request.available_posts if p.post_id == post_id), None)
            if post:
                recommendations.append({
                    "post_id": post_id,
                    "title": post.title,
                    "score": score,
                    "reason": "Based on your reading history and similar users' preferences"
                })

        return RecommendationResponse(
            recommendations=recommendations,
            explanation="Personalized recommendations based on your reading history and similar users' preferences"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")

@router.post("/similar", response_model=SimilarPostsResponse)
async def get_similar_posts(request: SimilarPostsRequest):
    """
    Get posts similar to a given post
    """
    if not request.similar_posts:
        raise HTTPException(status_code=400, detail="No similar posts provided")

    try:
        # Create feature matrix for all posts
        all_posts = [request.post_content] + request.similar_posts
        features = recommendation_engine.extract_features(all_posts)

        # Calculate similarity scores
        target_vector = features[0:1]  # First post is the target
        similarities = cosine_similarity(target_vector, features[1:]).flatten()

        # Get top similar posts
        top_indices = np.argsort(similarities)[::-1][:request.num_similar]

        similar_posts = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                post = request.similar_posts[idx]
                similar_posts.append({
                    "post_id": post.post_id,
                    "title": post.title,
                    "similarity_score": float(similarities[idx])
                })

        return SimilarPostsResponse(similar_posts=similar_posts)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity analysis failed: {str(e)}")