import os
import requests

API_KEY = os.environ["GOOGLE_SEARCH_API_KEY"]
CX = os.environ["GOOGLE_SEARCH_CX"]

def search(query: str, num: int = 5) -> list[dict]:
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "hl": "ja",
        "gl": "jp",
        "num": num,
        "sort": "date"
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()

    results = []
    for item in data.get("items", []):
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link"),
            "source": item.get("displayLink"),
        })
    return results
