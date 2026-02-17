from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os
import sqlite3

router = APIRouter()

# Get the directory where this file is located
ROUTER_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(ROUTER_DIR, '..', 'data', 'infinity_explorer.db')

# Daily reward configurations
DAILY_REWARDS = [
    {"day": 1, "xp": 25, "bonus": "Starter Pack", "icon": "🎁"},
    {"day": 2, "xp": 50, "bonus": "Double XP", "icon": "✨"},
    {"day": 3, "xp": 75, "bonus": "Mystery Box", "icon": "🎲"},
    {"day": 4, "xp": 100, "bonus": "Gold Boost", "icon": "🪙"},
    {"day": 5, "xp": 150, "bonus": "Mega Chest", "icon": "💎"},
    {"day": 6, "xp": 200, "bonus": "Super Star", "icon": "⭐"},
    {"day": 7, "xp": 500, "bonus": "Ultimate Prize", "icon": "👑"},
]

# In-memory storage (use database in production)
daily_login_data = {}


class DailyLoginData(BaseModel):
    character_name: str
    last_login_date: str = ""
    consecutive_days: int = 0
    total_rewards_claimed: int = 0
    current_streak: int = 0


class RewardClaim(BaseModel):
    character_name: str
    day: int


def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_daily_rewards_table():
    """Initialize daily rewards table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_rewards (
            character_name TEXT PRIMARY KEY,
            last_login_date TEXT,
            consecutive_days INTEGER DEFAULT 0,
            total_rewards_claimed INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            total_logins INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


# Initialize table on module load
init_daily_rewards_table()


def get_today_date():
    """Get today's date as string (YYYY-MM-DD)."""
    return datetime.now().strftime("%Y-%m-%d")


def get_yesterday_date():
    """Get yesterday's date as string."""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


