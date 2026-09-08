#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p logs
handle_interrupt() {
  echo "Automation Agent stopped."
  exit 0
}
trap handle_interrupt INT
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Please run Install.command first."
  exit 1
fi
export PYTHONUNBUFFERED=1
uv run python main.py 2>&1 | tee -a "logs/automation-agent.log"
STATUS=${PIPESTATUS[0]}
trap - INT
if [ "$STATUS" -eq 0 ] || [ "$STATUS" -eq 120 ] || [ "$STATUS" -eq 130 ]; then
  echo "Automation Agent stopped."
  exit 0
fi
exit "$STATUS"
