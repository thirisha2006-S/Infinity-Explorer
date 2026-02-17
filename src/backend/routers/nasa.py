from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import httpx
import os

router = APIRouter()

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
NASA_BASE_URL = "https://api.nasa.gov"


class APODResponse(BaseModel):
    title: str
    explanation: str
    url: str
    media_type: str
    date: str


class PlanetInfo(BaseModel):
    name: str
    description: str
    distance_from_sun: str
    interesting_fact: str


PLANETS_INFO = {
    "mercury": {
        "name": "Mercury",
        "description": "The smallest planet in our solar system and closest to the Sun.",
        "distance_from_sun": "58 million km",
        "interesting_fact": "Mercury has extreme temperature variations, from -173°C at night to 427°C during the day.",
    },
    "venus": {
        "name": "Venus",
        "description": "The second planet from the Sun and our closest neighbor.",
        "distance_from_sun": "108 million km",
        "interesting_fact": "Venus is the hottest planet in our solar system due to its thick greenhouse atmosphere.",
    },
    "earth": {
        "name": "Earth",
        "description": "Our home planet, the third from the Sun.",
        "distance_from_sun": "150 million km",
        "interesting_fact": "Earth is the only planet known to support life.",
    },
    "mars": {
        "name": "Mars",
        "description": "The Red Planet, fourth from the Sun.",
        "distance_from_sun": "228 million km",
        "interesting_fact": "Mars has the largest volcano in the solar system - Olympus Mons.",
    },
    "jupiter": {
        "name": "Jupiter",
        "description": "The largest planet in our solar system.",
        "distance_from_sun": "778 million km",
        "interesting_fact": "Jupiter is so massive that all other planets could fit inside it.",
    },
    "saturn": {
        "name": "Saturn",
        "description": "The sixth planet, famous for its beautiful rings.",
        "distance_from_sun": "1.4 billion km",
        "interesting_fact": "Saturn has more than 80 moons, including Titan, which has a thick atmosphere.",
    },
    "uranus": {
        "name": "Uranus",
        "description": "The seventh planet, an ice giant.",
        "distance_from_sun": "2.9 billion km",
        "interesting_fact": "Uranus rotates on its side, making its seasons last decades.",
    },
    "neptune": {
        "name": "Neptune",
        "description": "The farthest planet from the Sun.",
        "distance_from_sun": "4.5 billion km",
        "interesting_fact": "Neptune has the strongest winds in the solar system, reaching 2,100 km/h.",
    },
}


@router.get("/apod")
async def get_apod():
    """Get Astronomy Picture of the Day from NASA."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NASA_BASE_URL}/planetary/apod",
                params={"api_key": NASA_API_KEY},
            )
            if response.status_code == 200:
                data = response.json()
                return APODResponse(
                    title=data.get("title", ""),
                    explanation=data.get("explanation", ""),
                    url=data.get("url", ""),
                    media_type=data.get("media_type", "image"),
                    date=data.get("date", ""),
                )
            return {"error": "Failed to fetch APOD"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/planet/{planet_name}")
async def get_planet_info(planet_name: str):
    """Get information about a planet."""
    planet_key = planet_name.lower()
    if planet_key in PLANETS_INFO:
        return PLANETS_INFO[planet_key]
    return {"error": "Planet not found"}


@router.get("/planets")
async def get_all_planets():
    """Get information about all planets."""
    return {"planets": list(PLANETS_INFO.values())}


@router.get("/rover/{rover_name}")
async def get_rover_photos(rover_name: str, sol: int = 1000):
    """Get photos from NASA rovers (Curiosity, Opportunity, Spirit)."""
    valid_rovers = ["curiosity", "opportunity", "spirit"]
    if rover_name.lower() not in valid_rovers:
        return {"error": "Rover not found"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NASA_BASE_URL}/mars-photos/api/v1/rovers/{rover_name}/photos",
                params={"api_key": NASA_API_KEY, "sol": sol},
            )
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])[:10]  # Limit to 10 photos
                return {
                    "rover": rover_name,
                    "sol": sol,
                    "photos": [{"id": p["id"], "img_src": p["img_src"]} for p in photos],
                }
            return {"error": "Failed to fetch rover photos"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/neo")
async def get_neo(start_date: str = None, end_date: str = None):
    """Get Near Earth Objects (asteroids) close to Earth."""
    import datetime
    
    if not start_date:
        start_date = datetime.date.today().isoformat()
    if not end_date:
        end_date = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NASA_BASE_URL}/neo/rest/v1/feed",
                params={
                    "api_key": NASA_API_KEY,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            if response.status_code == 200:
                data = response.json()
                neo_count = data.get("element_count", 0)
                near_earth_objects = data.get("near_earth_objects", {})
                
                # Get first 5 asteroids
                asteroids = []
                for date, objects in near_earth_objects.items():
                    for obj in objects[:5]:
                        asteroids.append({
                            "name": obj["name"],
                            "estimated_diameter_km": obj["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
                            "is_potentially_hazardous": obj["is_potentially_hazardous_asteroid"],
                            "close_approach_date": obj["close_approach_data"][0]["close_approach_date"],
                        })
                    if len(asteroids) >= 5:
                        break
                
                return {
                    "count": neo_count,
                    "date_range": f"{start_date} to {end_date}",
                    "asteroids": asteroids,
                }
            return {"error": "Failed to fetch NEO data"}
    except Exception as e:
        return {"error": str(e)}
