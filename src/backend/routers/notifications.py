from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

router = APIRouter()

# Notification types
NOTIFICATION_TYPES = {
    "achievement_unlocked": {"icon": "🏆", "color": "gold", "priority": "high"},
    "level_up": {"icon": "⬆️", "color": "purple", "priority": "high"},
    "quest_completed": {"icon": "✅", "color": "green", "priority": "medium"},
    "quest_available": {"icon": "📋", "color": "blue", "priority": "medium"},
    "world_discovered": {"icon": "🌍", "color": "teal", "priority": "low"},
    "daily_reward": {"icon": "🎁", "color": "orange", "priority": "medium"},
    "tip": {"icon": "💡", "color": "gray", "priority": "low"},
    "reminder": {"icon": "⏰", "color": "yellow", "priority": "medium"},
}

# In-memory notification storage
notifications_db = {}


class Notification(BaseModel):
    id: str
    character_name: str
    type: str
    title: str
    message: str
    icon: str = "🔔"
    color: str = "purple"
    priority: str = "medium"
    is_read: bool = False
    created_at: str = ""
    data: Optional[dict] = None


class NotificationCreate(BaseModel):
    character_name: str
    type: str
    title: str
    message: str
    data: Optional[dict] = None


def create_notification(
    character_name: str,
    type: str,
    title: str,
    message: str,
    data: dict = None,
) -> Notification:
    """Create a notification with type-based icon and color."""
    type_info = NOTIFICATION_TYPES.get(type, {
        "icon": "🔔",
        "color": "purple",
        "priority": "medium",
    })
    
    notification = Notification(
        id=str(uuid.uuid4()),
        character_name=character_name,
        type=type,
        title=title,
        message=message,
        icon=type_info["icon"],
        color=type_info["color"],
        priority=type_info["priority"],
        created_at=datetime.now().isoformat(),
        data=data,
    )
    
    if character_name not in notifications_db:
        notifications_db[character_name] = []
    
    notifications_db[character_name].insert(0, notification)
    
    # Keep only last 50 notifications per character
    if len(notifications_db[character_name]) > 50:
        notifications_db[character_name] = notifications_db[character_name][:50]
    
    return notification


@router.get("/{character_name}")
async def get_notifications(
    character_name: str,
    unread_only: bool = False,
    limit: int = 20,
):
    """Get notifications for a character."""
    character_notifications = notifications_db.get(character_name, [])
    
    if unread_only:
        character_notifications = [n for n in character_notifications if not n.is_read]
    
    return {
        "notifications": character_notifications[:limit],
        "unread_count": len([n for n in character_notifications if not n.is_read]),
    }


@router.post("/")
async def create_notification_endpoint(data: NotificationCreate):
    """Create a new notification."""
    return create_notification(
        character_name=data.character_name,
        type=data.type,
        title=data.title,
        message=data.message,
        data=data.data,
    )


@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: str, character_name: str):
    """Mark a notification as read."""
    character_notifications = notifications_db.get(character_name, [])
    
    for notification in character_notifications:
        if notification.id == notification_id:
            notification.is_read = True
            return {"success": True}
    
    raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/{character_name}/mark_all_read")
async def mark_all_read(character_name: str):
    """Mark all notifications as read."""
    character_notifications = notifications_db.get(character_name, [])
    
    for notification in character_notifications:
        notification.is_read = True
    
    return {"success": True}


@router.delete("/{character_name}")
async def clear_notifications(character_name: str, unread_only: bool = False):
    """Clear notifications."""
    if unread_only:
        notifications_db[character_name] = [
            n for n in notifications_db.get(character_name, []) if not n.is_read
        ]
    else:
        notifications_db[character_name] = []
    
    return {"success": True}


# Pre-defined notification templates
def send_achievement_notification(character_name: str, achievement_name: str, xp_reward: int):
    return create_notification(
        character_name=character_name,
        type="achievement_unlocked",
        title="Achievement Unlocked!",
        message=f"You unlocked '{achievement_name}'! +{xp_reward} XP",
        data={"achievement": achievement_name, "xp": xp_reward},
    )


def send_level_up_notification(character_name: str, new_level: int):
    return create_notification(
        character_name=character_name,
        type="level_up",
        title="Level Up! 🎉",
        message=f"Congratulations! You've reached Level {new_level}!",
        data={"level": new_level},
    )


def send_quest_notification(character_name: str, quest_name: str):
    return create_notification(
        character_name=character_name,
        type="quest_available",
        title="New Quest Available!",
        message=f"Check out the new quest: {quest_name}",
        data={"quest": quest_name},
    )


def send_world_discovered_notification(character_name: str, world_name: str):
    return create_notification(
        character_name=character_name,
        type="world_discovered",
        title="New World Discovered!",
        message=f"You've discovered {world_name}!",
        data={"world": world_name},
    )


# Welcome notification
def send_welcome_notification(character_name: str):
    return create_notification(
        character_name=character_name,
        type="tip",
        title="Welcome to Infinity Explorer! 🌟",
        message="Start by creating a character and exploring the worlds. "
                "Chat with Astra to earn XP and unlock achievements!",
        data={"tutorial": True},
    )
