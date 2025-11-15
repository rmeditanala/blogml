from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import re
import hashlib
import json

from app.services.model_loader import ModelLoader

router = APIRouter()

class TextGenerationRequest(BaseModel):
    prompt: str
    max_length: int = 512
    temperature: float = 0.7
    num_beams: int = 4
    cache_key: Optional[str] = None

class OutlineGenerationRequest(BaseModel):
    topic: str
    num_sections: int = 5
    target_audience: str = "general"

class BlogPostGenerationRequest(BaseModel):
    topic: str
    outline: Optional[List[str]] = None
    tone: str = "informative"  # informative, casual, formal, creative
    target_length: int = 1000

class TextGenerationResponse(BaseModel):
    generated_text: str
    prompt_used: str
    generation_params: Dict[str, Any]
    cached: bool = False

class OutlineResponse(BaseModel):
    outline: List[str]
    topic: str
    estimated_sections: int

class BlogPostResponse(BaseModel):
    post_content: str
    title: str
    sections: List[str]
    metadata: Dict[str, Any]

class TextGenerationService:
    @staticmethod
    def clean_generated_text(text: str) -> str:
        """Clean and format generated text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove potential prompt repetition
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if len(cleaned_lines) > 0 and line.strip() == cleaned_lines[-1].strip():
                continue
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    @staticmethod
    def create_blog_post_prompt(topic: str, outline: List[str] = None, tone: str = "informative") -> str:
        """Create a prompt for blog post generation"""
        tone_instructions = {
            "informative": "Write in an informative and educational tone with clear explanations.",
            "casual": "Write in a friendly, conversational tone that engages readers.",
            "formal": "Write in a professional and formal tone suitable for business audiences.",
            "creative": "Write in a creative and engaging tone with vivid descriptions."
        }

        base_prompt = f"Write a comprehensive blog post about: {topic}\n\n"
        base_prompt += f"Style: {tone_instructions.get(tone, tone_instructions['informative'])}\n\n"

        if outline:
            base_prompt += "Structure:\n"
            for i, section in enumerate(outline, 1):
                base_prompt += f"{i}. {section}\n"
            base_prompt += "\n"

        base_prompt += "Please write a well-structured blog post that covers the topic thoroughly."

        return base_prompt

    @staticmethod
    def create_outline_prompt(topic: str, num_sections: int, audience: str) -> str:
        """Create a prompt for outline generation"""
        prompt = f"Create a detailed outline for a blog post about: {topic}\n\n"
        prompt += f"Target audience: {audience}\n"
        prompt += f"Number of sections: {num_sections}\n\n"
        prompt += "Generate a logical structure with main sections and key points for each section.\n"
        prompt += "Format as a numbered list of section titles."

        return prompt

text_service = TextGenerationService()

@router.post("/text", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    """
    Generate text using FLAN-T5 model
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    if request.max_length > 2048:
        raise HTTPException(status_code=400, detail="Max length cannot exceed 2048")

    try:
        # Try cache first
        redis_client = ModelLoader.get_redis_client()
        cache_key = request.cache_key or hashlib.md5(
            f"{request.prompt}_{request.max_length}_{request.temperature}".encode()
        ).hexdigest()

        if redis_client:
            cached_result = redis_client.get(f"text_gen:{cache_key}")
            if cached_result:
                result = json.loads(cached_result)
                result["cached"] = True
                return TextGenerationResponse(**result)

        # Generate text using Hugging Face API or local model
        generated_text = ModelLoader.generate_text(
            request.prompt,
            max_length=request.max_length
        )
        cleaned_text = text_service.clean_generated_text(generated_text)

        response_data = {
            "generated_text": cleaned_text,
            "prompt_used": request.prompt,
            "generation_params": {
                "max_length": request.max_length,
                "temperature": request.temperature,
                "num_beams": request.num_beams
            },
            "cached": False
        }

        # Cache the result
        if redis_client:
            redis_client.setex(
                f"text_gen:{cache_key}",
                3600,  # 1 hour cache
                json.dumps(response_data)
            )

        return TextGenerationResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")

