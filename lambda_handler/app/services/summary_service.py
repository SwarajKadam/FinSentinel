import boto3
from decimal import Decimal
from app.config import AWS_REGION, DYNAMODB_TABLE_NAME

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
predictions_table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def _decimal_to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def get_ticker_summary(ticker: str):
    ticker = ticker.upper()

    response = predictions_table.scan()
    items = response.get("Items", [])

    # Keep only rows created from scheduled news runs for this ticker
    filtered = [item for item in items if item.get("source") == ticker]

    # Sort newest first if timestamp exists
    filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    if not filtered:
        return {
            "ticker": ticker,
            "avg_sentiment": 0.0,
            "article_count": 0,
            "trend": [],
            "latest_articles": []
        }

    score_map = {"positive": 1, "neutral": 0, "negative": -1}

    scores = []
    latest_articles = []

    for item in filtered[:10]:
        label = item.get("label", "neutral")
        score = score_map.get(label, 0)
        scores.append(score)

        latest_articles.append({
            "headline": item.get("headline", ""),
            "label": label,
            "confidence": _decimal_to_float(item.get("confidence", 0)),
            "timestamp": item.get("timestamp", "")
        })

    avg_sentiment = sum(scores) / len(scores) if scores else 0.0

    # Very simple trend: last 7 items mapped as points
    trend = []
    recent = filtered[:7]
    recent.reverse()

    for idx, item in enumerate(recent, start=1):
        label = item.get("label", "neutral")
        trend.append({
            "day": f"Point {idx}",
            "sentiment": score_map.get(label, 0)
        })

    return {
        "ticker": ticker,
        "avg_sentiment": avg_sentiment,
        "article_count": len(filtered),
        "trend": trend,
        "latest_articles": latest_articles
    }