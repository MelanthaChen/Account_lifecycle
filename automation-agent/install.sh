#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p logs

echo "===================================="
echo "Automation Agent Installer"
echo "===================================="
echo "Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3.12 or newer is required. Install it from https://www.python.org/downloads/"
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
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "Installing Python dependencies..."
uv sync

echo "Installing Playwright Chromium..."
uv run playwright install chromium

if [ ! -f agent.yaml ]; then
  cp agent.yaml.example agent.yaml
  echo "Created agent.yaml from agent.yaml.example"
fi

echo
echo "Running setup doctor..."
uv run python main.py doctor || true

cat <<'EOF'

Installation finished.

Next step:
Double-click Run.command, or run:
./run.sh

Keep this terminal open while automation jobs are running.
EOF
