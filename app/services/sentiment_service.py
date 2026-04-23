from typing import List

from app.models.finbert_model import FinBERTModel
from app.utils.helpers import clean_text, format_unix_timestamp


_model_instance: FinBERTModel | None = None


def get_finbert_model() -> FinBERTModel:
    """Load the model only once and reuse it for later requests."""
    global _model_instance

    if _model_instance is None:
        _model_instance = FinBERTModel()

    return _model_instance


def predict_text_sentiment(text: str) -> dict:
    cleaned_text = clean_text(text)
    if not cleaned_text:
        raise ValueError("Text cannot be empty.")

    model = get_finbert_model()
    return model.predict(cleaned_text)


def analyze_articles(articles: List[dict]) -> List[dict]:
    analyzed_results = []

    for article in articles:
        headline = article.get("headline", "")
        summary = article.get("summary", "")
        text_to_analyze = clean_text(f"{headline}. {summary}".strip())

        if not text_to_analyze:
            continue

        sentiment = predict_text_sentiment(text_to_analyze)

        analyzed_results.append(
            {
                "headline": headline,
                "source": article.get("source", "Unknown"),
                "url": article.get("url", ""),
                "published_date": format_unix_timestamp(article.get("datetime")),
                "label": sentiment["label"],
                "confidence": sentiment["confidence"],
                "probabilities": sentiment["probabilities"],
            }
        )

    return analyzed_results
