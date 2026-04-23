import os


FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "FinSentinelPredictions")
WATCHLIST_TABLE_NAME = os.getenv("WATCHLIST_TABLE_NAME", "FinSentinelWatchlist")

FINNHUB_BASE_URL = "https://finnhub.io/api/v1/news"
