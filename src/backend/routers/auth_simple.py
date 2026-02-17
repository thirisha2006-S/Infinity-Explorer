import secrets
from datetime import datetime, timedelta
from typing import Optional
import hashlib

# Simple JWT-like token system (for demo without Firebase)
SECRET_KEY = secrets.token_hex(32)

# In-memory user storage (for demo - use database in production)
users_db = {}
tokens_db = {}

def hash_password(password: str) -> str:
    """Simple password hashing."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(user_id: str) -> str:
    """Create authentication token."""
    token = secrets.token_urlsafe(32)
    tokens_db[token] = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "expires": (datetime.now() + timedelta(days=7)).isoformat()
    }
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify token and return user info."""
    if token in tokens_db:
        token_data = tokens_db[token]
        expires = datetime.fromisoformat(token_data["expires"])
        if expires > datetime.now():
            return token_data
        else:
            del tokens_db[token]
    return None