@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(request: OutlineGenerationRequest):
    """
    Generate an outline for a blog post
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    if request.num_sections < 3 or request.num_sections > 10:
        raise HTTPException(status_code=400, detail="Number of sections must be between 3 and 10")

    try:
        # Create outline prompt
        prompt = text_service.create_outline_prompt(
            request.topic,
            request.num_sections,
            request.target_audience
        )

        # Generate outline
        generation_request = TextGenerationRequest(
            prompt=prompt,
            max_length=300,
            temperature=0.6,
            num_beams=5
        )

        result = await generate_text(generation_request)

        # Parse the generated text into an outline
        lines = result.generated_text.split('\n')
        outline = []

        for line in lines:
            # Remove numbering and clean up
            cleaned_line = re.sub(r'^\d+\.?\s*', '', line).strip()
            if cleaned_line and len(cleaned_line) > 5:
                outline.append(cleaned_line)

        # Ensure we have the right number of sections
        outline = outline[:request.num_sections]
        while len(outline) < request.num_sections:
            outline.append(f"Section {len(outline) + 1}")

        return OutlineResponse(
            outline=outline,
            topic=request.topic,
            estimated_sections=len(outline)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outline generation failed: {str(e)}")

@router.post("/post", response_model=BlogPostResponse)
async def generate_blog_post(request: BlogPostGenerationRequest):
    """
    Generate a complete blog post
    """
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    if request.target_length > 5000:
        raise HTTPException(status_code=400, detail="Target length cannot exceed 5000 words")

    try:
        # Generate outline if not provided
        outline = request.outline
        if not outline:
            outline_request = OutlineGenerationRequest(
                topic=request.topic,
                num_sections=5,
                target_audience="general"
            )
            outline_response = await generate_outline(outline_request)
            outline = outline_response.outline

        # Create blog post prompt
        prompt = text_service.create_blog_post_prompt(
            request.topic,
            outline,
            request.tone
        )

        # Calculate appropriate max_length based on target
        max_length = min(request.target_length * 2, 2048)  # Rough estimate

        # Generate blog post
        generation_request = TextGenerationRequest(
            prompt=prompt,
            max_length=max_length,
            temperature=0.7,
            num_beams=4
        )

        result = await generate_text(generation_request)

        # Generate a title
        title_prompt = f"Create a catchy blog post title about: {request.topic}"
        title_request = TextGenerationRequest(
            prompt=title_prompt,
            max_length=50,
            temperature=0.8,
            num_beams=3
        )
        title_result = await generate_text(title_request)

        # Create response
        return BlogPostResponse(
            post_content=result.generated_text,
            title=title_result.generated_text.strip(),
            sections=outline,
            metadata={
                "topic": request.topic,
                "tone": request.tone,
                "target_length": request.target_length,
                "actual_length": len(result.generated_text.split()),
                "generated_with": "FLAN-T5"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog post generation failed: {str(e)}")

@router.post("/expand")
async def expand_text(
    text: str,
    expansion_type: str = "paragraph",
    target_length: int = 200
):
    """
    Expand existing text (create more detailed content)
    """
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        prompts = {
            "paragraph": f"Expand this into a detailed paragraph: {text}",
            "section": f"Expand this into a comprehensive section with examples: {text}",
            "examples": f"Expand this with practical examples and use cases: {text}",
            "details": f"Add more details and explanations to: {text}"
        }

        prompt = prompts.get(expansion_type, prompts["paragraph"])

        generation_request = TextGenerationRequest(
            prompt=prompt,
            max_length=target_length * 2,
            temperature=0.6,
            num_beams=3
        )

        result = await generate_text(generation_request)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text expansion failed: {str(e)}")