from datetime import datetime, timezone

from app.services.aws_service import upload_json_to_s3


def generate_timestamped_key(prefix: str, base_name: str):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"{prefix}/{base_name}_{timestamp}.json"


def save_raw_news_to_s3(raw_news_data):
    key = generate_timestamped_key("raw", "news")
    s3_path = upload_json_to_s3(raw_news_data, key)
    return {"key": key, "s3_path": s3_path}


def save_processed_results_to_s3(processed_data):
    key = generate_timestamped_key("processed", "results")
    s3_path = upload_json_to_s3(processed_data, key)
    return {"key": key, "s3_path": s3_path}