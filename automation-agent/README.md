# Automation Agent

The Automation Agent is a local worker that polls the FastAPI backend for queued automation jobs and executes workflow steps with Playwright.

```bash
cd automation-agent
uv run python main.py
```

Configuration lives in `agent.yaml`.

For a deployed backend, copy `agent.yaml.example` to `agent.yaml` and set:

- `backend_url`: Render backend URL ending in `/api/v1`
- `worker_id`: worker id registered in backend `AUTOMATION_WORKERS`
- `worker_secret`: matching secret

The backend owns job state. The agent owns browser execution.
