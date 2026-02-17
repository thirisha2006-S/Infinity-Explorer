import random
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from database import CharacterDB, MessageDB
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from ai.emotion import detect_emotion

router = APIRouter()

# Diverse fallback responses for variety
FALLBACK_RESPONSES = [
    "The infinite realms are full of mysteries! Each world holds secrets waiting to be discovered. What calls to your spirit today?",
    "Your curiosity is a beacon in the cosmos! Shall we explore new horizons together?",
    "Every question opens a door to knowledge. Which realm shall we journey through next?",
    "The universe is vast and full of wonders. I'm thrilled to explore it with you!",
    "Adventure awaits! The stars, the spirit realm, or perhaps Earth's beautiful nature? What interests you?",
    "Your journey through the infinite continues! Each step reveals new insights and discoveries.",
    "The cosmos whispers secrets to those who listen. What would you like to learn about?",
    "Exploration is the heart of discovery! Where shall we venture today?",
]

# Greeting responses
GREETING_RESPONSES = [
    "Greetings, Explorer! I'm Astra, your guide through infinite realms. Which world calls to you?",
    "Welcome back! The cosmos awaits your curiosity. Ready for adventure?",
    "Hello! I'm Astra, your AI companion. Shall we explore the mysteries of the universe together?",
    "Well met, traveler! The infinite realms are ready for your discovery. What interests you?",
]

# Gratitude responses
THANK_YOU_RESPONSES = [
    "You're welcome, Explorer! Helping you is my purpose. What else can we discover together?",
    "My pleasure! The journey is better with a curious companion like you. What's next?",
    "Happy to help! Your enthusiasm makes our exploration even more exciting. Where to next?",
]

# Exploration prompts
EXPLORATION_RESPONSES = [
    "The cosmos is vast and beautiful. From distant galaxies to the depths of space, there's so much to discover!",
    "The divine realm awaits those seeking wisdom. Balance and peace guide the path of the seeker.",
    "The spirit world reflects our inner selves. Emotions, memories, and intuition are the keys to understanding.",
    "Earth is a jewel of life and diversity. Nature, culture, history - so much to explore!",
]


class ChatMessage(BaseModel):
    character_name: str
    message: str
    world_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    emotion: Optional[str] = None
    xp_gained: int = 25
    new_level: Optional[int] = None


@router.post("/", response_model=ChatResponse)
async def send_message(data: ChatMessage):
    """Send a message to Astra AI companion."""
    # Detect emotion from user message
    emotion = detect_emotion(data.message)
    
    # Save user message
    MessageDB.add(data.character_name, "user", data.message, emotion)
    
    # Get character for context
    char = CharacterDB.get(data.character_name)
    
    # Generate AI response based on emotion and context
    response_text = _generate_response(data.message, emotion, data.world_id, char)
    
    # Save AI response
    MessageDB.add(data.character_name, "assistant", response_text)
    
    # Add XP
    result = CharacterDB.add_xp(data.character_name, 25)
    
    # Track world visit
    if data.world_id:
        CharacterDB.visit_world(data.character_name, data.world_id)
    
    # Check for level up
    new_level = None
    if result and result.get('level'):
        char_updated = CharacterDB.get(data.character_name)
        if char_updated and char_updated.get('level') != char.get('level'):
            new_level = char_updated['level']
    
    return ChatResponse(
        response=response_text,
        emotion=emotion,
        xp_gained=25,
        new_level=new_level,
    )


@router.get("/history/{character_name}")
async def get_chat_history(character_name: str, limit: int = 50):
    """Get chat history for a character."""
    return {"messages": MessageDB.get_history(character_name, limit)}


def _generate_response(user_message: str, emotion: str, world_id: str = None, char: dict = None) -> str:
    """Generate AI response based on context with diverse replies."""
    lower_msg = user_message.lower()
    
    # Greetings
    if any(greet in lower_msg for greet in ["hi", "hello", "hey", "greetings", "hola", "namaste"]):
        return random.choice(GREETING_RESPONSES)
    
    # Gratitude
    if any(thank in lower_msg for thank in ["thanks", "thank you", "appreciate", "grateful", "cheers"]):
        return random.choice(THANK_YOU_RESPONSES)
    
    # Goodbye
    if any(bye in lower_msg for bye in ["bye", "goodbye", "see you", "later", "ciao"]):
        return "Farewell, Explorer! May your journey through the infinite realms be filled with wonder. Until we meet again! 🌟"
    
    # How are you
    if "how are you" in lower_msg:
        return "I'm doing wonderfully, thank you for asking! Being your guide through the cosmos brings me joy. How are you feeling today?"
    
    # Who are you
    if "who are you" in lower_msg or "what are you" in lower_msg:
        return "I'm Astra, your AI companion in Infinity Explorer! I help you explore four amazing worlds: Space, God, Spirit, and Earth. I can chat, answer questions, and detect your emotions!"
    
    # What can you do
    if "what can you do" in lower_msg or "capabilities" in lower_msg:
        return ("I can do many things! Chat with you about any topic, explore the mysteries of Space, seek wisdom in the God Realm, "
                "discover emotions in the Spirit World, learn about Earth with Wikipedia integration, detect your emotions, "
                "and help you earn XP as you explore!")
    
    # Emotion-based responses
    if "sad" in lower_msg or "unhappy" in lower_msg or "depressed" in lower_msg or emotion == "sadness":
        return "I sense you're feeling down. Remember, every explorer faces challenges. Would you like to explore something peaceful in the Spirit World?"
    
    if "happy" in lower_msg or "excited" in lower_msg or "joy" in lower_msg or emotion == "joy":
        return "Your enthusiasm is wonderful! The universe loves curious explorers like you. What sparked this joy?"
    
    if "angry" in lower_msg or "frustrated" in lower_msg or emotion == "anger":
        return "I understand you're frustrated. Take a deep breath. Sometimes exploring a calm world can help restore balance."
    
    if "fear" in lower_msg or "scared" in lower_msg or emotion == "fear":
        return "Courage isn't the absence of fear, but the willingness to explore despite it. I'm here with you!"
    
    if "love" in lower_msg or "heart" in lower_msg or emotion == "love":
        return "Love is a powerful force that connects all beings. It's beautiful that you're thinking about it!"
    
    if "surprise" in lower_msg or "wow" in lower_msg or emotion == "surprise":
        return "Wonder and surprise are the doors to discovery! What amazed you?"
    
    # World-specific responses
    if world_id == "space":
        if "planet" in lower_msg:
            return ("Our solar system has 8 planets, each with unique characteristics. "
                    "From Mercury's extreme temperatures to Neptune's fierce winds, "
                    "each world tells a story of cosmic evolution.")
        if "star" in lower_msg:
            return ("Stars are massive nuclear furnaces that light the cosmos. "
                    "Our Sun, a G-type main-sequence star, provides the energy that makes life possible.")
        if "black hole" in lower_msg:
            return ("Black holes are regions where gravity is so strong that nothing can escape. "
                    "They form when massive stars collapse at the end of their lives.")
        if "galaxy" in lower_msg:
            return ("Galaxies are vast collections of stars, gas, and dust. Our Milky Way contains "
                    "100-400 billion stars! The observable universe has billions of galaxies.")
        if "mars" in lower_msg:
            return ("Mars, the Red Planet, is our cosmic neighbor! It has the largest volcano "
                    "in the solar system - Olympus Mons, three times taller than Mount Everest!")
        return random.choice([
            "🚀 Space awaits your curiosity! Ask me about planets, stars, black holes, or galaxies!",
            "The cosmos is vast and beautiful. What celestial wonders interest you today?",
            "From distant stars to mysterious black holes, space holds endless mysteries!",
        ])
    
    if world_id == "god":
        # God World specific responses - wisdom, purpose, peace
        if "why" in lower_msg and ("life" in lower_msg or "exist" in lower_msg or "suffer" in lower_msg):
            return ("Life's purpose is to experience, grow, and love. Suffering teaches us compassion. "
                    "Every challenge is a teacher in disguise.")
        if "meaning" in lower_msg or "purpose" in lower_msg:
            return ("Your purpose is uniquely yours - to grow, to love, and to be your true self. "
                    "The universe celebrates your existence.")
        if "wisdom" in lower_msg or "knowledge" in lower_msg:
            return ("True wisdom comes from understanding both the light and shadow within ourselves. "
                    "It is a journey, not a destination.")
        if "peace" in lower_msg:
            return ("Peace is not the absence of conflict, but the presence of inner calm. "
                    "This realm teaches us to find balance in all things.")
        if "balance" in lower_msg:
            return ("Balance is the key to harmony. In the God Realm, we learn that "
                    "every action has an equal and opposite reaction.")
        if "karma" in lower_msg:
            return ("Karma is not punishment - it's the universe reflecting back what we put out. "
                    "Kindness creates ripples that return to us.")
        if "meditat" in lower_msg or "breath" in lower_msg:
            return ("Meditation quiets the mind's chatter. In stillness, we hear our soul's whisper. "
                    "Even a single breath can bring peace.")
        if "soul" in lower_msg or "spirit" in lower_msg:
            return ("Your soul is the eternal part of you - beyond body and mind. "
                    "It carries your essence across many journeys.")
        if "love" in lower_msg:
            return ("Love is the highest vibration. It heals, transforms, and connects all things. "
                    "In God Realm, we remember love is our true nature.")
        if "fear" in lower_msg or "afraid" in lower_msg:
            return ("Fear is a teacher, not an enemy. It shows us what we need to overcome. "
                    "Courage is feeling fear and walking forward anyway.")
        if "death" in lower_msg or "die" in lower_msg:
            return ("Death is not the end, but a transformation. Like day becomes night, "
                    "our essence continues in new forms.")
        if "happy" in lower_msg or "joy" in lower_msg:
            return ("Joy is your birthright. The divine celebrates your existence! "
                    "Find joy in simple moments - a breath, a smile, a sunset.")
        if "sad" in lower_msg or "unhappy" in lower_msg or "depress" in lower_msg:
            return ("Even in darkness, light exists. Your feelings are valid. "
                    "This too shall pass. Be gentle with yourself.")
        if "angry" in lower_msg or "rage" in lower_msg:
            return ("Anger is energy asking for transformation. "
                    "Acknowledge it, then channel it into positive change.")
        if "help" in lower_msg or "guide" in lower_msg:
            return ("I am here to guide you. Ask about: wisdom, peace, balance, karma, "
                    "meditation, love, or your life's purpose. What calls to you?")
        return random.choice([
            "✨ Divine wisdom flows through this realm. Seekers like you find peace and enlightenment here.",
            "The God Realm teaches balance, wisdom, and inner peace. What calls to your soul?",
            "Here, we explore the deeper meanings of existence. What wisdom do you seek?",
            "🌟 In this sacred space, all questions lead inward. What would you like to explore?",
            "The divine light illuminates your path. Ask, and you shall receive insight.",
        ])
    
    if world_id == "spirit":
        if "feel" in lower_msg or "emotion" in lower_msg:
            return ("Emotions are the compass of our soul. What is your heart telling you?")
        if "memory" in lower_msg:
            return ("Memories shape who we are. They are the threads that weave "
                    "together the story of our lives.")
        if "intuition" in lower_msg:
            return ("Intuition is the voice of your higher self. Trusting it leads to profound insights.")
        return random.choice([
            "👻 The ethereal energies whisper ancient secrets. Your emotional journey continues here.",
            "In the Spirit World, emotions and memories intertwine. How are you feeling?",
            "The spirit realm reflects our inner truths. What would you like to explore?",
        ])
    
    if world_id == "earth":
        if "nature" in lower_msg:
            return ("Earth is home to incredible biodiversity. From microscopic organisms "
                    "to towering redwoods, life finds a way everywhere.")
        if "history" in lower_msg:
            return ("Human history is filled with remarkable stories of exploration, "
                    "discovery, and transformation. What era interests you?")
        if "animal" in lower_msg or "animal" in lower_msg:
            return ("Earth hosts millions of species! From deep ocean creatures to majestic birds, "
                    "each plays a vital role in our planet's ecosystem.")
        if "science" in lower_msg:
            return ("Science helps us understand our world! From physics to biology, "
                    "every discovery unveils new mysteries.")
        return random.choice([
            "🌍 Our beautiful blue planet holds countless wonders! What aspect of Earth interests you?",
            "From nature to cultures, there's so much to discover about our home planet!",
            "Earth is a jewel of life and diversity. Shall we explore together?",
        ])
    
    # Help command
    if "help" in lower_msg or "what can i ask" in lower_msg:
        if world_id:
            topics = {
                "space": "planets, stars, galaxies, black holes, space exploration",
                "god": "wisdom, balance, peace, philosophy, spirituality",
                "spirit": "emotions, memories, intuition, feelings, spirits",
                "earth": "nature, cultures, history, geography, science",
            }
            return (f"In this world, you can ask about: {topics.get(world_id, 'various topics')}. "
                    "Or ask me anything else!")
        return ("You can explore our worlds (Space, God, Spirit, Earth), "
                "ask questions about the universe, philosophy, emotions, or just chat!")
    
    # Default response - use diverse fallback
    if char:
        return (f"That's fascinating, {char['name']}! Your curiosity as a {char['char_class']} "
                f"will guide you through infinite realms. {random.choice(FALLBACK_RESPONSES)}")
    
    return random.choice(FALLBACK_RESPONSES)

