# Automation Agent Installation Guide

This guide explains how to install and run the Account Lifecycle Automation Agent.

The web application is shared and already deployed:

- Frontend: Vercel
- Backend: Render
- Database: Neon PostgreSQL

The professor runs one Automation Agent on the automation computer. The agent keeps browser profiles, Reddit login sessions, and automation runtime local to that machine.

The professor package is preconfigured. It already includes the backend URL, agent name, and agent secret.

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
- uv Python package manager
- Playwright Chromium browser
- Chrome or Chromium for normal browser testing

The installer scripts can install `uv`, Python dependencies, and Playwright Chromium. Python should be installed first.

## macOS Requirements

Install Python from:

```text
https://www.python.org/downloads/
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

Use PowerShell for the commands in this guide.

## Quick Start

1. Unzip `Automation-Agent.zip`.
2. Open the `Automation-Agent` folder.
3. Double-click `Install.command`.
4. Wait for installation to finish.
5. Double-click `Run.command`.
6. Open the Account Lifecycle web application.

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

From the package folder:

```bash
./Install.command
```

Then run:

```bash
./Run.command
```

## Automatic Installer: Windows

Open PowerShell from the package folder:

```powershell
.\install.ps1
```

Then run:

```powershell
.\run.ps1
```

If PowerShell blocks scripts, run this once in the same PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run `.\install.ps1` again.

## Configuration

The professor package includes `agent.yaml` with the correct backend URL, agent name, and agent secret.

Do not edit `agent.yaml` unless the project owner sends an updated configuration.

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

The included `agent.yaml` fields:

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

The included agent credentials do not match the deployed backend.

Ask the project owner to confirm the Render backend environment variable and send an updated package.

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

For the professor package, use the updated ZIP sent by the project owner.

For repository development, stop the agent with `Ctrl+C`, then:

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
