# Automation Agent Release Package

This guide explains how to prepare the dedicated Automation Agent ZIP file for the professor.

The recipient should not need Git and should not edit YAML. They should receive one folder named `Automation-Agent` with the backend URL and agent credentials already included.

## Release Workflow

1. Pull the latest repository.

   ```bash
   git pull
   ```

2. Verify the Automation Agent.

   ```bash
   cd automation-agent
   uv sync
   uv run --extra dev ruff check .
   uv run python -m compileall .
   uv run python main.py doctor
   ```

3. Refresh the package folder.

   ```bash
   python3 scripts/build_automation_agent_package.py
   ```

4. Create the ZIP file.

   ```bash
   cd dist
   zip -r Automation-Agent.zip Automation-Agent
   ```

5. Send `dist/Automation-Agent.zip` to the professor.

## What The ZIP Contains

```text
Automation-Agent/
  Install.command
  Run.command
  README.md
  README.pdf
  agent.yaml.example
  agent.yaml
  automation-agent/
  logs/
```

## Before Sending

Confirm:

- `Install.command` is executable.
- `Run.command` is executable.
- `README.pdf` opens.
- `agent.yaml` contains the professor's dedicated backend URL, agent name, and agent secret.
- `agent.yaml.example` contains the same dedicated configuration as the fallback copy.
- `automation-agent/agent.yaml` is not included inside the nested source folder.
- `automation-agent/.venv`, `.ruff_cache`, and `__pycache__` are not included.

## Recipient Instructions

Tell the recipient:

1. Unzip the file.
2. Double-click `Install.command`.
3. Double-click `Run.command`.
4. Open the web application.
5. Keep the terminal window open while using the web platform.
