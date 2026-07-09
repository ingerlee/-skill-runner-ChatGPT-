from __future__ import annotations

import json
import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from config import OUTPUT_DIR, load_profile, run_date, write_json


def main() -> int:
    date = run_date()
    profile = load_profile()
    report_path = OUTPUT_DIR / f"report-{date}.md"

    status = {
        "date": date,
        "status": "pending",
        "reason": None,
        "to": os.getenv("EMAIL_TO") or profile.get("email", {}).get("to"),
    }

    if not report_path.exists():
        status.update({"status": "failed", "reason": f"missing report file: {report_path}"})
        write_json(f"mail-status-{date}.json", status)
        print(json.dumps(status, ensure_ascii=False))
        return 0

    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "465") or 465)
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()
    email_from = os.getenv("EMAIL_FROM", smtp_user).strip()
    email_to = os.getenv("EMAIL_TO", profile.get("email", {}).get("to", "")).strip()

    missing = [k for k, v in {
        "SMTP_HOST": smtp_host,
        "SMTP_USER": smtp_user,
        "SMTP_PASS": smtp_pass,
        "EMAIL_FROM": email_from,
        "EMAIL_TO": email_to,
    }.items() if not v]

    if missing:
        status.update({
            "status": "skipped",
            "reason": f"missing secrets/env: {', '.join(missing)}",
        })
        write_json(f"mail-status-{date}.json", status)
        print(json.dumps(status, ensure_ascii=False))
        return 0

    body = report_path.read_text(encoding="utf-8")
    subject_template = profile.get("email", {}).get("subject_template", "每日玄學盤前起卦｜{date}｜術數×量化×交易節奏")
    subject = subject_template.format(date=date)

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as server:
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        status.update({"status": "sent", "reason": None, "subject": subject})
    except Exception as exc:
        status.update({"status": "failed", "reason": repr(exc), "subject": subject})

    write_json(f"mail-status-{date}.json", status)
    print(json.dumps(status, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
