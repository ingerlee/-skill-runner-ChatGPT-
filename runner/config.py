from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = ROOT / "inputs"
OUTPUT_DIR = ROOT / "outputs"
CACHE_DIR = ROOT / ".cache"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

PROFILE_PATH = INPUT_DIR / "profile.json"

TAROT_EXTERNAL_URL = "https://raw.githubusercontent.com/daman-ovo-0404/tarot-skill/a9f59f02b3df8a539e9ec618fb4757d481443803/scripts/draw.py"
QIMEN_EXTERNAL_URL = "https://raw.githubusercontent.com/FANzR-arch/Numerologist_skills/847a38ed4245e6fcc50e5fcf099e4b55fb3611a6/qimen-dunjia/scripts/qimen_cli.py"


def load_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def now_taipei() -> datetime:
    return datetime.now(ZoneInfo("Asia/Taipei"))


def run_date() -> str:
    forced = os.getenv("RUN_DATE", "").strip()
    if forced:
        return forced
    return now_taipei().strftime("%Y-%m-%d")


def write_json(name: str, payload: dict) -> Path:
    path = OUTPUT_DIR / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
