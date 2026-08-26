# Automation Agent

## Overview

The Automation Agent is the local browser helper for the Account Lifecycle Platform.

You use the web application in your browser. The Automation Agent runs quietly on your computer and performs browser tasks when the web application sends a job.

```text
Web Application
      |
      v
Backend Server
      |
      v
Automation Agent on this computer
      |
      v
Chrome / Reddit
```

Keep the Automation Agent window open while you are creating Reddit sessions or running campaigns.

## Requirements

Before installing, you need:

- macOS.
- Internet access.
- Python 3.12 or newer.
- The Agent Secret from the platform administrator.
- Access to the deployed Account Lifecycle web application.

The installer will install:

- uv, the Python dependency manager.
- Python dependencies for the agent.
- Playwright Chromium, the browser used by the agent.

## Installation

1. Unzip the `Automation-Agent.zip` file.
2. Open the `Automation-Agent` folder.
3. Double-click `Install.command`.
4. Wait until you see `Installation complete`.

If macOS blocks the file:

1. Right-click `Install.command`.
2. Click `Open`.
3. Click `Open` again if macOS asks for confirmation.

## First Run

1. Double-click `Run.command`.
2. If this is the first run, the Agent will ask for:
   - Backend URL
   - Agent Name
   - Agent Secret
3. Enter the values provided by the project owner.

Use this Backend URL unless the project owner gives you a different one:

```text
https://account-lifecycle-backend.onrender.com/api/v1
```

Use this Agent Name unless the project owner gives you a different one:

```text
automation-agent
```

When the agent is connected, you should see:

```text
Automation Agent
Status: Online
Heartbeat: OK
Browser: Ready
Queue: Waiting for jobs
```

## Creating a Reddit Session

1. Start the Automation Agent with `Run.command`.
2. Open the Account Lifecycle web application.
3. Go to an account.
4. Click `Create Session`.
5. A browser window opens.
6. Log in to Reddit manually.
7. Leave the browser open until the agent confirms the session is saved.

After this, the agent can reuse that Reddit session for future jobs.

## Keeping the Agent Running

The terminal window must stay open while automation is needed.

You can stop the agent by pressing:

```text
Control + C
```

You can start it again later by double-clicking `Run.command`.

## Doctor Mode

Doctor mode checks whether the agent is ready.

Open Terminal, go to the `automation-agent` folder, and run:

```bash
AGENT_CONFIG_PATH="../agent.yaml" uv run python main.py doctor
```

Doctor checks:

- Python
- uv
- Dependencies
- Playwright
- Chromium
- Backend connection
- Authentication
- Queue API
- Heartbeat
- Storage folder
- Browser launch

## Common Errors

### Authentication failed

The Agent Secret is wrong or missing.

Check:

- `agent.yaml`
- `agent_name`
- `agent_secret`
- `backend_url`

Ask the project owner for the correct Agent Secret.

### Cannot reach backend

The agent cannot connect to the backend server.

Check:

- Internet connection.
- Backend URL.
- Whether the backend server is awake.

Try again after one minute.

### Backend not updated

The backend does not support this agent version.

Ask the project owner to redeploy the backend.

### Browser installation missing

Run `Install.command` again.

This reinstalls Playwright Chromium.

### Python is missing

Install Python 3.12 or newer from:

```text
https://www.python.org/downloads/
```

## FAQ

### Do I need Git?

No. If you received the ZIP file, you do not need Git.

### Do I need to edit YAML?

Usually no. `Run.command` will ask for the required values if the configuration is missing.

### Can I close the agent?

Yes, but automation jobs will not run while it is closed.

### Does the agent publish by itself?

No. The web application creates jobs. The agent only executes jobs that the platform queues.

### Where are logs stored?

Logs are stored in:

```text
logs/automation-agent.log
```

### Where are browser sessions stored?

Browser profiles and session files are stored in:

```text
storage/
```
