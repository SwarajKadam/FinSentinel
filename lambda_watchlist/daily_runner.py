import json
from datetime import datetime
from decimal import Decimal

from app.services.watchlist_service import get_watchlist
from app.services.news_service import fetch_financial_news
from app.services.sentiment_service import predict_sentiment
from app.services.aws_service import upload_json_to_s3, save_prediction_record


def lambda_handler(event, context):
    try:
        tickers = get_watchlist()

        if not tickers:
            return {"message": "No tickers in watchlist"}

        all_results = []

        for item in tickers:
            ticker = item["ticker"]

            # Fetch news for ticker
            articles = fetch_financial_news(category="general", limit=5)

            ticker_results = []
            scores = []

            for article in articles:
                text = article["headline"]

                prediction = predict_sentiment(text)

                label = prediction["label"]
                confidence = prediction["confidence"]

                score = 1 if label == "positive" else -1 if label == "negative" else 0
                scores.append(score)

                record = {
                    "ticker": ticker,
                    "headline": article["headline"],
                    "label": label,
                    "confidence": confidence,
                    "sentiment_score": score,
                    "timestamp": datetime.utcnow().isoformat()
                }

                ticker_results.append(record)

                # Save individual prediction
                save_prediction_record(
                    input_text=article["headline"],
                    label=label,
                    confidence=confidence,
                    input_type="news",
                    source=ticker,
                    headline=article["headline"],
                    url=article.get("url")
                )

            # Save raw + processed to S3
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            raw_key = f"daily/raw/{ticker}_{timestamp}.json"
            processed_key = f"daily/processed/{ticker}_{timestamp}.json"

            upload_json_to_s3(articles, raw_key)
            upload_json_to_s3(ticker_results, processed_key)

            # Compute daily summary
            avg_sentiment = sum(scores) / len(scores) if scores else 0

            summary = {
                "ticker": ticker,
                "date": datetime.utcnow().strftime("%Y-%m-%d"),
                "avg_sentiment": avg_sentiment,
                "article_count": len(scores)
            }

            all_results.append(summary)

        return {
            "status": "success",
            "results": all_results
        }

    except Exception as e:
        return {"error": str(e)}