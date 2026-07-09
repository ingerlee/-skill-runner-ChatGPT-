#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runner"))
from config import CACHE_DIR, OUTPUT_DIR, QIMEN_EXTERNAL_URL, load_profile, run_date, write_json


def build_input(date: str, profile: dict) -> dict:
    loc = profile["divination_location"]
    return {
        "question_type": "daily_market_risk",
        "question_goal": "盤前交易節奏、風險門、文件門、情緒門、尾盤門",
        "calendar_type": "solar",
        "time_input": f"{date} 08:30:00",
        "location": {
            "country": loc.get("country", "China"),
            "city": loc.get("city", "Shenzhen Longgang"),
            "timezone": loc.get("timezone", "Asia/Shanghai"),
        },
        "ruleset": "mainline-cn-v1",
    }


def try_external(date: str, profile: dict) -> tuple[dict | None, str | None]:
    if os.getenv("RUN_EXTERNAL_FETCH", "1") != "1":
        return None, "RUN_EXTERNAL_FETCH disabled"
    try:
        ext_dir = CACHE_DIR / "external"
        ext_dir.mkdir(parents=True, exist_ok=True)
        script = ext_dir / "qimen_cli.py"
        input_path = ext_dir / f"qimen-input-{date}.json"
        output_path = ext_dir / f"qimen-output-{date}.json"
        urllib.request.urlretrieve(QIMEN_EXTERNAL_URL, script)
        input_path.write_text(json.dumps(build_input(date, profile), ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [sys.executable, str(script), "--input", str(input_path), "--output", str(output_path)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        if proc.returncode != 0:
            details = output_path.read_text(encoding="utf-8") if output_path.exists() else proc.stderr
            return None, details or f"external qimen exited {proc.returncode}"
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        payload["mode"] = "E1_EXTERNAL_QIMEN"
        payload["external_source"] = QIMEN_EXTERNAL_URL
        return payload, None
    except Exception as exc:
        return None, repr(exc)


def fallback(date: str, profile: dict, error: str | None) -> dict:
    person = profile["person"]
    return {
        "mode": "E3_RULE_BASED_QIMEN",
        "external_error": error,
        "date": date,
        "normalized_input": build_input(date, profile),
        "chart": {
            "name": "規則化奇門層，不稱完整九宮局",
            "risk_gate": "午後拉升段，易被分時尖峰誘發錯單",
            "trading_gate": "先看開盤價、VWAP、成交量；未確認承接不加倉",
            "document_gate": "利IPO審計底稿、披露差異、證據鏈核對",
            "communication_gate": "文字確認優先；evidence → analysis → conclusion",
            "emotion_gate": "防錯過恐懼與追回虧損衝動",
            "tail_gate": "14:45後偏防守，只處理風險，不新增情緒倉",
            "bazi_anchor": person["bazi"],
            "favorable_elements": person["favorable_elements"],
        },
        "warnings": [
            "qimen_cli.py 未真實成功執行，已啟動 E3 規則化奇門 Runner。",
            "本輸出不得視為完整九宮奇門盤。",
        ],
    }


def main() -> int:
    profile = load_profile()
    date = run_date()
    external, error = try_external(date, profile)
    if external:
        payload = external
        status = "success"
    else:
        payload = fallback(date, profile, error)
        status = "degraded"
    payload.update({"skill": "qimen", "status": status})
    write_json(f"qimen-{date}.json", payload)
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
