import os

from tavily import TavilyClient


def tavily_search(query, num=5):
    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        return []

    client = TavilyClient(api_key=api_key)
    data = client.search(query=query, max_results=num)
    items = data.get("results", [])

    results = []
    for item in items:
        results.append(
            {
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "link": item.get("url", ""),
            }
        )
    return results
