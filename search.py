import requests
from config import SEARCH_API_KEY


class SearchEngine:
def init(self):


self.api_key = SEARCH_API_KEY
self.url = "https://serpapi.com/search"


def search(self, query):


try:
params = {
    "q": query,
    "api_key": self.api_key,
    "engine": "google"
}

response = requests.get(self.url, params=params, timeout=10)
response.raise_for_status()

data = response.json()

if "organic_results" in data:
results = []
for item in data["organic_results"][:5]:
title = item.get("title", "")
snippet = item.get("snippet", "")
link = item.get("link", "")
results.append({
    "title": title,
    "snippet": snippet,
    "link": link
})
return results

return []

except Exception as e:
print(f"Search Error: {e}")
return []
