from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from lambda_package.app.services.news_service import fetch_market_news
from app.services.sentiment_service import analyze_articles, predict_text_sentiment
from app.services.storage_service import (
    list_processed_files,
    read_json_file,
    save_processed_results,
    save_raw_news,
)


router = APIRouter()


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to analyze with FinBERT")


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.get("/news")
def get_news(category: str = "general", limit: int = 5) -> dict:
    try:
        articles = fetch_market_news(category=category, limit=limit)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return {"count": len(articles), "articles": articles}


@router.post("/predict")
def predict_sentiment(request: PredictRequest) -> dict:
    try:
        result = predict_text_sentiment(request.text)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {"text": request.text, **result}


@router.post("/analyze-news")
def analyze_news(category: str = "general", limit: int = 5) -> dict:
    try:
        articles = fetch_market_news(category=category, limit=limit)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    if not articles:
        raise HTTPException(status_code=404, detail="No news articles were returned by Finnhub.")

    raw_file_path = save_raw_news(articles)
    results = analyze_articles(articles)
    processed_file_path = save_processed_results(results)

    return {
        "raw_file": str(raw_file_path),
        "processed_file": str(processed_file_path),
        "count": len(results),
        "results": results,
    }


@router.get("/saved-results")
def get_saved_results(filename: Optional[str] = Query(default=None)) -> dict:
    if filename:
        try:
            file_data = read_json_file(filename, data_type="processed")
        except FileNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

        return {"filename": filename, "data": file_data}

    files = list_processed_files()
    return {"files": files}
