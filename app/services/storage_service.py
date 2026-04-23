import json
from pathlib import Path
from typing import Any, List

from app.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from app.utils.helpers import generate_timestamp_filename


def _ensure_data_directories() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def write_json_file(file_path: Path, data: Any) -> Path:
    _ensure_data_directories()
    with file_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    return file_path


def read_json_file(filename: str, data_type: str = "processed") -> Any:
    _ensure_data_directories()
    target_directory = PROCESSED_DATA_DIR if data_type == "processed" else RAW_DATA_DIR
    file_path = target_directory / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_raw_news(articles: List[dict]) -> Path:
    filename = generate_timestamp_filename(prefix="raw_news")
    return write_json_file(RAW_DATA_DIR / filename, articles)


def save_processed_results(results: List[dict]) -> Path:
    filename = generate_timestamp_filename(prefix="analyzed_news")
    return write_json_file(PROCESSED_DATA_DIR / filename, results)


def list_processed_files() -> List[str]:
    _ensure_data_directories()
    return sorted(file.name for file in PROCESSED_DATA_DIR.glob("*.json"))
