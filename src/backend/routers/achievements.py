from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# Achievement definitions
ACHIEVEMENTS = [
    # Exploration achievements
    {
        "id": "first_steps",
        "name": "First Steps",
        "description": "Complete your first exploration",
        "icon": "👣",
        "xp_reward": 50,
        "category": "exploration",
        "requirement": {"type": "chats", "count": 1},
    },
    {
        "id": "world_explorer",
        "name": "World Explorer",
        "description": "Visit all 4 worlds",
        "icon": "🌍",
        "xp_reward": 200,
        "category": "exploration",
        "requirement": {"type": "worlds_visited", "count": 4},
    },
    {
        "id": "space_navigator",
        "name": "Space Navigator",
        "description": "Explore Space World 10 times",
        "icon": "🚀",
        "xp_reward": 150,
        "category": "exploration",
        "requirement": {"type": "world_specific", "world": "space", "count": 10},
    },
    {
        "id": "divine_seeker",
        "name": "Divine Seeker",
        "description": "Explore God World 10 times",
        "icon": "✨",
        "xp_reward": 150,
        "category": "exploration",
        "requirement": {"type": "world_specific", "world": "god", "count": 10},
    },
    {
        "id": "spirit_whisperer",
        "name": "Spirit Whisperer",
        "description": "Explore Spirit World 10 times",
        "icon": "👻",
        "xp_reward": 150,
        "category": "exploration",
        "requirement": {"type": "world_specific", "world": "spirit", "count": 10},
    },
    {
        "id": "earth_adventurer",
        "name": "Earth Adventurer",
        "description": "Explore Earth World 10 times",
        "icon": "🌿",
        "xp_reward": 150,
        "category": "exploration",
        "requirement": {"type": "world_specific", "world": "earth", "count": 10},
    },
    
    # Level achievements
    {
        "id": "rising_star",
        "name": "Rising Star",
        "description": "Reach Level 5",
        "icon": "⭐",
        "xp_reward": 100,
        "category": "level",
        "requirement": {"type": "level", "count": 5},
    },
    {
        "id": "expert_explorer",
        "name": "Expert Explorer",
        "description": "Reach Level 10",
        "icon": "🏆",
        "xp_reward": 250,
        "category": "level",
        "requirement": {"type": "level", "count": 10},
    },
    {
        "id": "master_adventurer",
        "name": "Master Adventurer",
        "description": "Reach Level 25",
        "icon": "👑",
        "xp_reward": 500,
        "category": "level",
        "requirement": {"type": "level", "count": 25},
    },
    
    # Social achievements
    {
        "id": "friendly_explorer",
        "name": "Friendly Explorer",
        "description": "Have 10 conversations",
        "icon": "💬",
        "xp_reward": 75,
        "category": "social",
        "requirement": {"type": "chats", "count": 10},
    },
    {
        "id": "great_conversationalist",
        "name": "Great Conversationalist",
        "description": "Have 50 conversations",
        "icon": "🎭",
        "xp_reward": 200,
        "category": "social",
        "requirement": {"type": "chats", "count": 50},
    },
    
    # Knowledge achievements
    {
        "id": "curious_mind",
        "name": "Curious Mind",
        "description": "Ask 20 questions",
        "icon": "❓",
        "xp_reward": 100,
        "category": "knowledge",
        "requirement": {"type": "questions", "count": 20},
    },
    {
        "id": "wisdom_seeker",
        "name": "Wisdom Seeker",
        "description": "Complete 5 wisdom-related quests",
        "icon": "📚",
        "xp_reward": 150,
        "category": "knowledge",
        "requirement": {"type": "wisdom_quests", "count": 5},
    },
]

# Quest definitions
QUESTS = [
    {
        "id": "welcome_quest",
        "name": "Welcome to Infinity",
        "description": "Have your first conversation with Astra",
        "icon": "👋",
        "xp_reward": 25,
        "world": None,
        "steps": [
            {"type": "chat", "description": "Say hello to Astra"},
        ],
    },
    {
        "id": "space_intro",
        "name": "Journey to Space",
        "description": "Explore the cosmos and learn about planets",
        "icon": "🪐",
        "xp_reward": 50,
        "world": "space",
        "steps": [
            {"type": "visit_world", "world_id": "space", "description": "Visit Space World"},
            {"type": "chat_topic", "topic": "planet", "description": "Ask about planets"},
            {"type": "chat_topic", "topic": "star", "description": "Ask about stars"},
        ],
    },
    {
        "id": "god_wisdom",
        "name": "Seeking Wisdom",
        "description": "Discover the path to knowledge",
        "icon": "📖",
        "xp_reward": 50,
        "world": "god",
        "steps": [
            {"type": "visit_world", "world_id": "god", "description": "Visit God World"},
            {"type": "chat_topic", "topic": "wisdom", "description": "Ask about wisdom"},
            {"type": "chat_topic", "topic": "balance", "description": "Ask about balance"},
        ],
    },
    {
        "id": "spirit_journey",
        "name": "Into the Spirit",
        "description": "Connect with your inner self",
        "icon": "🔮",
        "xp_reward": 50,
        "world": "spirit",
        "steps": [
            {"type": "visit_world", "world_id": "spirit", "description": "Visit Spirit World"},
            {"type": "chat_topic", "topic": "emotion", "description": "Share your feelings"},
            {"type": "chat_topic", "topic": "intuition", "description": "Ask about intuition"},
        ],
    },
    {
        "id": "earth_exploration",
        "name": "Earth Explorer",
        "description": "Discover amazing places on Earth",
        "icon": "🗺️",
        "xp_reward": 50,
        "world": "earth",
        "steps": [
            {"type": "visit_world", "world_id": "earth", "description": "Visit Earth World"},
            {"type": "search_place", "description": "Search for a famous place"},
            {"type": "explore_place", "description": "Explore a place in detail"},
        ],
    },
    {
        "id": "level_5_quest",
        "name": "Rising Higher",
        "description": "Reach Level 5",
        "icon": "📈",
        "xp_reward": 100,
        "world": None,
        "steps": [
            {"type": "level", "required": 5, "description": "Reach Level 5"},
        ],
    },
]


