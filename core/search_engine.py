"""Advanced search engine with web, news, weather, and Wikipedia."""

from typing import List, Dict, Optional
import requests
from core.logger import Logger
from core.config_manager import Config

logger = Logger.get(__name__)


class SearchEngine:
    """Multi-source search engine for web, news, weather, and knowledge."""

    def __init__(self) -> None:
        self.api_key = Config.api.search_key
        self.serpapi_url = "https://serpapi.com/search"
        self.weather_url = "https://wttr.in"
        self.wikipedia_url = "https://en.wikipedia.org/w/api.php"

    def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web using SerpAPI."""
        if not self.api_key:
            logger.warning("Search API key not configured")
            return []

        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": num_results,
            }
            response = requests.get(self.serpapi_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []
            for item in data.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            logger.debug(f"Web search: found {len(results)} results for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []

    def search_news(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search for news."""
        if not self.api_key:
            return []

        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google_news",
                "num": num_results,
            }
            response = requests.get(self.serpapi_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []
            for item in data.get("news_results", [])[:num_results]:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "source": item.get("source", ""),
                    "date": item.get("date", ""),
                })
            logger.debug(f"News search: found {len(results)} results for '{query}'")
            return results
        except Exception as e:
            logger.error(f"News search failed: {e}")
            return []

    def get_weather(self, location: str = "London") -> Dict:
        """Get weather information."""
        try:
            # Using wttr.in (free, no key required)
            url = f"{self.weather_url}/{location}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            current = data["current_condition"][0]
            return {
                "location": location,
                "temperature": current["temp_C"],
                "condition": current["weatherDesc"][0]["value"],
                "humidity": current["humidity"],
                "wind_speed": current["windspeedKmph"],
            }
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return {}

    def search_wikipedia(self, query: str) -> Optional[Dict]:
        """Search Wikipedia for information."""
        try:
            params = {
                "action": "query",
                "format": "json",
                "srsearch": query,
                "srwhat": "text",
                "srlimit": 1,
            }
            response = requests.get(self.wikipedia_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            search_results = data.get("query", {}).get("search", [])

            if not search_results:
                return None

            # Get the first result's full content
            page_title = search_results[0]["title"]
            page_params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "extracts",
                "explaintext": True,
                "exintro": True,
            }
            page_response = requests.get(self.wikipedia_url, params=page_params, timeout=10)
            page_response.raise_for_status()

            page_data = page_response.json()
            pages = page_data.get("query", {}).get("pages", {})
            page = list(pages.values())[0] if pages else {}

            result = {
                "title": page_title,
                "extract": page.get("extract", "")[:500],  # First 500 chars
            }
            logger.debug(f"Wikipedia search: found '{page_title}'")
            return result
        except Exception as e:
            logger.error(f"Wikipedia search failed: {e}")
            return None

    def smart_search(self, query: str) -> Dict:
        """Intelligent search that routes to appropriate engine."""
        query_lower = query.lower()

        # Detect weather query
        if any(word in query_lower for word in ["weather", "temperature", "forecast"]):
            # Extract location if mentioned
            location = query_lower.replace("weather in", "").replace("weather", "").strip()
            return {"type": "weather", "data": self.get_weather(location or "London")}

        # Detect news query
        if any(word in query_lower for word in ["news", "recent", "latest"]):
            clean_query = query_lower.replace("news", "").replace("recent", "").strip()
            return {"type": "news", "data": self.search_news(clean_query or query)}

        # Try Wikipedia for factual queries
        if any(word in query_lower for word in ["what is", "who is", "define"]):
            clean_query = query_lower.replace("what is", "").replace("who is", "").replace("define", "").strip()
            wiki_result = self.search_wikipedia(clean_query or query)
            if wiki_result:
                return {"type": "wikipedia", "data": wiki_result}

        # Default to web search
        return {"type": "web", "data": self.search_web(query)}
