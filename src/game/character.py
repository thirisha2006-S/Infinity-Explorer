import json
import os
from datetime import datetime

DATA_DIR = "data"
CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")

CHARACTER_CLASSES = {
    "1": {
        "name": "Explorer",
        "description": "Bold and courageous, Explorers venture into the unknown.",
        "base_stats": {"wisdom": 7, "courage": 10, "empathy": 6}
    },
    "2": {
        "name": "Scholar",
        "description": "Wise and knowledgeable, Scholars seek truth and understanding.",
        "base_stats": {"wisdom": 10, "courage": 6, "empathy": 8}
    },
    "3": {
        "name": "Mystic",
        "description": "Intuitive and spiritual, Mystics connect with hidden forces.",
        "base_stats": {"wisdom": 8, "courage": 7, "empathy": 10}
    }
}


class Character:
    def __init__(self, name, char_class, wisdom, courage, empathy):
        self.name = name
        self.char_class = char_class
        self.wisdom = wisdom
        self.courage = courage
        self.empathy = empathy
        self.experience = 0
        self.level = 1
        self.created_at = datetime.now().isoformat()
        self.worlds_visited = []

    def to_dict(self):
        return {
            "name": self.name,
            "class": self.char_class,
            "wisdom": self.wisdom,
            "courage": self.courage,
            "empathy": self.empathy,
            "experience": self.experience,
            "level": self.level,
            "created_at": self.created_at,
            "worlds_visited": self.worlds_visited
        }

    @classmethod
    def from_dict(cls, data):
        char = cls(
            data["name"],
            data["class"],
            data["wisdom"],
            data["courage"],
            data["empathy"]
        )
        char.experience = data.get("experience", 0)
        char.level = data.get("level", 1)
        char.created_at = data.get("created_at", datetime.now().isoformat())
        char.worlds_visited = data.get("worlds_visited", [])
        return char

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= self.level * 100:
            self.level += 1
            self.experience = 0
            return True
        return False

    def visit_world(self, world_name):
        if world_name not in self.worlds_visited:
            self.worlds_visited.append(world_name)

    def get_stats_display(self):
        return f"""
=== {self.name} the {self.char_class} ===
Level: {self.level} | XP: {self.experience}/100
Stats:
  - Wisdom:  {'★' * (self.wisdom // 2)}{'☆' * (5 - self.wisdom // 2)}
  - Courage: {'★' * (self.courage // 2)}{'☆' * (5 - self.courage // 2)}
  - Empathy: {'★' * (self.empathy // 2)}{'☆' * (5 - self.empathy // 2)}
Worlds Visited: {len(self.worlds_visited)}
"""


class CharacterManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.characters = self._load_all()

    def _load_all(self):
        if os.path.exists(CHARACTERS_FILE):
            try:
                with open(CHARACTERS_FILE, 'r') as f:
                    data = json.load(f)
                    return {name: Character.from_dict(char_data) for name, char_data in data.items()}
            except (json.JSONDecodeError, KeyError):
                return {}
        return {}

    def _save_all(self):
        data = {name: char.to_dict() for name, char in self.characters.items()}
        with open(CHARACTERS_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def create_character(self, name, class_choice):
        if name in self.characters:
            return None
        
        if class_choice not in CHARACTER_CLASSES:
            return None
        
        class_info = CHARACTER_CLASSES[class_choice]
        char = Character(
            name=name,
            char_class=class_info["name"],
            wisdom=class_info["base_stats"]["wisdom"],
            courage=class_info["base_stats"]["courage"],
            empathy=class_info["base_stats"]["empathy"]
        )
        self.characters[name] = char
        self._save_all()
        return char

    def get_character(self, name):
        return self.characters.get(name)

    def delete_character(self, name):
        if name in self.characters:
            del self.characters[name]
            self._save_all()
            return True
        return False

    def list_characters(self):
        return list(self.characters.keys())

    def update_character(self, character):
        self.characters[character.name] = character
        self._save_all()
