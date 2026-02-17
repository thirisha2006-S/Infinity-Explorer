from fastapi import APIRouter
from datetime import datetime
from typing import Dict, List

router = APIRouter()

# Simple in-memory analytics (use database in production)
analytics_data = {
    "total_users": 0,
    "total_messages": 0,
    "total_xp_earned": 0,
    "world_visits": {
        "god": 0,
        "space": 0,
        "spirit": 0,
        "earth": 0
    },
    "topic_mentions": {},
    "recent_activity": []
}

def track_event(event_type: str, data: Dict = None):
    """Track an analytics event."""
    global analytics_data
    
    if event_type == "user_created":
        analytics_data["total_users"] += 1
    elif event_type == "message_sent":
        analytics_data["total_messages"] += 1
    elif event_type == "xp_earned":
        xp = data.get("xp", 0) if data else 0
        analytics_data["total_xp_earned"] += xp
    elif event_type == "world_visit":
        world = data.get("world", "unknown") if data else "unknown"
        if world in analytics_data["world_visits"]:
            analytics_data["world_visits"][world] += 1
    elif event_type == "topic_asked":
        topic = data.get("topic", "unknown") if data else "unknown"
        analytics_data["topic_mentions"][topic] = analytics_data["topic_mentions"].get(topic, 0) + 1
    
    # Add to recent activity
    analytics_data["recent_activity"].append({
        "type": event_type,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last 100 events
    if len(analytics_data["recent_activity"]) > 100:
        analytics_data["recent_activity"] = analytics_data["recent_activity"][-100:]


@router.get("/stats")
async def get_stats():
    """Get analytics statistics."""
    return {
        "total_users": analytics_data["total_users"],
        "total_messages": analytics_data["total_messages"],
        "total_xp_earned": analytics_data["total_xp_earned"],
        "world_visits": analytics_data["world_visits"],
        "top_topics": sorted(
            analytics_data["topic_mentions"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
    }


@router.get("/activity")
async def get_recent_activity(limit: int = 20):
    """Get recent activity."""
    return {
        "activity": analytics_data["recent_activity"][-limit:]
    }
