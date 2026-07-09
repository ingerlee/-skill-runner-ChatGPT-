from __future__ import annotations

import json
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from config import OUTPUT_DIR, run_date, write_json

ROOT = Path(__file__).resolve().parents[1]


def run_step(name: str, command: list[str], timeout: int = 180) -> dict:
    result = {
        "name": name,
        "status": "pending",
        "command": command,
        "stdout": "",
        "stderr": "",
        "error": None,
        "started_at": datetime.now(ZoneInfo("Asia/Taipei")).isoformat(),
        "ended_at": None,
    }
    try:
        proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        result["stdout"] = proc.stdout[-8000:]
        result["stderr"] = proc.stderr[-8000:]
        result["returncode"] = proc.returncode
        result["status"] = "success" if proc.returncode == 0 else "failed"
    except Exception:
        result["status"] = "failed"
        result["error"] = traceback.format_exc()
    finally:
        result["ended_at"] = datetime.now(ZoneInfo("Asia/Taipei")).isoformat()
    return result


def main() -> int:
    date = run_date()
    steps = [
        ("tarot", [sys.executable, "runner/skills/tarot_runner.py"]),
        ("qimen", [sys.executable, "runner/skills/qimen_runner.py"]),
        ("ziwei", ["node", "runner/skills/ziwei_runner.mjs"]),
        ("taibu", ["node", "runner/skills/taibu_runner.mjs"]),
    ]

    smoke = []
    for name, cmd in steps:
        print(f"[run] {name}: {' '.join(cmd)}")
        smoke.append(run_step(name, cmd))

    write_json(f"smoke-test-{date}.json", {"date": date, "steps": smoke})

    render = run_step("render_report", [sys.executable, "runner/render_report.py"])
    mail = run_step("send_email", [sys.executable, "runner/mailer.py"])

    summary = {
        "date": date,
        "skills": smoke,
        "render": render,
        "mail": mail,
        "status": "success" if all(s["status"] == "success" for s in smoke) else "degraded",
    }
    write_json(f"run-summary-{date}.json", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    # Always return 0 so a degraded skill does not block artifact/report delivery.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
