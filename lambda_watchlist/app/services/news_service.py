import requests

from app.config import FINNHUB_API_KEY, FINNHUB_BASE_URL


def fetch_financial_news(category="general", limit=5):
    """
    Fetches financial news from Finnhub and returns a cleaned list of articles.
    """
    if not FINNHUB_API_KEY:
        raise ValueError("FINNHUB_API_KEY is missing.")

    params = {
        "category": category,
        "token": FINNHUB_API_KEY
    }

    response = requests.get(FINNHUB_BASE_URL, params=params, timeout=20)
    response.raise_for_status()

    articles = response.json()

    cleaned_articles = []
    for article in articles[:limit]:
        cleaned_articles.append({
            "headline": article.get("headline", ""),
            "summary": article.get("summary", ""),
            "source": article.get("source", ""),
            "url": article.get("url", ""),
            "published_at": article.get("datetime", "")
        })

    return cleaned_articles