# Local Development Guide

## Prerequisites

- Python 3.12
- Node.js 20+
- npm 10+
- Docker Compose
- Git

Optional:

- `uv` for Python environment management

## Backend Setup

```bash
docker compose up -d postgres
cd backend
cp .env.example .env
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m playwright install chromium
alembic upgrade head
```

Run:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Backend Setup With uv

```bash
cd backend
uv sync --extra dev
source .venv/bin/activate
python -m playwright install chromium
alembic upgrade head
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The Vite proxy forwards `/api` to `http://127.0.0.1:8000`.

## Verification

Backend:

```bash
cd backend
ruff check app alembic
python -m compileall app alembic
```

Frontend:

```bash
cd frontend
npm run build
```

Database:

```bash
cd backend
alembic current
```

## Working With Migrations

Models live in `backend/app/models/`.

Create migrations manually under `backend/alembic/versions/`. Keep migrations small and include both `upgrade()` and `downgrade()`.

Apply migrations:

```bash
alembic upgrade head
```

## Browser Sessions

Browser sessions use Playwright persistent Chromium profiles.

Runtime files live under:

```text
storage/reddit/<username>/
```

Do not commit runtime profiles, cookies, or storage state.

## Scheduler Development

The scheduler starts with FastAPI. Enabled schedules are loaded from the database during startup.

For local testing:

1. Start backend.
2. Create a campaign.
3. Open the campaign detail page.
4. Save a schedule.
5. Use Run Now.

The scheduler calls `CampaignService.run()` and does not bypass workflow execution.
