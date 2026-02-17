from fastapi import APIRouter

router = APIRouter()

# World data (in-memory for now)
WORLDS = [
    {
        "id": "space",
        "name": "Space World",
        "description": "Stars glow around you. Explore the cosmos and its mysteries.",
        "theme": "space",
        "icon": "🚀",
        "topics": ["planets", "stars", "galaxies", "black holes", "space exploration"],
        "color": "#1E3A5F",
    },
    {
        "id": "god",
        "name": "God World",
        "description": "A calm divine realm. Knowledge, balance, and peace surround you.",
        "theme": "divine",
        "icon": "✨",
        "topics": ["philosophy", "wisdom", "balance", "peace", "spirituality"],
        "color": "#4A3F6B",
    },
    {
        "id": "spirit",
        "name": "Spirit World",
        "description": "Soft whispers of lost souls. Emotions are strong here.",
        "theme": "spiritual",
        "icon": "👻",
        "topics": ["emotions", "memories", "spirits", "intuition", "feelings"],
        "color": "#2D4A3F",
    },
    {
        "id": "earth",
        "name": "Earth World",
        "description": "Explore our beautiful planet - nature, cultures, and history.",
        "theme": "nature",
        "icon": "🌍",
        "topics": ["nature", "cultures", "history", "geography", "science"],
        "color": "#2D5A3F",
    },
]


@router.get("/")
async def get_all_worlds():
    """Get all available worlds."""
    return {"worlds": WORLDS}


@router.get("/{world_id}")
async def get_world(world_id: str):
    """Get a specific world by ID."""
    world = next((w for w in WORLDS if w["id"] == world_id), None)
    if world:
        return {"world": world}
    return {"error": "World not found"}
