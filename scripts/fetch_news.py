from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.services.news_service import fetch_market_news
from app.services.storage_service import save_raw_news


def main() -> None:
    articles = fetch_market_news(limit=5)
    file_path = save_raw_news(articles)
    print(f"Saved {len(articles)} raw articles to {file_path}")


if __name__ == "__main__":
    main()
