# Automation Agent Installation Guide

This guide explains how to install and run the Account Lifecycle Automation Agent.

The web application is shared and already deployed:

- Frontend: Vercel
- Backend: Render
- Database: Neon PostgreSQL

Each researcher who owns Reddit accounts should run one Automation Agent on their own computer. The agent keeps that researcher's browser profiles, Reddit login sessions, and automation runtime local to their machine.

## What The Agent Does

The Automation Agent:

- polls the backend for queued jobs
- launches Playwright Chromium locally
- stores persistent browser profiles under `storage/`
- saves Reddit login sessions locally
- executes account jobs such as session login, profile sync, upvote, comment, campaign, and workflow steps
- sends job results back to the backend

Keep the agent terminal open while automation is needed. If the agent is stopped, the web app can still create jobs, but jobs will wait in the queue until the agent is running again.

## Requirements

Install these before starting:

- Python 3.12 or newer
- Git
- uv Python package manager
- Playwright Chromium browser
- Chrome or Chromium for normal browser testing

The installer scripts can install `uv`, Python dependencies, and Playwright Chromium. Python and Git should be installed first.

## macOS Requirements

Install Python from:

```text
https://www.python.org/downloads/
```

Install Git either from Xcode Command Line Tools or from:

```text
https://git-scm.com/downloads
```

To install Xcode Command Line Tools:

```bash
xcode-select --install
```

## Windows Requirements

Install Python 3.12 or newer from:

```text
https://www.python.org/downloads/windows/
```

During installation, enable:

```text
Add python.exe to PATH
```

Install Git from:

```text
https://git-scm.com/download/win
```

Use PowerShell for the commands in this guide.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/MelanthaChen/Account_lifecycle.git
cd Account_lifecycle/automation-agent
```

Install dependencies:

```bash
uv sync --extra dev
```

Install Playwright Chromium:

```bash
uv run playwright install chromium
```

Create the configuration file:

```bash
cp agent.yaml.example agent.yaml
```

On Windows PowerShell:

```powershell
Copy-Item agent.yaml.example agent.yaml
```

Edit `agent.yaml`:

```yaml
agent_name: automation-agent
agent_secret: replace-with-secret-from-platform-admin
backend_url: https://account-lifecycle-backend.onrender.com/api/v1
poll_interval: 5
heartbeat_interval: 30
manual_login_timeout_seconds: 900
profile_root: ../storage
headless: false
provider: reddit
```

Run diagnostics:

```bash
uv run python main.py doctor
```

Start the agent:

```bash
uv run python main.py
```

The terminal should show:

```text
==================================
Automation Agent
Backend: https://account-lifecycle-backend.onrender.com/api/v1
Status: Connecting...
==================================
Automation Agent
Status: Online
Polling: Every 5 seconds
Browser: Ready
Queue: Waiting for jobs
```

## Automatic Installer: macOS/Linux

From the repository root:

```bash
cd automation-agent
chmod +x install.sh run.sh
./install.sh
```

Then edit `agent.yaml` and run:

```bash
./run.sh
```

## Automatic Installer: Windows

Open PowerShell from the repository root:

```powershell
cd automation-agent
.\install.ps1
```

Then edit `agent.yaml` and run:

```powershell
.\run.ps1
```

If PowerShell blocks scripts, run this once in the same PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run `.\install.ps1` again.

## First-Run Configuration Wizard

If `agent.yaml` does not exist, the agent will prompt for:

- Backend URL
- Agent Name
- Agent Secret

Then it creates `agent.yaml` automatically.

Example:

```text
Backend URL [https://account-lifecycle-backend.onrender.com/api/v1]:
Agent Name [automation-agent]:
Agent Secret:
```

Ask the platform administrator for the backend URL and agent secret.

## Doctor Command

Run:

```bash
uv run python main.py doctor
```

The doctor checks:

- Backend reachable
- Authentication
- Heartbeat
- Queue API
- Playwright
- Chromium
- Storage directory
- Profile directory
- Reddit provider

Successful output looks like:

```text
✓ Backend reachable
✓ Authentication
✓ Heartbeat
✓ Queue API
✓ Playwright
✓ Chromium
✓ Storage directory
✓ Profile directory
✓ Reddit provider

Automation Agent is ready.
```

## Configuration Reference

`agent.yaml` fields:

- `agent_name`: display name for this local runtime
- `agent_secret`: secret used to authenticate with the backend
- `backend_url`: Render backend URL ending in `/api/v1`
- `poll_interval`: seconds between queue checks
- `heartbeat_interval`: seconds between health check-ins
- `manual_login_timeout_seconds`: how long Reddit login can remain open
- `profile_root`: where browser profiles are stored
- `headless`: `false` shows Chromium windows
- `provider`: currently `reddit`

## Storage

Browser profiles are stored locally:

```text
storage/
  reddit/
    <account-username>/
      profile/
      storage_state.json
      screenshots/
      downloads/
      logs/
      exports/
```

Do not delete `storage/` unless you intentionally want to remove local Reddit browser sessions.

## Common Errors

### Authentication failed

Check:

- `agent_name`
- `agent_secret`
- `backend_url`

Make sure there are no extra spaces in `agent.yaml`.

### Backend does not support this Automation Agent version

The backend deployment is older than the local agent.

Ask the platform administrator to redeploy the Render backend.

### Playwright Chromium is missing

Run:

```bash
uv run playwright install chromium
```

### Python version too old

Install Python 3.12 or newer.

### Jobs stay queued

Check that:

- the Automation Agent terminal is still open
- `uv run python main.py doctor` passes
- the dashboard shows Automation Agent Online
- the account has a valid Reddit session

## Updating The Agent

Stop the agent with `Ctrl+C`, then:

```bash
git pull
cd automation-agent
uv sync --extra dev
uv run playwright install chromium
uv run python main.py doctor
uv run python main.py
```

## Security Notes

The agent secret grants access to the automation job queue. Keep it private.

Each researcher's Reddit browser sessions remain on their own computer inside `storage/`.
