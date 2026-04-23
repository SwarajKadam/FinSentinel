from datetime import datetime
import re


def generate_timestamp_filename(prefix: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.json"


def clean_text(text: str) -> str:
    # Replace repeated spaces and strip leading/trailing whitespace.
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


def format_unix_timestamp(unix_time: int | None) -> str:
    if unix_time is None:
        return "Unknown"

    return datetime.fromtimestamp(unix_time).strftime("%Y-%m-%d %H:%M:%S")
