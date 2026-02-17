import sys
import os

# Add current directory to path before any imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import characters, chat, worlds, nasa, openstreetmap, achievements, notifications, daily_rewards, auth, wikipedia, nlp
from database import init_db

app = FastAPI(
    title="Infinity Explorer API",
    description="Backend API for Infinity Explorer mobile app",
    version="1.0.0",
)

# CORS middleware for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Include routers
app.include_router(characters.router, prefix="/api/characters", tags=["Characters"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(worlds.router, prefix="/api/worlds", tags=["Worlds"])
app.include_router(nasa.router, prefix="/api/nasa", tags=["NASA"])
app.include_router(openstreetmap.router, prefix="/api/osm", tags=["OpenStreetMap"])
app.include_router(achievements.router, prefix="/api/achievements", tags=["Achievements"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(daily_rewards.router, prefix="/api/daily", tags=["Daily Rewards"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(wikipedia.router, prefix="/api/wikipedia", tags=["Wikipedia"])
app.include_router(nlp.router, prefix="/api/nlp", tags=["NLP"])


# Serve frontend static files - use absolute path from project root
import pathlib
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
frontend_path = PROJECT_ROOT / "frontend"

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    frontend_index = frontend_path / "god_world_preview.html"
    if frontend_index.exists():
        return FileResponse(str(frontend_index))
    return {
        "message": "Welcome to Infinity Explorer API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