class QuestProgress(BaseModel):
    quest_id: str
    character_name: str
    current_step: int = 0
    completed_steps: List[int] = []
    is_completed: bool = False
    started_at: str = ""
    completed_at: str = ""


class AchievementProgress(BaseModel):
    achievement_id: str
    character_name: str
    current_progress: int = 0
    is_unlocked: bool = False
    unlocked_at: str = ""


# In-memory progress storage (replace with database in production)
quest_progress = {}
achievement_progress = {}


@router.get("/achievements")
async def get_all_achievements():
    """Get all available achievements."""
    return {"achievements": ACHIEVEMENTS}


@router.get("/quests")
async def get_all_quests():
    """Get all available quests."""
    return {"quests": QUESTS}


@router.get("/progress/{character_name}")
async def get_character_progress(character_name: str):
    """Get a character's achievement and quest progress."""
    char_quests = {k: v for k, v in quest_progress.items() if v.character_name == character_name}
    char_achievements = {k: v for k, v in achievement_progress.items() if v.character_name == character_name}
    
    return {
        "quests": list(char_quests.values()),
        "achievements": list(char_achievements.values()),
    }


@router.post("/quest/{quest_id}/start")
async def start_quest(quest_id: str, character_name: str):
    """Start a quest."""
    quest = next((q for q in QUESTS if q["id"] == quest_id), None)
    if not quest:
        return {"error": "Quest not found"}
    
    key = f"{character_name}_{quest_id}"
    if key in quest_progress:
        return {"error": "Quest already started"}
    
    quest_progress[key] = QuestProgress(
        quest_id=quest_id,
        character_name=character_name,
        started_at=datetime.now().isoformat(),
    )
    
    return {"success": True, "quest": quest}


@router.post("/quest/{quest_id}/complete_step")
async def complete_quest_step(quest_id: str, character_name: str, step: int):
    """Complete a step in a quest."""
    key = f"{character_name}_{quest_id}"
    if key not in quest_progress:
        return {"error": "Quest not started"}
    
    progress = quest_progress[key]
    if progress.is_completed:
        return {"error": "Quest already completed"}
    
    if step not in progress.completed_steps:
        progress.completed_steps.append(step)
    
    quest = next((q for q in QUESTS if q["id"] == quest_id), None)
    if len(progress.completed_steps) >= len(quest["steps"]):
        progress.is_completed = True
        progress.completed_at = datetime.now().isoformat()
    
    return {"success": True, "progress": progress}


@router.post("/character/{character_name}/check_achievements")
async def check_achievements(character_name: str, stats: dict):
    """Check and unlock achievements based on character stats."""
    unlocked = []
    
    for achievement in ACHIEVEMENTS:
        key = f"{character_name}_{achievement['id']}"
        req = achievement["requirement"]
        
        if key in achievement_progress and achievement_progress[key].is_unlocked:
            continue
        
        should_unlock = False
        
        if req["type"] == "chats" and stats.get("total_chats", 0) >= req["count"]:
            should_unlock = True
        elif req["type"] == "worlds_visited" and stats.get("worlds_visited", 0) >= req["count"]:
            should_unlock = True
        elif req["type"] == "world_specific":
            count = stats.get("world_visits", {}).get(req["world"], 0)
            if count >= req["count"]:
                should_unlock = True
        elif req["type"] == "level" and stats.get("level", 0) >= req["count"]:
            should_unlock = True
        elif req["type"] == "questions" and stats.get("questions_asked", 0) >= req["count"]:
            should_unlock = True
        elif req["type"] == "wisdom_quests" and stats.get("wisdom_quests_completed", 0) >= req["count"]:
            should_unlock = True
        
        if should_unlock:
            achievement_progress[key] = AchievementProgress(
                achievement_id=achievement["id"],
                character_name=character_name,
                is_unlocked=True,
                unlocked_at=datetime.now().isoformat(),
            )
            unlocked.append(achievement)
    
    return {"unlocked": unlocked}


@router.get("/leaderboard")
async def get_leaderboard():
    """Get XP leaderboard (placeholder)."""
    return {
        "message": "Leaderboard coming soon!",
        "top_explorers": [
            {"name": "Explorer1", "level": 10, "xp": 2500},
            {"name": "Adventurer2", "level": 8, "xp": 1800},
            {"name": "Traveler3", "level": 5, "xp": 1000},
        ],
    }
