from datetime import datetime, timezone
import boto3

from app.config import AWS_REGION, WATCHLIST_TABLE_NAME

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
watchlist_table = dynamodb.Table(WATCHLIST_TABLE_NAME)


def add_ticker(ticker):
    ticker = ticker.upper()

    item = {
        "ticker": ticker,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True
    }

    watchlist_table.put_item(Item=item)
    return item


def get_watchlist():
    response = watchlist_table.scan()
    items = response.get("Items", [])

    # Only return active tickers
    return [item for item in items if item.get("is_active", True)]