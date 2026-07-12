"""Advanced search engine with web, news, and weather support."""

from typing import List, Dict, Optional
from core.logger import Logger
from core.config_manager import Config

logger = Logger.get(__name__)

try:
    import requests
except ImportError:
    requests = None


class SearchEngine:
    """Multi-source search with fallback capabilities."""

    def __init__(self) -> None:
        self.api_key = Config.api.search_key
        self.base_url = "https://serpapi.com/search"
        self.news_url = "https://newsapi.org/v2/everything"
        self.weather_url = "https://api.open-meteo.com/v1/forecast"

    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Perform web search."""
        if not self.api_key or not requests:
            logger.warning("Search API not configured or requests library not available")
            return []

        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": num_results
            }
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                })
            return results
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []

    def search_news(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search news articles."""
        if not requests:
            logger.warning("Requests library not available")
            return []

        try:
            params = {
                "q": query,
                "sortBy": "publishedAt",
                "language": "en",
                "pageSize": num_results
            }
            response = requests.get(self.news_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for article in data.get("articles", [])[:num_results]:
                results.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", "")
                })
            return results
        except Exception as e:
            logger.error(f"News search error: {e}")
            return []

    def get_weather(self, latitude: float, longitude: float) -> Optional[Dict]:
        """Get weather information."""
        if not requests:
            logger.warning("Requests library not available")
            return None

        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
            response = requests.get(self.weather_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            return {
                "temperature": current.get("temperature_2m"),
                "weather_code": current.get("weather_code"),
                "wind_speed": current.get("wind_speed_10m")
            }
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return None

    def search_wikipedia(self, query: str) -> Optional[Dict]:
        """Search Wikipedia."""
        if not requests:
            logger.warning("Requests library not available")
            return None

        try:
            params = {
                "action": "query",
                "format": "json",
                "srsearch": query,
                "srwhat": "text"
            }
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            search_results = data.get("query", {}).get("search", [])
            if search_results:
                first_result = search_results[0]
                return {
                    "title": first_result.get("title", ""),
                    "snippet": first_result.get("snippet", "")
                }
            return None
        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return None
