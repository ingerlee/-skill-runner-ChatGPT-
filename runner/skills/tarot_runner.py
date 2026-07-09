#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))
from config import CACHE_DIR, OUTPUT_DIR, TAROT_EXTERNAL_URL, load_profile, run_date, write_json

MAJORS = (
    "愚者 魔術師 女祭司 女皇 皇帝 教皇 戀人 戰車 力量 隱士 命運之輪 正義 "
    "倒吊人 死神 節制 惡魔 高塔 星星 月亮 太陽 審判 世界"
).split()
SUITS = {"權杖": "火", "聖杯": "水", "寶劍": "風", "星幣": "土"}
RANKS = "Ace 二 三 四 五 六 七 八 九 十 侍從 騎士 皇后 國王".split()
MINORS = [f"{s}{r}" for s in SUITS for r in RANKS]
ELEMENTS = dict(zip(MAJORS, "風 風 水 土 火 土 風 水 火 土 火 風 水 水 火 土 火 風 水 火 火 土".split()))
ELEMENTS.update({card: SUITS[card[:2]] for card in MINORS})
CARDS = MAJORS + MINORS
TIME = {"morning": ("火", "風"), "afternoon": ("水", "土"), "night": ("major",)}
THREE = [("狀態", 0, 0), ("阻力", 1, 0), ("建議", 0, 1)]


def deterministic_seed(date: str, profile: dict) -> int:
    person = profile["person"]
    location = profile["divination_location"]
    raw = "|".join([
        date,
        "08:30",
        person["birth_solar"],
        person["true_solar_time"],
        person["bazi"],
        location["city"],
        "daily",
    ])
    return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16], 16)


def weight(card: str, key: int, boosted: tuple[str, ...]) -> float:
    major = card in MAJORS
    base = (60 / 28) if key * major else 1.0
    hit = (("major" in boosted) and major) or (ELEMENTS.get(card) in boosted)
    return base * (1.08 if hit else 1.0)


def draw_builtin(seed: int, time_factor: str = "morning") -> dict:
    rng = random.Random(seed)
    pool = list(CARDS)
    boosted = TIME[time_factor]
    cards = []
    for name, key, upright_bias in THREE:
        picked = rng.choices(pool, weights=[weight(c, key, boosted) for c in pool], k=1)[0]
        pool.remove(picked)
        cards.append({
            "position": name,
            "card": picked,
            "orientation": "正位" if rng.random() < (0.7 if upright_bias else 0.6) else "逆位",
            "is_major": picked in MAJORS,
        })
    return {"mode": "E3_BUILTIN_TAROT", "seed": seed, "spread": "three", "time_factor": time_factor, "cards": cards}


def try_external(seed: int, question: str) -> tuple[dict | None, str | None]:
    if os.getenv("RUN_EXTERNAL_FETCH", "1") != "1":
        return None, "RUN_EXTERNAL_FETCH disabled"
    try:
        ext_dir = CACHE_DIR / "external"
        ext_dir.mkdir(parents=True, exist_ok=True)
        script = ext_dir / "tarot_draw.py"
        urllib.request.urlretrieve(TAROT_EXTERNAL_URL, script)
        cmd = [sys.executable, str(script), "--spread", "three", "--question", question, "--seed", str(seed), "--time-factor", "morning"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return None, proc.stderr or f"external tarot exited {proc.returncode}"
        payload = json.loads(proc.stdout)
        payload["mode"] = "E1_EXTERNAL_TAROT"
        payload["external_source"] = TAROT_EXTERNAL_URL
        return payload, None
    except Exception as exc:
        return None, repr(exc)


def main() -> int:
    profile = load_profile()
    date = run_date()
    seed = deterministic_seed(date, profile)
    question = f"{date} 玄學盤前交易節奏"
    external, error = try_external(seed, question)
    if external:
        payload = external
        status = "success"
    else:
        payload = draw_builtin(seed)
        payload["external_error"] = error
        status = "degraded"
    payload.update({"skill": "tarot", "status": status, "date": date})
    write_json(f"tarot-{date}.json", payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
