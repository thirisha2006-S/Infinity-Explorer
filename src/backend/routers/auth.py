from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
import firebase_admin
from firebase_admin import credentials, auth
import os

router = APIRouter()

# Initialize Firebase Admin SDK (optional - works without real credentials for demo)
try:
    firebase_cred_path = os.getenv("FIREBASE_CRED_PATH", "firebase_creds.json")
    if os.path.exists(firebase_cred_path):
        cred = credentials.Certificate(firebase_cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Demo mode - simulated auth
        firebase_admin.initialize_app(options={
            'projectId': 'infinity-explorer-demo',
        })
except ValueError:
    # Already initialized
    pass


class UserCreate(BaseModel):
    email: str
    password: str
    display_name: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    display_name: str


class UserProfile(BaseModel):
    user_id: str
    email: str
    display_name: str
    photo_url: Optional[str] = None
    created_at: str = ""


# Demo user storage (replace with Firebase in production)
demo_users = {}


@router.post("/signup", response_model=TokenResponse)
async def signup(user: UserCreate):
    """Create a new user account."""
    try:
        # Try Firebase Auth
        try:
            user_record = auth.create_user(
                email=user.email,
                password=user.password,
                display_name=user.display_name,
            )
            
            # Generate custom token for demo
            access_token = f"demo_token_{user_record.uid}"
            
            return TokenResponse(
                access_token=access_token,
                user_id=user_record.uid,
                email=user.email,
                display_name=user.display_name,
            )
        except Exception as firebase_error:
            # Fallback to demo mode
            if user.email in demo_users:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            
            user_id = f"demo_{len(demo_users)}"
            demo_users[user_id] = {
                "email": user.email,
                "password": user.password,  # In production, hash this!
                "display_name": user.display_name,
                "created_at": "",
            }
            
            return TokenResponse(
                access_token=f"demo_token_{user_id}",
                user_id=user_id,
                email=user.email,
                display_name=user.display_name,
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(user: UserLogin):
    """Login with email and password."""
    try:
        # Try Firebase Auth
        try:
            user_record = auth.get_user_by_email(user.email)
            
            # In production, verify password with Firebase Auth
            # For demo, just return success
            
            return TokenResponse(
                access_token=f"demo_token_{user_record.uid}",
                user_id=user_record.uid,
                email=user.email,
                display_name=user_record.display_name or "",
            )
        except Exception as firebase_error:
            # Fallback to demo mode
            for user_id, user_data in demo_users.items():
                if user_data["email"] == user.email:
                    return TokenResponse(
                        access_token=f"demo_token_{user_id}",
                        user_id=user_id,
                        email=user.email,
                        display_name=user_data["display_name"],
                    )
            
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)."""
    return {"message": "Logged out successfully"}


@router.get("/profile/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str):
    """Get user profile."""
    try:
        try:
            user_record = auth.get_user(user_id)
            return UserProfile(
                user_id=user_record.uid,
                email=user_record.email or "",
                display_name=user_record.display_name or "",
                photo_url=user_record.photo_url,
                created_at="",
            )
        except Exception:
            # Demo mode
            if user_id in demo_users:
                user_data = demo_users[user_id]
                return UserProfile(
                    user_id=user_id,
                    email=user_data["email"],
                    display_name=user_data["display_name"],
                )
            
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/profile/{user_id}")
async def update_profile(user_id: str, display_name: str = None, photo_url: str = None):
    """Update user profile."""
    try:
        try:
            if display_name:
                auth.update_user(user_id, display_name=display_name)
            if photo_url:
                auth.update_user(user_id, photo_url=photo_url)
            return {"message": "Profile updated successfully"}
        except Exception:
            # Demo mode
            if user_id in demo_users:
                if display_name:
                    demo_users[user_id]["display_name"] = display_name
                return {"message": "Profile updated successfully"}
            
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/password/reset")
async def password_reset(email: str):
    """Send password reset email."""
    try:
        # In production, this would send an email via Firebase Auth
        return {
            "message": f"Password reset email sent to {email}",
            "note": "Demo mode - email not actually sent"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/account/{user_id}")
async def delete_account(user_id: str):
    """Delete user account."""
    try:
        try:
            auth.delete_user(user_id)
            return {"message": "Account deleted successfully"}
        except Exception:
            # Demo mode
            if user_id in demo_users:
                del demo_users[user_id]
                return {"message": "Account deleted successfully"}
            
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/token/verify")
async def verify_token(token: str):
    """Verify Firebase token."""
    try:
        # In production, verify the actual Firebase token
        if token.startswith("demo_token_"):
            user_id = token.replace("demo_token_", "")
            return {
                "valid": True,
                "user_id": user_id,
                "message": "Demo token verified"
            }
        
        # Try Firebase token verification
        decoded_token = auth.verify_id_token(token)
        return {
            "valid": True,
            "user_id": decoded_token["uid"],
            "message": "Token verified"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }
