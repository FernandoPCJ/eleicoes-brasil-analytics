from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


RAW_DATA = BASE_DIR / "data" / "raw"

PROCESSED_DATA = BASE_DIR / "data" / "processed"