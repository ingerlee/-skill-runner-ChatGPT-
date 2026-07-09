#!/usr/bin/env bash
set -euo pipefail
python3 runner/run_all.py
ls -la outputs
