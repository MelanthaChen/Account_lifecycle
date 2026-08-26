$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "Automation Agent installer"
Write-Host "Checking Python..."

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    Write-Error "Python 3.12 or newer is required. Install it from https://www.python.org/downloads/"
}
$PythonCommand = $python.Source

& $PythonCommand -c "import sys; raise SystemExit('Python 3.12 or newer is required.') if sys.version_info < (3, 12) else print(f'Python {sys.version_info.major}.{sys.version_info.minor} OK')"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

Write-Host "Installing Python dependencies..."
uv sync --extra dev

Write-Host "Installing Playwright Chromium..."
uv run playwright install chromium

if (-not (Test-Path "agent.yaml")) {
    Copy-Item "agent.yaml.example" "agent.yaml"
    Write-Host "Created agent.yaml from the included professor configuration."
}

Write-Host ""
Write-Host "Installation finished."
Write-Host ""
Write-Host "Next step:"
Write-Host "Start the Automation Agent: .\run.ps1"
Write-Host ""
Write-Host "Keep this PowerShell window open while automation jobs are running."
