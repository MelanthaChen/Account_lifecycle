# Automation Agent

The Automation Agent is the local browser runtime for a researcher. It polls the FastAPI backend for queued automation jobs and executes workflow steps with Playwright.

```bash
cd automation-agent
uv run python main.py
```

Configuration lives in `agent.yaml`.

For a deployed backend, copy `agent.yaml.example` to `agent.yaml` and set:

- `backend_url`: Render backend URL ending in `/api/v1`
- `agent_name`: use `automation-agent`
- `agent_secret`: the value configured in backend `AUTOMATION_AGENT_SECRET`

The backend owns job state. The Automation Agent owns browser execution, persistent browser profiles, and Reddit sessions for the researcher running it.
