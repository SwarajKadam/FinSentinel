from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.services.news_service import fetch_market_news
from app.services.sentiment_service import analyze_articles
from app.services.storage_service import save_processed_results, save_raw_news


def main() -> None:
    articles = fetch_market_news(limit=5)
    raw_file = save_raw_news(articles)
    analyzed_results = analyze_articles(articles)
    processed_file = save_processed_results(analyzed_results)

    print(f"Saved raw news to {raw_file}")
    print(f"Saved analyzed news to {processed_file}")


if __name__ == "__main__":
    main()
