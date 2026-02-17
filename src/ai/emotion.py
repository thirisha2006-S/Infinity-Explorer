from textblob import TextBlob

def detect_emotion(text):
    """
    Detect emotion from text using TextBlob sentiment analysis.
    Returns one of: joy, sadness, anger, fear, surprise, neutral, disgust, love, excitement, hope
    """
    if not text or not text.strip():
        return "neutral"
    
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity  # -1 to 1
    subjectivity = analysis.sentiment.subjectivity  # 0 to 1
    
    text_lower = text.lower()
    
    # Enhanced emotion detection with keyword matching
    joy_keywords = ["happy", "glad", "joy", "excited", "wonderful", "amazing", "love", "great", "awesome", "fantastic", "excellent"]
    sadness_keywords = ["sad", "unhappy", "depressed", "sorry", "miss", "lonely", "hurt", "down", "blue", "melancholy"]
    anger_keywords = ["angry", "mad", "frustrated", "hate", "annoyed", "irritated", "furious", "livid", "enraged"]
    fear_keywords = ["afraid", "scared", "worried", "nervous", "anxious", "terrified", "panic", "horror", "dread"]
    love_keywords = ["love", "adore", "care", "appreciate", "fond", "cherish", "heart", "dear", "beautiful"]
    surprise_keywords = ["surprised", "shocked", "wow", "unexpected", "amazing", "incredible", "unbelievable"]
    excitement_keywords = ["excited", "thrilled", "eager", "pumped", "stoked", "can't wait", "anticipating"]
    hope_keywords = ["hope", "wish", "dream", "aspire", "optimistic", "positive", "faith", "belief"]
    
    # Check for keyword matches
    keyword_scores = {
        "joy": 0, "sadness": 0, "anger": 0, "fear": 0,
        "love": 0, "surprise": 0, "excitement": 0, "hope": 0
    }
    
    for word in joy_keywords:
        if word in text_lower:
            keyword_scores["joy"] += 1
    
    for word in sadness_keywords:
        if word in text_lower:
            keyword_scores["sadness"] += 1
    
    for word in anger_keywords:
        if word in text_lower:
            keyword_scores["anger"] += 1
    
    for word in fear_keywords:
        if word in text_lower:
            keyword_scores["fear"] += 1
    
    for word in love_keywords:
        if word in text_lower:
            keyword_scores["love"] += 1
    
    for word in surprise_keywords:
        if word in text_lower:
            keyword_scores["surprise"] += 1
    
    for word in excitement_keywords:
        if word in text_lower:
            keyword_scores["excitement"] += 1
    
    for word in hope_keywords:
        if word in text_lower:
            keyword_scores["hope"] += 1
    
    # Get the highest keyword match
    max_keyword_score = max(keyword_scores.values())
    if max_keyword_score > 0:
        dominant_emotion = max(keyword_scores, key=keyword_scores.get)
        return dominant_emotion
    
    # Fall back to polarity-based detection
    if polarity > 0.5:
        return "joy"
    elif polarity > 0.2:
        return "excitement"
    elif polarity > 0:
        return "hope"
    elif polarity < -0.5:
        return "sadness"
    elif polarity < -0.2:
        return "anger"
    elif polarity < 0:
        return "fear"
    else:
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
