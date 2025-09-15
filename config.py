
# config.py
from __future__ import annotations
import os
from pathlib import Path

BASE_DIR = Path(os.getenv("ALZ_BASE_DIR", Path(__file__).resolve().parent))
VAR_DIR = Path(os.getenv("ALZ_VAR_DIR", BASE_DIR / "var"))
DATA_DIR = Path(os.getenv("ALZ_DATA_DIR", BASE_DIR / "data"))
INPUT_DIR = Path(os.getenv("ALZ_INPUT_DIR", DATA_DIR / "input"))
OUTPUT_DIR = Path(os.getenv("ALZ_OUTPUT_DIR", DATA_DIR / "output"))
LOG_DIR = Path(os.getenv("ALZ_LOG_DIR", VAR_DIR / "logs"))
DB_PATH = Path(os.getenv("ALZ_DB_PATH", VAR_DIR / "jobs.db"))

for p in (VAR_DIR, DATA_DIR, INPUT_DIR, OUTPUT_DIR, LOG_DIR):
    p.mkdir(parents=True, exist_ok=True)

API_HOST = os.getenv("ALZ_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("ALZ_API_PORT", "8000"))

AUDIT_REF = str(LOG_DIR / "audit.ndjson")
