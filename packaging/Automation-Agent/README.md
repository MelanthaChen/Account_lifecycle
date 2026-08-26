# Automation Agent

## Overview

The Automation Agent is a dedicated local browser appliance for the Account Lifecycle Platform.

The web application is already configured. The backend connection and agent credentials are already included in this package. You do not need to edit any configuration files.

```text
Account Lifecycle Web App
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
- Access to the Account Lifecycle web application.

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

## Running the Agent

1. Double-click `Run.command`.
2. Wait for the agent to connect.
3. Open the Account Lifecycle web application.

When the agent is connected, you should see:

```text
Automation Agent
Status: Online
Heartbeat: OK
Browser: Ready
Queue: Waiting for jobs
```

The agent is preconfigured for the professor's deployment:

```text
Backend: https://account-lifecycle-backend.onrender.com/api/v1
Agent: automation-agent
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

The included agent credentials do not match the backend.

Ask the project owner to confirm the Render backend environment variable for the Automation Agent.

### Cannot reach backend

The agent cannot connect to the backend server.

Check:

- Internet connection.
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

No. This package is preconfigured for the professor's deployment.

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
