"""
NLP Router - HuggingFace Emotion Analysis
Provides sentiment and emotion analysis for chat messages
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import os

router = APIRouter(prefix="/nlp", tags=["NLP"])

# HuggingFace Inference API (free tier)
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Emotion labels
EMOTIONS = [
    "joy", "sadness", "anger", "fear", "surprise", 
    "neutral", "disgust", "love", "excitement", "hope"
]

# Sentiment labels
SENTIMENTS = ["positive", "negative", "neutral"]


class EmotionResult(BaseModel):
    """Model for emotion analysis result"""
    label: str
    score: float


class SentimentResult(BaseModel):
    """Model for sentiment analysis result"""
    label: str
    score: float


class TextAnalysisRequest(BaseModel):
    """Request for text analysis"""
    text: str


class ConversationAnalysis(BaseModel):
    """Full conversation analysis"""
    overall_sentiment: SentimentResult
    dominant_emotion: EmotionResult
    emotion_trend: List[EmotionResult]
    suggested_mood: str


@router.post("/emotions")
async def analyze_emotions(request: TextAnalysisRequest) -> List[EmotionResult]:
    """
    Analyze emotions in text using HuggingFace emotion model
    """
    if not HUGGINGFACE_API_KEY:
        # Fallback to simple rule-based analysis
        return _simple_emotion_analysis(request.text)

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        try:
            response = await client.post(
                HUGGINGFACE_API_URL + "j-hartmann/emotion-english-distilroberta-base",
                headers=headers,
                json={"inputs": request.text},
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data[0]:
                    results.append(EmotionResult(
                        label=item["label"],
                        score=item["score"]
                    ))
                return sorted(results, key=lambda x: x.score, reverse=True)
            elif response.status_code == 503:
                # Model loading, use fallback
                return _simple_emotion_analysis(request.text)
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"HuggingFace API error: {str(e)}")


@router.post("/sentiment")
async def analyze_sentiment(request: TextAnalysisRequest) -> List[SentimentResult]:
    """
    Analyze sentiment in text using HuggingFace sentiment model
    """
    if not HUGGINGFACE_API_KEY:
        # Fallback to simple rule-based analysis
        return _simple_sentiment_analysis(request.text)

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        
        try:
            response = await client.post(
                HUGGINGFACE_API_URL + "distilbert-base-uncased-finetuned-sst-2-english",
                headers=headers,
                json={"inputs": request.text},
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data[0]:
                    results.append(SentimentResult(
                        label=item["label"],
                        score=item["score"]
                    ))
                return sorted(results, key=lambda x: x.score, reverse=True)
            elif response.status_code == 503:
                # Model loading, use fallback
                return _simple_sentiment_analysis(request.text)
            else:
                raise HTTPException(status_code=response.status_code, detail=response.text)
                
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"HuggingFace API error: {str(e)}")


@router.post("/analyze")
async def analyze_text(request: TextAnalysisRequest) -> ConversationAnalysis:
    """
    Full text analysis - emotions and sentiment
    """
    emotions = await analyze_emotions(request)
    sentiments = await analyze_sentiment(request)
    
    dominant_emotion = emotions[0] if emotions else EmotionResult(label="neutral", score=1.0)
    overall_sentiment = sentiments[0] if sentiments else SentimentResult(label="neutral", score=1.0)
    
    suggested_mood = _get_mood_for_emotion(dominant_emotion.label)
    
    return ConversationAnalysis(
        overall_sentiment=overall_sentiment,
        dominant_emotion=dominant_emotion,
        emotion_trend=emotions[:3],
        suggested_mood=suggested_mood,
    )


@router.post("/conversation")
async def analyze_conversation(messages: List[dict]) -> ConversationAnalysis:
    """
    Analyze a conversation and return overall analysis
    """
    if not messages:
        return ConversationAnalysis(
            overall_sentiment=SentimentResult(label="neutral", score=1.0),
            dominant_emotion=EmotionResult(label="neutral", score=1.0),
            emotion_trend=[],
            suggested_mood="neutral",
        )
    
    # Analyze last few messages
    recent_messages = messages[-5:]
    combined_text = " ".join([msg.get("content", "") for msg in recent_messages])
    
    return await analyze_text(TextAnalysisRequest(text=combined_text))


@router.get("/emotions")
async def get_available_emotions() -> dict:
    """
    Get list of available emotions
    """
    return {
        "emotions": EMOTIONS,
        "sentiments": SENTIMENTS,
    }


@router.post("/companion-response-emotion")
async def get_companion_emotional_response(emotion: str) -> dict:
    """
    Get emotional context for companion response based on user emotion
    """
    emotional_responses = {
        "joy": {
            "companion_mood": "happy",
            "response_style": "enthusiastic",
            "suggested_reaction": "I'm glad you're feeling happy!",
        },
        "sadness": {
            "companion_mood": "supportive",
            "response_style": "gentle",
            "suggested_reaction": "I'm here for you. Would you like to talk about it?",
        },
        "anger": {
            "companion_mood": "calm",
            "response_style": "patient",
            "suggested_reaction": "I understand you're frustrated. Take your time.",
        },
        "fear": {
            "companion_mood": "reassuring",
            "response_style": "comforting",
            "suggested_reaction": "Don't worry, we'll face this together.",
        },
        "neutral": {
            "companion_mood": "neutral",
            "response_style": "friendly",
            "suggested_reaction": "How can I help you today?",
        },
        "love": {
            "companion_mood": "warm",
            "response_style": "affectionate",
            "suggested_reaction": "That's wonderful to hear!",
        },
        "excitement": {
            "companion_mood": "excited",
            "response_style": "energetic",
            "suggested_reaction": "That's amazing! Tell me more!",
        },
        "surprise": {
            "companion_mood": "curious",
            "response_style": "intrigued",
            "suggested_reaction": "Wow, that's unexpected!",
        },
        "disgust": {
            "companion_mood": "concerned",
            "response_style": "understanding",
            "suggested_reaction": "I understand how you feel about that.",
        },
        "hope": {
            "companion_mood": "optimistic",
            "response_style": "encouraging",
            "suggested_reaction": "There's always hope! Let's explore possibilities.",
        },
    }
    
    return emotional_responses.get(emotion.lower(), emotional_responses["neutral"])


# Fallback simple emotion analysis (no API key needed)
def _simple_emotion_analysis(text: str) -> List[EmotionResult]:
    """Simple rule-based emotion analysis"""
    text_lower = text.lower()
    
    # Emotion keywords
    joy_words = ["happy", "glad", "joy", "excited", "wonderful", "amazing", "love", "great"]
    sadness_words = ["sad", "unhappy", "depressed", "sorry", "miss", "lonely", "hurt"]
    anger_words = ["angry", "mad", "frustrated", "hate", "annoyed", "irritated"]
    fear_words = ["afraid", "scared", "worried", "nervous", "anxious", "terrified"]
    love_words = ["love", "adore", "care", "appreciate", "fond"]
    surprise_words = ["surprised", "shocked", "wow", "unexpected"]
    
    scores = {}
    for emotion in EMOTIONS:
        scores[emotion] = 0.1  # Base score
    
    # Check for emotion keywords
    for word in joy_words:
        if word in text_lower:
            scores["joy"] += 0.2
    
    for word in sadness_words:
        if word in text_lower:
            scores["sadness"] += 0.2
    
    for word in anger_words:
        if word in text_lower:
            scores["anger"] += 0.2
    
    for word in fear_words:
        if word in text_lower:
            scores["fear"] += 0.2
    
    for word in love_words:
        if word in text_lower:
            scores["love"] += 0.2
    
    for word in surprise_words:
        if word in text_lower:
            scores["surprise"] += 0.2
    
    # Check for question marks (curiosity/neutral)
    if "?" in text:
        scores["neutral"] += 0.1
    
    # Normalize scores
    total = sum(scores.values())
    if total > 0:
        for emotion in scores:
            scores[emotion] /= total
    
    results = [EmotionResult(label=k, score=v) for k, v in scores.items()]
    return sorted(results, key=lambda x: x.score, reverse=True)


def _simple_sentiment_analysis(text: str) -> List[SentimentResult]:
    """Simple rule-based sentiment analysis"""
    text_lower = text.lower()
    
    positive_words = [
        "good", "great", "amazing", "wonderful", "excellent", "happy", "love",
        "best", "beautiful", "fantastic", "awesome", "nice", "glad", "thank"
    ]
    negative_words = [
        "bad", "terrible", "awful", "horrible", "sad", "angry", "hate",
        "worst", "ugly", "disappointing", "boring", "annoying", "sorry"
    ]
    
    pos_score = 0.1
    neg_score = 0.1
    
    for word in positive_words:
        if word in text_lower:
            pos_score += 0.15
    
    for word in negative_words:
        if word in text_lower:
            neg_score += 0.15
    
    # Normalize
    total = pos_score + neg_score
    pos_score = pos_score / total
    neg_score = neg_score / total
    
    neutral_score = 1.0 - abs(pos_score - neg_score)
    
    results = [
        SentimentResult(label="positive", score=pos_score),
        SentimentResult(label="negative", score=neg_score),
        SentimentResult(label="neutral", score=neutral_score * 0.3),
    ]
    
    return sorted(results, key=lambda x: x.score, reverse=True)


def _get_mood_for_emotion(emotion: str) -> str:
    """Get suggested companion mood for user emotion"""
    mood_map = {
        "joy": "happy",
        "sadness": "supportive",
        "anger": "calm",
        "fear": "reassuring",
        "surprise": "curious",
        "neutral": "neutral",
        "disgust": "concerned",
        "love": "warm",
        "excitement": "excited",
        "hope": "optimistic",
    }
    return mood_map.get(emotion.lower(), "neutral")
