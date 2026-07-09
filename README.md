# mystic-skill-runner

Stable external-skill runner for the daily `玄學盤前起卦｜術數×量化×交易節奏` workflow.

This repo moves external skill execution out of ChatGPT's temporary automation runtime and into a fixed GitHub Actions runtime.

## What it does

At each run it:

1. Runs a smoke test for each external skill path.
2. Attempts true external execution first.
3. Falls back to built-in deterministic runners if an external skill fails.
4. Generates JSON outputs and a Markdown report.
5. Attempts email delivery through SMTP.
6. Uploads outputs as GitHub Actions artifacts.

## Included runners

| Runner | Primary external path | Fallback |
|---|---|---|
| Tarot | pinned `daman-ovo-0404/tarot-skill/scripts/draw.py` | built-in deterministic draw logic |
| Qimen | pinned `FANzR-arch/Numerologist_skills/qimen-dunjia/scripts/qimen_cli.py` | rule-based qimen summary |
| Ziwei | `iztro` + `lunar-javascript` npm packages | structured skeleton only |
| Taibu | `taibu-core` npm package smoke/import | symbolic taibu layer |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
python runner/run_all.py
```

Outputs appear under `outputs/`.

## GitHub Actions setup

Create a new GitHub repo, upload this folder, then add these repository secrets:

| Secret | Example |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `465` |
| `SMTP_USER` | your sender Gmail address |
| `SMTP_PASS` | Gmail app password or SMTP password |
| `EMAIL_FROM` | your sender Gmail address |
| `EMAIL_TO` | `nuovalee@hotmail.com` |

Then run **Actions → Daily Mystic Skill Runner → Run workflow** once manually.

The schedule is set at `00:20 UTC`, equal to `08:20 Asia/Taipei`, to avoid peak-hour GitHub Actions delays.

## Operational rule

A failed external skill must not fail the whole report. It must be recorded in `smoke-test-YYYY-MM-DD.json`, then replaced by fallback output.

