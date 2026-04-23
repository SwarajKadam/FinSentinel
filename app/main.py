from fastapi import FastAPI

from app.routes.sentiment_routes import router


app = FastAPI(title="Financial News Sentiment API")
app.include_router(router)
