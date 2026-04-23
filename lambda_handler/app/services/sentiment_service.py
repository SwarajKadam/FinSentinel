from app.services.aws_service import invoke_sagemaker_endpoint


def predict_sentiment(text: str):
    """
    Sends text to SageMaker FinBERT endpoint and returns a simple result.
    """
    if not text or not text.strip():
        raise ValueError("Text input is required.")

    text = text.strip()

    result = invoke_sagemaker_endpoint(text)

    if not result or not isinstance(result, list):
        raise ValueError("Invalid response from SageMaker endpoint.")

    top_prediction = result[0]

    return {
        "text": text,
        "label": top_prediction["label"].lower(),
        "confidence": float(top_prediction["score"]),
    }


def analyze_articles(articles):
    """
    Runs sentiment prediction on a list of article dictionaries.
    """
    analyzed_results = []

    for article in articles:
        headline = article.get("headline", "")
        summary = article.get("summary", "")
        combined_text = f"{headline}. {summary}".strip()

        if not combined_text:
            continue

        prediction = predict_sentiment(combined_text)

        analyzed_article = {
            "headline": headline,
            "summary": summary,
            "source": article.get("source", ""),
            "url": article.get("url", ""),
            "published_at": article.get("published_at", ""),
            "label": prediction["label"],
            "confidence": prediction["confidence"],
        }

        analyzed_results.append(analyzed_article)

    return analyzed_results 