import requests
from config import SEARCH_API_KEY


class SearchEngine:
    def __init__(self):
        self.api_key = SEARCH_API_KEY
        self.url = "https://serpapi.com/search"

    def search(self, query):
        if not self.api_key:
            print("Search API key not set (SEARCH_API_KEY).")
            return []

        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google"
            }

            response = requests.get(self.url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []
            for item in data.get("organic_results", [])[:5]:
                title = item.get("title", "")
                snippet = item.get("snippet", "")
                link = item.get("link", "")
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link
                })
            return results

        except Exception as e:
            print(f"Search Error: {e}")
            return []
