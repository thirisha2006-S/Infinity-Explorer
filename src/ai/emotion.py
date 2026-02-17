from textblob import TextBlob
import re

def detect_emotion(text):
    """
    Detect emotion from text using enhanced keyword matching + TextBlob sentiment.
    Returns one of: joy, sadness, anger, fear, surprise, neutral, disgust, love, excitement, hope, gratitude, compassion
    """
    if not text or not text.strip():
        return "neutral"
    
    text_lower = text.lower()
    
    # Enhanced emotion detection with more comprehensive keyword matching
    emotion_keywords = {
        "joy": ["happy", "glad", "joy", "excited", "wonderful", "amazing", "great", "awesome", 
                "fantastic", "excellent", "brilliant", "delighted", "thrilled", "elated", "blessed",
                "grateful", "thankful", "grateful", "appreciative", "cheerful", "content", "fulfilled"],
        "sadness": ["sad", "unhappy", "depressed", "sorry", "miss", "lonely", "hurt", "down", "blue", 
                    "melancholy", "grief", "sorrow", "heartbroken", "devastated", "miserable", "hopeless",
                    "disappointed", "discouraged", "empty", "lost"],
        "anger": ["angry", "mad", "frustrated", "hate", "annoyed", "irritated", "furious", "livid", 
                  "enraged", "outraged", "infuriated", "bitter", "resentful", "hostile", "aggravated"],
        "fear": ["afraid", "scared", "worried", "nervous", "anxious", "terrified", "panic", "horror", 
                "dread", "frightened", "alarmed", "concerned", "uneasy", "apprehensive", "threatened"],
        "love": ["love", "adore", "care", "appreciate", "fond", "cherish", "heart", "dear", "beautiful",
                 "passion", "affection", "devoted", "romantic", "attached", "connected", "compassion"],
        "surprise": ["surprised", "shocked", "wow", "unexpected", "incredible", "unbelievable", "astonished",
                     "amazed", "stunned", "speechless", "wow", "whoa"],
        "excitement": ["excited", "thrilled", "eager", "pumped", "stoked", "can't wait", "anticipating",
                      "enthusiastic", "fired up", "psyched", "amped", "hyper"],
        "hope": ["hope", "wish", "dream", "aspire", "optimistic", "positive", "faith", "belief",
                "confident", "encouraged", "uplifted", "inspired", "motivated", "looking forward"],
        "gratitude": ["thank", "grateful", "blessed", "fortunate", "appreciate", "thanks", "mindful"],
        "compassion": ["kind", "gentle", "understanding", "supportive", "helping", "caring", "sympathetic"]
    }
    
    # Calculate keyword scores
    keyword_scores = {emotion: 0 for emotion in emotion_keywords}
    
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                keyword_scores[emotion] += 1
    
    # Check for negation patterns (e.g., "not happy")
    negation_patterns = [r"not\s+\w+", r"don't\s+\w+", r"isn't\s+\w+", r"aren't\s+\w+", r"won't\s+\w+"]
    has_negation = any(re.search(pattern, text_lower) for pattern in negation_patterns)
    
    # Get the highest keyword match
    max_keyword_score = max(keyword_scores.values())
    
    # If strong keyword match and no negation
    if max_keyword_score > 0 and not has_negation:
        dominant_emotion = max(keyword_scores, key=keyword_scores.get)
        return dominant_emotion
    
    # Fall back to TextBlob polarity-based detection
    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity  # -1 to 1
        subjectivity = analysis.sentiment.subjectivity  # 0 to 1
        
        if polarity > 0.6:
            return "joy"
        elif polarity > 0.3:
            return "excitement"
        elif polarity > 0:
            return "hope"
        elif polarity < -0.6:
            return "sadness"
        elif polarity < -0.3:
            return "anger"
        elif polarity < 0:
            return "fear"
    except:
        pass
    
    return "neutral"


def get_emotion_emoji(emotion):
    """Get emoji for emotion"""
    emotion_emojis = {
        "joy": "😊",
        "sadness": "😢",
        "anger": "😠",
        "fear": "😨",
        "surprise": "😮",
        "neutral": "😐",
        "disgust": "🤢",
        "love": "❤️",
        "excitement": "🤩",
        "hope": "✨"
    }
    return emotion_emojis.get(emotion, "😐")
