"""Central configuration for SmritiSaathi (frontend)."""
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("SMRITI_DATA", Path.home() / ".smritisaathi"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "smritisaathi.db"          # on-device SQLite (offline-first store)

API_URL = os.environ.get("SMRITI_API", "http://localhost:8000")   # FastAPI backend (next phase)
SYNC_INTERVAL_SEC = 30
DEFAULT_LANG = "hi"
MAX_LEVEL = 3
