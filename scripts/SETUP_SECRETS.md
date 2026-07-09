# GitHub Secrets Setup

Go to your repository:

Settings → Secrets and variables → Actions → New repository secret

Add:

- `SMTP_HOST` = `smtp.gmail.com`
- `SMTP_PORT` = `465`
- `SMTP_USER` = sender Gmail address
- `SMTP_PASS` = Gmail app password, not your normal login password
- `EMAIL_FROM` = sender Gmail address
- `EMAIL_TO` = `nuovalee@hotmail.com`

Then run:

Actions → Daily Mystic Skill Runner → Run workflow

If email does not send, download the workflow artifact and read:

- `mail-status-YYYY-MM-DD.json`
- `run-summary-YYYY-MM-DD.json`
- `smoke-test-YYYY-MM-DD.json`
