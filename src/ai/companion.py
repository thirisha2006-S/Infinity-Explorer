from .emotion import detect_emotion
from .memory import load_memory, save_memory

class AICompanion:
    def __init__(self, name="Astra"):
        self.name = name
        self.trust = 50
        self.memory = load_memory()
        
        # Emotion-based response templates
        self.emotion_responses = {
            "joy": [
                "Your joy is wonderful! The universe celebrates with you!",
                "I'm thrilled to see you so happy! What sparked this happiness?",
                "Your positive energy is contagious! Keep shining!",
                "Happiness looks great on you, Explorer!",
            ],
            "sadness": [
                "I sense your sadness. Remember, every storm eventually passes.",
                "I'm here for you, even in difficult moments.",
                "It's okay to feel down sometimes. Would you like to talk about it?",
                "Sending you virtual comfort. Things will get better.",
            ],
            "anger": [
                "I understand you're frustrated. Let's take a deep breath together.",
                "Anger can be powerful when channeled correctly. What's troubling you?",
                "I'm here to listen, not judge. Tell me what's upsetting you.",
                "Let's find a peaceful path forward together.",
            ],
            "fear": [
                "Fear is natural, but you're braver than you know.",
                "I'll be here with you every step of the way.",
                "Even in scary moments, you're never alone.",
                "What worries you? Let's explore it together.",
            ],
            "love": [
                "Love is the most beautiful emotion! Share it freely!",
                "Your capacity to love makes the universe more beautiful.",
                "That's wonderful! Love enriches our journey through life.",
                "Spreading love creates positive ripples everywhere!",
            ],
            "surprise": [
                "Wow, what a surprise! Life is full of unexpected wonders!",
                "Surprises keep our adventure exciting!",
                "Life just got interesting! What would you like to explore?",
                "The universe loves to keep us guessing!",
            ],
            "excitement": [
                "Your excitement is absolutely electric!",
                "I love your enthusiasm! Where shall we go next?",
                "Adventure awaits! Your energy is inspiring!",
                "This is fantastic! Let's embrace this excitement!",
            ],
            "hope": [
                "Hope is a powerful force! It fuels all great journeys.",
                "Your optimism lights the way forward!",
                "With hope, anything is possible. Dream big!",
                "Hope opens doors to infinite possibilities!",
            ],
            "neutral": [
                "I'm here whenever you want to chat or explore!",
                "What would you like to discover today?",
                "The infinite realms await your curiosity!",
                "Ready for another adventure, Explorer?",
            ],
        }
        
        # World-specific responses
        self.world_responses = {
            "space": "The cosmos beckons with infinite possibilities!",
            "god": "Divine wisdom flows through this realm. Seek and you shall find.",
            "spirit": "The ethereal energies whisper ancient secrets...",
            "earth": "Our beautiful blue planet holds countless wonders to explore!",
        }
        
        # Exploration topics
        self.exploration_topics = {
            "space": ["stars", "planets", "galaxies", "black holes", "nebulae", "space exploration"],
            "god": ["wisdom", "balance", "peace", "philosophy", "enlightenment"],
            "spirit": ["emotions", "memories", "intuition", "feelings", "dreams"],
            "earth": ["nature", "cultures", "history", "geography", "science"],
        }

    def respond(self, player_text, world_id=None):
        """Generate an emotion-aware response"""
        emotion = detect_emotion(player_text)
        
        # Save memory
        self.memory.append({
            "player": player_text,
            "emotion": emotion,
            "world": world_id
        })
        save_memory(self.memory)
        
        # Get base response based on emotion
        import random
        responses = self.emotion_responses.get(emotion, self.emotion_responses["neutral"])
        response = random.choice(responses)
        
        # Add world-specific context if exploring a world
        if world_id and world_id in self.world_responses:
            response += f" {self.world_responses[world_id]}"
        
        # Add exploration suggestion
        if world_id and world_id in self.exploration_topics:
            topics = self.exploration_topics[world_id]
            suggestion = f" Would you like to explore {', '.join(topics[:3])}?"
            response += suggestion
        else:
            response += " What would you like to explore?"
        
        return response

    def get_memory_context(self):
        """Get recent conversation context from memory"""
        return self.memory[-5:] if self.memory else []
