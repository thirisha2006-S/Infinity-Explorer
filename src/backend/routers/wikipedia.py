"""
Wikipedia API Router for Earth World Exploration
Provides endpoints for searching and retrieving Wikipedia articles
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import httpx
import xml.etree.ElementTree as ET

router = APIRouter(prefix="/wikipedia", tags=["Wikipedia"])

# Wikipedia API base URLs
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_PAGE_URL = "https://en.wikipedia.org/wiki/"

# Featured categories for exploration
EXPLORATION_CATEGORIES = [
    "Science", "History", "Geography", "Technology", "Culture",
    "Nature", "Space", "Ancient Civilizations", "Modern World",
    "Art", "Philosophy", "Physics", "Biology", "Astronomy"
]


class WikipediaSearchResult(BaseModel):
    """Model for Wikipedia search result"""
    title: str
    snippet: str
    pageid: int
    url: str
    thumbnail: Optional[str] = None


class WikipediaArticle(BaseModel):
    """Model for Wikipedia article"""
    title: str
    pageid: int
    url: str
    extract: str
    thumbnail: Optional[str] = None
    categories: List[str] = []
    related_pages: List[str] = []


class FeaturedTopic(BaseModel):
    """Model for featured exploration topic"""
    title: str
    category: str
    description: str
    image_url: Optional[str] = None
    pageid: int


@router.get("/search")
async def search_wikipedia(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
) -> List[WikipediaSearchResult]:
    """
    Search Wikipedia articles
    """
    async with httpx.AsyncClient() as client:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": limit,
            "format": "json",
            "origin": "*"
        }
        
        try:
            response = await client.get(WIKIPEDIA_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("query", {}).get("search", []):
                thumbnail = None
                if "thumbnail" in item:
                    thumbnail = item["thumbnail"].get("source")
                
                results.append(WikipediaSearchResult(
                    title=item["title"],
                    snippet=item["snippet"].replace("...", "..."),
                    pageid=item["pageid"],
                    url=f"{WIKIPEDIA_PAGE_URL}{item['title'].replace(' ', '_')}",
                    thumbnail=thumbnail
                ))
            
            return results
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Wikipedia API error: {str(e)}")


@router.get("/article/{pageid}")
async def get_article(pageid: int) -> WikipediaArticle:
    """
    Get a Wikipedia article by page ID
    """
    async with httpx.AsyncClient() as client:
        params = {
            "action": "query",
            "prop": "extracts|pageimages|categories",
            "pageids": pageid,
            "exintro": False,
            "explaintext": True,
            "pithumbsize": 500,
            "cllimit": 10,
            "format": "json",
            "origin": "*"
        }
        
        try:
            response = await client.get(WIKIPEDIA_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            page = data.get("query", {}).get("pages", {}).get(str(pageid))
            if not page or page.get("missing"):
                raise HTTPException(status_code=404, detail="Article not found")
            
            thumbnail = None
            if "thumbnail" in page:
                thumbnail = page["thumbnail"].get("source")
            
            categories = []
            for cat in page.get("categories", []):
                cat_title = cat["title"]
                if cat_title.startswith("Category:"):
                    categories.append(cat_title.replace("Category:", ""))
            
            # Get related pages (links to this page)
            related_params = {
                "action": "query",
                "prop": "linkshere",
                "lhlimit": 5,
                "pageids": pageid,
                "format": "json",
                "origin": "*"
            }
            
            related_response = await client.get(WIKIPEDIA_API_URL, params=related_params)
            related_data = related_response.json()
            
            related_pages = []
            for link in related_data.get("query", {}).get("pages", {}).get(str(pageid), {}).get("linkshere", []):
                related_pages.append(link["title"])
            
            return WikipediaArticle(
                title=page["title"],
                pageid=page["pageid"],
                url=f"{WIKIPEDIA_PAGE_URL}{page['title'].replace(' ', '_')}",
                extract=page.get("extract", ""),
                thumbnail=thumbnail,
                categories=categories,
                related_pages=related_pages
            )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Wikipedia API error: {str(e)}")


@router.get("/random")
async def get_random_articles(
    count: int = Query(5, ge=1, le=20, description="Number of random articles")
) -> List[WikipediaArticle]:
    """
    Get random Wikipedia articles for exploration
    """
    async with httpx.AsyncClient() as client:
        articles = []
        
        for _ in range(count):
            try:
                params = {
                    "action": "query",
                    "prop": "extracts|pageimages",
                    "generator": "random",
                    "grnnamespace": 0,
                    "grnlimit": 1,
                    "exintro": True,
                    "explaintext": True,
                    "pithumbsize": 300,
                    "format": "json",
                    "origin": "*"
                }
                
                response = await client.get(WIKIPEDIA_API_URL, params=params)
                response.raise_for_status()
                data = response.json()
                
                pages = data.get("query", {}).get("pages", {})
                if pages:
                    page_id = list(pages.keys())[0]
                    page = pages[page_id]
                    
                    thumbnail = None
                    if "thumbnail" in page:
                        thumbnail = page["thumbnail"].get("source")
                    
                    articles.append(WikipediaArticle(
                        title=page["title"],
                        pageid=page["pageid"],
                        url=f"{WIKIPEDIA_PAGE_URL}{page['title'].replace(' ', '_')}",
                        extract=page.get("extract", "")[:500] + "...",
                        thumbnail=thumbnail,
                        categories=[],
                        related_pages=[]
                    ))
            except Exception:
                continue
        
        return articles


@router.get("/featured")
async def get_featured_topics() -> List[FeaturedTopic]:
    """
    Get featured exploration topics
    """
    async with httpx.AsyncClient() as client:
        featured = []
        
        # Sample featured topics with their Wikipedia page IDs
        topics = [
            ("Solar System", "Science", "Explore our cosmic neighborhood", 0),
            ("Ancient Egypt", "History", "Discover the mysteries of the pharaohs", 0),
            ("Human Brain", "Science", "Unlock the secrets of consciousness", 0),
            ("World War II", "History", "Learn about the pivotal global conflict", 0),
            ("Machine Learning", "Technology", "Dive into the world of AI", 0),
            ("Ocean", "Nature", "Explore Earth's final frontier", 0),
            ("Renaissance", "Culture", "Experience the rebirth of art and science", 0),
            ("Quantum Physics", "Science", "Journey into the subatomic realm", 0),
            ("Amazon Rainforest", "Nature", "Discover the lungs of our planet", 0),
            ("Space Exploration", "Science", "Trace humanity's journey to the stars", 0),
        ]
        
        for title, category, description, _ in topics:
            # Search for the page ID
            params = {
                "action": "query",
                "titles": title,
                "format": "json",
                "origin": "*"
            }
            
            try:
                response = await client.get(WIKIPEDIA_API_URL, params=params)
                data = response.json()
                
                pages = data.get("query", {}).get("pages", {})
                pageid = 0
                thumbnail = None
                
                for page_id, page_data in pages.items():
                    if "missing" not in page_data:
                        pageid = int(page_id)
                        if "thumbnail" in page_data:
                            thumbnail = page_data["thumbnail"].get("source")
                        break
                
                if pageid > 0:
                    featured.append(FeaturedTopic(
                        title=title,
                        category=category,
                        description=description,
                        image_url=thumbnail,
                        pageid=pageid
                    ))
            except Exception:
                continue
        
        return featured


@router.get("/category/{category}")
async def get_category_articles(
    category: str,
    limit: int = Query(10, ge=1, le=50)
) -> List[WikipediaSearchResult]:
    """
    Get articles from a specific category
    """
    async with httpx.AsyncClient() as client:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmlimit": limit,
            "format": "json",
            "origin": "*"
        }
        
        try:
            response = await client.get(WIKIPEDIA_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("query", {}).get("categorymembers", []):
                results.append(WikipediaSearchResult(
                    title=item["title"],
                    snippet="",
                    pageid=item["pageid"],
                    url=f"{WIKIPEDIA_PAGE_URL}{item['title'].replace(' ', '_')}",
                    thumbnail=None
                ))
            
            return results
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Wikipedia API error: {str(e)}")


@router.get("/trending")
async def get_trending_articles() -> List[WikipediaSearchResult]:
    """
    Get trending Wikipedia articles (most viewed)
    """
    # Wikipedia doesn't have a public trending API, so we return featured topics
    return await get_featured_topics()


@router.get("/explore/random")
async def explore_random(
    category: Optional[str] = Query(None, description="Optional category to explore")
) -> WikipediaArticle:
    """
    Get a random article to explore, optionally from a specific category
    """
    async with httpx.AsyncClient() as client:
        params = {
            "action": "query",
            "prop": "extracts|pageimages|categories",
            "generator": "random",
            "grnnamespace": 0,
            "grnlimit": 1,
            "exintro": True,
            "explaintext": True,
            "pithumbsize": 500,
            "cllimit": 5,
            "format": "json",
            "origin": "*"
        }
        
        if category:
            params["grncategory"] = category
        
        try:
            response = await client.get(WIKIPEDIA_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                raise HTTPException(status_code=404, detail="No articles found")
            
            page_id = list(pages.keys())[0]
            page = pages[page_id]
            
            thumbnail = None
            if "thumbnail" in page:
                thumbnail = page["thumbnail"].get("source")
            
            categories = []
            for cat in page.get("categories", []):
                cat_title = cat["title"]
                if cat_title.startswith("Category:"):
                    categories.append(cat_title.replace("Category:", ""))
            
            return WikipediaArticle(
                title=page["title"],
                pageid=int(page_id),
                url=f"{WIKIPEDIA_PAGE_URL}{page['title'].replace(' ', '_')}",
                extract=page.get("extract", ""),
                thumbnail=thumbnail,
                categories=categories,
                related_pages=[]
            )
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"Wikipedia API error: {str(e)}")
