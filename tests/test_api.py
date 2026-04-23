from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_endpoint(monkeypatch) -> None:
    def mock_predict_text_sentiment(text: str) -> dict:
        return {
            "label": "positive",
            "confidence": 0.92,
            "probabilities": {
                "positive": 0.92,
                "negative": 0.03,
                "neutral": 0.05,
            },
        }

    monkeypatch.setattr("app.routes.sentiment_routes.predict_text_sentiment", mock_predict_text_sentiment)

    response = client.post(
        "/predict",
        json={"text": "Tesla stock rises after strong quarterly earnings."},
    )

    assert response.status_code == 200
    assert response.json()["label"] == "positive"


def test_analyze_news_endpoint(monkeypatch) -> None:
    sample_articles = [
        {
            "headline": "Tesla shares move higher",
            "summary": "Investors reacted well to earnings.",
            "source": "Demo News",
            "url": "https://example.com/article",
            "datetime": 1710000000,
        }
    ]

    sample_results = [
        {
            "headline": "Tesla shares move higher",
            "source": "Demo News",
            "url": "https://example.com/article",
            "published_date": "2024-03-09 16:00:00",
            "label": "positive",
            "confidence": 0.91,
            "probabilities": {
                "positive": 0.91,
                "negative": 0.04,
                "neutral": 0.05,
            },
        }
    ]

    monkeypatch.setattr("app.routes.sentiment_routes.fetch_market_news", lambda category="general", limit=5: sample_articles)
    monkeypatch.setattr("app.routes.sentiment_routes.analyze_articles", lambda articles: sample_results)

    response = client.post("/analyze-news")

    assert response.status_code == 200
    assert response.json()["count"] == 1
