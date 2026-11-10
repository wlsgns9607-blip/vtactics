import json
import sqlite3
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
DB_PATH = ROOT / "db" / "volleyball.db"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))

from server import Handler  # type: ignore

class handler(Handler):
    pass

