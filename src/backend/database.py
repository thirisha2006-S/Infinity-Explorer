import sqlite3
import os
from typing import Optional, List, Dict

DATABASE_PATH = "data/infinity_explorer.db"


def get_connection():
    """Get database connection."""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Characters table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            char_class TEXT NOT NULL,
            wisdom INTEGER DEFAULT 5,
            courage INTEGER DEFAULT 5,
            empathy INTEGER DEFAULT 5,
            experience INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            worlds_visited TEXT DEFAULT '[]'
        )
    ''')
    
    # Messages table for chat history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_name TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            emotion TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # World visits table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS world_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_name TEXT NOT NULL,
            world_id TEXT NOT NULL,
            visited_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(character_name, world_id)
        )
    ''')
    
    conn.commit()
    conn.close()


class CharacterDB:
    """Database operations for characters."""
    
    @staticmethod
    def create(name: str, char_class: str, wisdom: int, courage: int, empathy: int) -> Dict:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO characters (name, char_class, wisdom, courage, empathy)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, char_class, wisdom, courage, empathy))
            conn.commit()
            return CharacterDB.get(name)
        except sqlite3.IntegrityError:
            return {"error": "Character already exists"}
        finally:
            conn.close()
    
    @staticmethod
    def get(name: str) -> Optional[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    
    @staticmethod
    def get_all() -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM characters ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(name: str, **kwargs) -> Optional[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        set_clause = ', '.join([f"{k} = ?" for k in kwargs])
        values = list(kwargs.values()) + [name]
        cursor.execute(f'UPDATE characters SET {set_clause} WHERE name = ?', values)
        conn.commit()
        conn.close()
        return CharacterDB.get(name)
    
    @staticmethod
    def delete(name: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM characters WHERE name = ?', (name,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    @staticmethod
    def add_xp(name: str, amount: int) -> Dict:
        char = CharacterDB.get(name)
        if char:
            new_xp = char['experience'] + amount
            new_level = char['level']
            xp_needed = new_level * 100
            
            if new_xp >= xp_needed:
                new_xp -= xp_needed
                new_level += 1
            
            CharacterDB.update(name, experience=new_xp, level=new_level)
            return CharacterDB.get(name)
        return {"error": "Character not found"}
    
    @staticmethod
    def visit_world(name: str, world_id: str) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO world_visits (character_name, world_id)
                VALUES (?, ?)
            ''', (name, world_id))
            conn.commit()
            return True
        finally:
            conn.close()
    
    @staticmethod
    def get_worlds_visited(name: str) -> List[str]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT world_id FROM world_visits WHERE character_name = ?', (name,))
        rows = cursor.fetchall()
        conn.close()
        return [row['world_id'] for row in rows]


class MessageDB:
    """Database operations for messages."""
    
    @staticmethod
    def add(character_name: str, role: str, content: str, emotion: str = None):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO messages (character_name, role, content, emotion)
            VALUES (?, ?, ?, ?)
        ''', (character_name, role, content, emotion))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_history(character_name: str, limit: int = 50) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM messages 
            WHERE character_name = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (character_name, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows][::-1]
