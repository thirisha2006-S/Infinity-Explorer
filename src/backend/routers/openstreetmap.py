from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import httpx
import urllib.parse

router = APIRouter()

OSM_BASE_URL = "https://nominatim.openstreetmap.org"


class SearchParams(BaseModel):
    query: str
    limit: int = 10
    format: str = "json"


class LocationResult(BaseModel):
    place_id: int
    osm_id: int
    lat: str
    lon: str
    display_name: str
    class_: str
    type: str


@router.get("/search")
async def search_location(
    q: str,
    limit: int = 10,
    format: str = "json",
):
    """Search for a location using OpenStreetMap Nominatim."""
    try:
        encoded_query = urllib.parse.quote(q)
        url = f"{OSM_BASE_URL}/search"
        params = {
            "q": q,
            "format": format,
            "limit": limit,
            "addressdetails": 1,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data:
                    results.append({
                        "place_id": item.get("place_id", 0),
                        "osm_id": item.get("osm_id", 0),
                        "lat": item.get("lat", ""),
                        "lon": item.get("lon", ""),
                        "display_name": item.get("display_name", ""),
                        "class": item.get("class", ""),
                        "type": item.get("type", ""),
                        "address": item.get("address", {}),
                    })
                return {"results": results}
            return {"error": "Failed to fetch location data"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/reverse")
async def reverse_geocode(
    lat: str,
    lon: str,
):
    """Reverse geocode coordinates to get address."""
    try:
        url = f"{OSM_BASE_URL}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "addressdetails": 1,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {
                    "place_id": data.get("place_id", 0),
                    "lat": data.get("lat", ""),
                    "lon": data.get("lon", ""),
                    "display_name": data.get("display_name", ""),
                    "address": data.get("address", {}),
                }
            return {"error": "Failed to fetch address"}
    except Exception as e:
        return {"error": str(e)}


@router.get("/places/popular")
async def get_popular_places():
    """Get popular places to explore."""
    popular_places = [
        {
            "name": "Eiffel Tower",
            "location": "Paris, France",
            "lat": "48.8584",
            "lon": "2.2945",
            "description": "Iconic iron lattice tower on the Champ de Mars.",
            "category": "landmark",
        },
        {
            "name": "Great Wall of China",
            "location": "China",
            "lat": "40.4319",
            "lon": "116.5704",
            "description": "Ancient series of walls and fortifications.",
            "category": "landmark",
        },
        {
            "name": "Machu Picchu",
            "location": "Peru",
            "lat": "-13.1631",
            "lon": "-72.5450",
            "description": "15th-century Inca citadel in the Andes.",
            "category": "heritage",
        },
        {
            "name": "Taj Mahal",
            "location": "Agra, India",
            "lat": "27.1751",
            "lon": "78.0421",
            "description": "Ivory-white marble mausoleum on the Yamuna River.",
            "category": "landmark",
        },
        {
            "name": "Grand Canyon",
            "location": "Arizona, USA",
            "lat": "36.1069",
            "lon": "-112.1129",
            "description": "Steep-sided canyon carved by the Colorado River.",
            "category": "nature",
        },
        {
            "name": "Mount Everest",
            "location": "Nepal/Tibet",
            "lat": "27.9881",
            "lon": "86.9250",
            "description": "Earth's highest mountain above sea level.",
            "category": "mountain",
        },
        {
            "name": "Amazon Rainforest",
            "location": "South America",
            "lat": "-3.4653",
            "lon": "-62.2159",
            "description": "World's largest tropical rainforest.",
            "category": "nature",
        },
        {
            "name": "Colosseum",
            "location": "Rome, Italy",
            "lat": "41.8902",
            "lon": "12.4922",
            "description": "Ancient oval amphitheatre in Rome.",
            "category": "heritage",
        },
        {
            "name": "Santorini",
            "location": "Greece",
            "lat": "36.3932",
            "lon": "25.4615",
            "description": "Volcanic island in the southern Aegean Sea.",
            "category": "island",
        },
        {
            "name": "Serengeti",
            "location": "Tanzania",
            "lat": "-2.3333",
            "lon": "34.8333",
            "description": "Large savanna ecosystem in Tanzania.",
            "category": "nature",
        },
    ]
    return {"places": popular_places}


@router.get("/places/nearby")
async def get_nearby_places(
    lat: str,
    lon: str,
    category: str = None,
):
    """Get nearby places based on coordinates."""
    try:
        url = f"{OSM_BASE_URL}/search"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 10,
            "limit": 20,
        }
        
        if category:
            params["q"] = category
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return {"places": data[:10]}
            return {"error": "Failed to fetch nearby places"}
    except Exception as e:
        return {"error": str(e)}


# Earth world facts for AI responses
EARTH_FACTS = {
    "continent": [
        "Earth has 7 continents: Africa, Antarctica, Asia, Europe, North America, Australia (Oceania), and South America.",
        "Asia is the largest continent, covering about 30% of Earth's land area.",
        "Antarctica is the coldest, driest, and windiest continent.",
    ],
    "ocean": [
        "Earth has 5 oceans: Pacific, Atlantic, Indian, Arctic, and Southern.",
        "The Pacific Ocean is the largest and deepest ocean on Earth.",
        "The Mariana Trench is the deepest point in any ocean, reaching about 11,000 meters.",
    ],
    "country": [
        "There are 195 countries in the world.",
        "Russia is the largest country by area, while Vatican City is the smallest.",
        "China and India are the two most populous countries.",
    ],
    "culture": [
        "Earth is home to thousands of unique cultures and traditions.",
        "Languages spoken worldwide exceed 7,000, with thousands of dialects.",
        "UNESCO recognizes over 1,000 World Heritage Sites worldwide.",
    ],
    "nature": [
        "Earth is the only planet known to support life.",
        "Biodiversity on Earth includes an estimated 8.7 million species.",
        "Forests cover about 31% of Earth's land area.",
    ],
    "history": [
        "Human civilization dates back approximately 5,000-7,000 years.",
        "Ancient civilizations flourished in Mesopotamia, Egypt, India, and China.",
        "The Renaissance marked a cultural rebirth in Europe from the 14th to 17th century.",
    ],
    "science": [
        "Earth's diameter is approximately 12,742 kilometers.",
        "The planet is about 4.5 billion years old.",
        "Earth's atmosphere is 78% nitrogen and 21% oxygen.",
    ],
}
