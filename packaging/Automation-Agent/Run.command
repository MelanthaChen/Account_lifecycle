#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"
AGENT_DIR="$PWD/automation-agent"
CONFIG_PATH="$PWD/agent.yaml"
LOG_DIR="$PWD/logs"
LOG_FILE="$LOG_DIR/automation-agent.log"

mkdir -p "$LOG_DIR"

handle_interrupt() {
  echo
  echo "Automation Agent stopped. You can close this window."
  echo
  exit 0
}

trap handle_interrupt INT

echo "===================================="
echo "Automation Agent"
echo "===================================="
echo

if [ ! -d "$AGENT_DIR" ]; then
  echo "The automation-agent folder is missing."
  echo "Please use the complete Automation-Agent package."
  if [ -t 0 ]; then
    read -r -p "Press Enter to close..."
  fi
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed."
  echo "Please double-click Install.command first."
  if [ -t 0 ]; then
    read -r -p "Press Enter to close..."
  fi
  exit 1
fi

if [ ! -f "$CONFIG_PATH" ]; then
  cp "$PWD/agent.yaml.example" "$CONFIG_PATH"
fi

cd "$AGENT_DIR"
export AGENT_CONFIG_PATH="$CONFIG_PATH"
export PYTHONUNBUFFERED=1

uv run python main.py 2>&1 | tee -a "$LOG_FILE"
STATUS=${PIPESTATUS[0]}
trap - INT

if [ "$STATUS" -eq 0 ] || [ "$STATUS" -eq 120 ] || [ "$STATUS" -eq 130 ]; then
  echo
  echo "Automation Agent stopped. You can close this window."
  echo
elif [ "$STATUS" -ne 0 ]; then
  echo
  echo "The Automation Agent stopped with an error."
  echo
  echo "Try these steps:"
  echo "1. Double-click Install.command again."
  echo "2. Run doctor mode:"
  echo "   cd automation-agent"
  echo "   AGENT_CONFIG_PATH=\"$CONFIG_PATH\" uv run python main.py doctor"
  echo "3. Check agent.yaml for the backend URL and agent secret."
  echo
fi

if [ -t 0 ]; then
  read -r -p "Press Enter to close..."
fi
exit "$STATUS"
