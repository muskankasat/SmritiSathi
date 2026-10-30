"""Populate the local DB with 14 days of demo data so the dashboard has something to show."""
from config import DB_PATH
from core.db import DB

DB(DB_PATH).seed_demo()
print("Demo data written to", DB_PATH)