@router.get("/{character_name}")
async def get_daily_reward_status(character_name: str):
    """Get daily reward status for a character."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM daily_rewards WHERE character_name = ?',
        (character_name,)
    )
    row = cursor.fetchone()
    conn.close()
    
    today = get_today_date()
    
    if row:
        data = dict(row)
        last_login = data['last_login_date']
        can_claim = last_login != today
        data['can_claim'] = can_claim
        data['today'] = today
        
        # Calculate streak status
        if last_login == get_yesterday_date():
            data['streak_status'] = 'active'  # Continue streak tomorrow
        elif last_login == today:
            data['streak_status'] = 'claimed'  # Already claimed today
        else:
            data['streak_status'] = 'broken'  # Streak broken
        
        return data
    
    # New player
    return {
        'character_name': character_name,
        'last_login_date': '',
        'consecutive_days': 0,
        'total_rewards_claimed': 0,
        'current_streak': 0,
        'total_logins': 0,
        'can_claim': False,
        'today': today,
        'streak_status': 'new',
    }


@router.post("/claim")
async def claim_daily_reward(claim: RewardClaim):
    """Claim daily reward."""
    character_name = claim.character_name
    day = claim.day
    
    if day < 1 or day > 7:
        raise HTTPException(status_code=400, detail="Invalid day")
    
    reward = DAILY_REWARDS[day - 1]
    today = get_today_date()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get current data
    cursor.execute(
        'SELECT * FROM daily_rewards WHERE character_name = ?',
        (character_name,)
    )
    row = cursor.fetchone()
    
    now = datetime.now()
    
    if row:
        data = dict(row)
        
        # Check if already claimed today
        if data['last_login_date'] == today:
            raise HTTPException(status_code=400, detail="Reward already claimed today")
        
        # Check streak
        last_login = data['last_login_date']
        yesterday = get_yesterday_date()
        
        if last_login == yesterday:
            # Continue streak
            consecutive_days = data['consecutive_days'] + 1
            if consecutive_days > 7:
                consecutive_days = 1  # Reset after day 7
        elif last_login == today:
            consecutive_days = data['consecutive_days']
        else:
            # Streak broken
            consecutive_days = 1
        
        # Update record
        cursor.execute('''
            UPDATE daily_rewards
            SET last_login_date = ?,
                consecutive_days = ?,
                total_rewards_claimed = total_rewards_claimed + 1,
                current_streak = ?,
                total_logins = total_logins + 1
            WHERE character_name = ?
        ''', (today, consecutive_days, consecutive_days, character_name))
    else:
        # New player - create record
        consecutive_days = 1
        cursor.execute('''
            INSERT INTO daily_rewards
            (character_name, last_login_date, consecutive_days, total_rewards_claimed, current_streak, total_logins)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (character_name, today, consecutive_days, 1, consecutive_days, 1))
    
    conn.commit()
    conn.close()
    
    return {
        'success': True,
        'reward': {
            'day': day,
            'xp': reward['xp'],
            'bonus': reward['bonus'],
            'icon': reward['icon'],
        },
        'streak': {
            'current': consecutive_days,
            'max': 7,
        },
        'message': f"You claimed Day {day} reward! +{reward['xp']} XP - {reward['bonus']}",
    }


@router.get("/{character_name}/history")
async def get_reward_history(character_name: str, limit: int = 30):
    """Get reward claim history."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # For now, return simulated history based on data
    cursor.execute(
        'SELECT * FROM daily_rewards WHERE character_name = ?',
        (character_name,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        history = []
        
        # Generate history based on consecutive days
        for i in range(min(data['consecutive_days'], 7)):
            reward = DAILY_REWARDS[i]
            history.append({
                'day': i + 1,
                'xp': reward['xp'],
                'bonus': reward['bonus'],
                'icon': reward['icon'],
                'claimed': True,
            })
        
        # Add remaining days
        for i in range(data['consecutive_days'], 7):
            reward = DAILY_REWARDS[i]
            history.append({
                'day': i + 1,
                'xp': reward['xp'],
                'bonus': reward['bonus'],
                'icon': reward['icon'],
                'claimed': False,
            })
        
        return {
            'current_streak': data['consecutive_days'],
            'total_rewards': data['total_rewards_claimed'],
            'total_logins': data['total_logins'],
            'history': history,
        }
    
    return {
        'current_streak': 0,
        'total_rewards': 0,
        'total_logins': 0,
        'history': [
            {'day': d['day'], 'xp': d['xp'], 'bonus': d['bonus'], 'icon': d['icon'], 'claimed': False}
            for d in DAILY_REWARDS
        ],
    }


@router.get("/streak/{character_name}")
async def get_streak_info(character_name: str):
    """Get detailed streak information."""
    today = get_today_date()
    yesterday = get_yesterday_date()
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM daily_rewards WHERE character_name = ?',
        (character_name,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        data = dict(row)
        last_login = data['last_login_date']
        
        # Check if streak is still valid
        if last_login == today:
            status = 'claimed'
        elif last_login == yesterday:
            status = 'active'  # Can claim tomorrow
        elif last_login == '' or last_login < yesterday:
            # Check if streak should be reset (missed more than 1 day)
            if last_login and datetime.strptime(last_login, "%Y-%m-%d") < datetime.strptime(yesterday, "%Y-%m-%d"):
                status = 'broken'
            else:
                status = 'new'
        else:
            status = 'unknown'
        
        return {
            'current_streak': data['consecutive_days'],
            'last_login': last_login,
            'status': status,
            'can_claim': last_login != today,
            'streak_bonus': data['consecutive_days'] * 10,  # 10 bonus XP per streak day
        }
    
    return {
        'current_streak': 0,
        'last_login': '',
        'status': 'new',
        'can_claim': False,
        'streak_bonus': 0,
    }


# Premium rewards (optional expansion)
PREMIUM_REWARDS = {
    'vip': {
        'multiplier': 2.0,  # Double XP
        'daily_bonus': 100,  # Extra 100 XP daily
        'exclusive_items': ['VIP Badge', 'Golden Avatar'],
    }
}
