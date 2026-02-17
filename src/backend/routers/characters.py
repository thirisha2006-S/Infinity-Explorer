from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from database import CharacterDB

router = APIRouter()


class CharacterCreate(BaseModel):
    name: str
    char_class: str
    wisdom: int = 5
    courage: int = 5
    empathy: int = 5


class CharacterUpdate(BaseModel):
    wisdom: Optional[int] = None
    courage: Optional[int] = None
    empathy: Optional[int] = None
    experience: Optional[int] = None
    level: Optional[int] = None


@router.post("/")
async def create_character(data: CharacterCreate):
    """Create a new character."""
    result = CharacterDB.create(
        name=data.name,
        char_class=data.char_class,
        wisdom=data.wisdom,
        courage=data.courage,
        empathy=data.empathy,
    )
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "character": result}


@router.get("/")
async def get_all_characters():
    """Get all characters."""
    return {"characters": CharacterDB.get_all()}


@router.get("/{name}")
async def get_character(name: str):
    """Get a specific character."""
    char = CharacterDB.get(name)
    if char:
        char["worlds_visited_list"] = CharacterDB.get_worlds_visited(name)
        return {"success": True, "character": char}
    return {"success": False, "message": "Character not found"}


@router.put("/{name}")
async def update_character(name: str, data: CharacterUpdate):
    """Update a character."""
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    if update_data:
        result = CharacterDB.update(name, **update_data)
        if result:
            return {"success": True, "character": result}
    return {"success": False, "message": "Character not found"}


@router.delete("/{name}")
async def delete_character(name: str):
    """Delete a character."""
    if CharacterDB.delete(name):
        return {"success": True, "message": "Character deleted"}
    return {"success": False, "message": "Character not found"}


@router.post("/{name}/xp")
async def add_xp(name: str, amount: int = 25):
    """Add XP to a character."""
    result = CharacterDB.add_xp(name, amount)
    if "error" in result:
        return {"success": False, "message": result["error"]}
    return {"success": True, "character": result}


@router.post("/{name}/visit/{world_id}")
async def visit_world(name: str, world_id: str):
    """Mark a world as visited."""
    CharacterDB.visit_world(name, world_id)
    return {"success": True, "message": f"Visited {world_id}"}
