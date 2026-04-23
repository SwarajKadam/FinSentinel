import json

from app.services.news_service import fetch_financial_news
from app.services.sentiment_service import predict_sentiment, analyze_articles
from app.services.storage_service import save_raw_news_to_s3, save_processed_results_to_s3
from app.services.aws_service import save_prediction_record
from app.services.watchlist_service import add_ticker, get_watchlist
from app.services.summary_service import get_ticker_summary


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    path = event.get("rawPath", "")
    method = event.get("requestContext", {}).get("http", {}).get("method", "")

    if path == "/health" and method == "GET":
        return build_response(200, {"status": "ok"})

    if path == "/predict" and method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
            text = body.get("text", "")

            prediction = predict_sentiment(text)

            db_item = save_prediction_record(
                input_text=text,
                label=prediction["label"],
                confidence=prediction["confidence"],
                input_type="text",
                source="direct"
            )

            return build_response(200, {
                "message": "Prediction successful",
                "prediction": prediction
            })

        except Exception as e:
            return build_response(400, {"error": str(e)})

    if path == "/analyze-news" and method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
            category = body.get("category", "general")
            limit = int(body.get("limit", 5))

            news_articles = fetch_financial_news(category=category, limit=limit)

            raw_save_result = save_raw_news_to_s3(news_articles)
            analyzed_results = analyze_articles(news_articles)
            processed_save_result = save_processed_results_to_s3(analyzed_results)

            for article in analyzed_results:
                save_prediction_record(
                    input_text=f"{article.get('headline', '')}. {article.get('summary', '')}",
                    label=article["label"],
                    confidence=article["confidence"],
                    input_type="news_batch",
                    source=article.get("source", ""),
                    s3_raw_key=raw_save_result["key"],
                    s3_processed_key=processed_save_result["key"],
                    headline=article.get("headline", ""),
                    url=article.get("url", ""),
                )

            return build_response(200, {
                "message": "News analysis completed",
                "raw_s3": raw_save_result,
                "processed_s3": processed_save_result,
                "results": analyzed_results
            })

        except Exception as e:
            return build_response(400, {"error": str(e)})
        
    if path == "/watchlist/add" and method == "POST":
        try:
            body = json.loads(event.get("body", "{}"))
            ticker = body.get("ticker", "")

            if not ticker:
                return build_response(400, {"error": "Ticker is required"})

            item = add_ticker(ticker)

            return build_response(200, {
                "message": "Ticker added",
                "ticker": item["ticker"]
            })

        except Exception as e:
            return build_response(400, {"error": str(e)})
        
    if path == "/watchlist" and method == "GET":
        try:
            items = get_watchlist()

            return build_response(200, {
                "watchlist": items
            })

        except Exception as e:
            return build_response(400, {"error": str(e)})
        
    if path == "/ticker-summary" and method == "GET":
        try:
            query_params = event.get("queryStringParameters") or {}
            ticker = query_params.get("ticker", "").strip().upper()

            if not ticker:
                return build_response(400, {"error": "Ticker is required"})

            summary = get_ticker_summary(ticker)
            return build_response(200, summary)

        except Exception as e:
            return build_response(400, {"error": str(e)})

    return build_response(404, {"error": "Route not found"})