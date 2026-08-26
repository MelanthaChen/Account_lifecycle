#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Please run Install.command first."
  exit 1
fi
uv run python main.py 2>&1 | tee -a "logs/automation-agent.log"
