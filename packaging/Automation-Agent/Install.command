#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
AGENT_DIR="$PWD/automation-agent"

echo "===================================="
echo "Automation Agent Installer"
echo "===================================="
echo

if [ ! -d "$AGENT_DIR" ]; then
  echo "The automation-agent folder is missing."
  echo "Please use the complete Automation-Agent package."
  read -r -p "Press Enter to close..."
  exit 1
fi

mkdir -p "$PWD/logs"

echo "Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.12 or newer is required."
  echo "Install Python from https://www.python.org/downloads/"
  read -r -p "Press Enter to close..."
  exit 1
fi

python3 - <<'PY'
import sys
if sys.version_info < (3, 12):
    raise SystemExit("Python 3.12 or newer is required.")
print(f"Python {sys.version_info.major}.{sys.version_info.minor} OK")
PY

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv installation did not finish correctly."
  echo "Close this window, open Install.command again, or install uv from https://docs.astral.sh/uv/"
  read -r -p "Press Enter to close..."
  exit 1
fi

if [ ! -f "$PWD/agent.yaml" ]; then
  cp "$PWD/agent.yaml.example" "$PWD/agent.yaml"
  echo "Created agent.yaml"
fi

echo "Installing Python dependencies..."
cd "$AGENT_DIR"
uv sync

echo "Installing Playwright Chromium..."
uv run playwright install chromium

echo
echo "Installation complete."
echo
echo "Next step:"
echo "Double-click Run.command."
echo
read -r -p "Press Enter to close..."
