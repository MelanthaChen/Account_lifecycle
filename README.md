# Account Lifecycle Platform

Account Lifecycle Platform is a full-stack control center for managing Reddit accounts, persistent browser sessions, reusable behavior workflows, campaigns, health scoring, recommendations, activity history, and scheduled campaign execution.

This is not a demo scaffold. The current implementation is a working Reddit-focused platform with a provider abstraction layer so future platforms can be added behind stable service boundaries.

## Project Overview

The platform helps an operator answer:

- Which Reddit accounts are managed?
- Which browser sessions are valid?
- Which account profiles have been synced?
- Which campaigns and workflows are ready to run?
- Which activities happened recently?
- Which accounts need attention?
- Which campaign runs are scheduled next?

The system uses manual login for Reddit accounts. Each account receives its own persistent Playwright Chromium profile and storage state under `storage/reddit/<account>/`.

## Architecture Diagram

```text
React / Vite frontend
  pages -> hooks -> api client
          |
          | HTTP /api/v1
          v
FastAPI backend
  routers -> services -> repositories -> PostgreSQL
              |
              +-> ProviderManager -> RedditProvider
              |       |
              |       +-> session/profile/actions/browser behavior
              |
              +-> APScheduler -> CampaignService -> WorkflowService
```

Runtime browser state:

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

## Features

- Account CRUD for Reddit accounts.
- Account detail workspace with Overview, Session, Activity, Publishing, Analytics, and Settings tabs.
- Persistent Playwright browser profiles per account.
- Manual Reddit login with durable `storage_state.json`.
- Session create, finish, validate, refresh, open browser, open home, and delete.
- Reddit profile synchronization.
- Activity Engine audit log.
- Upvote Engine for sequential multi-account Reddit upvote execution.
- Campaign Engine for reusable execution plans.
- Workflow Engine with ordered steps.
- Behavior Engine actions: `WAIT`, `SCROLL`, `OPEN_POST`, `BACK`.
- Behavior Library with built-in templates.
- Health Engine with rule-based scoring.
- Recommendation Engine with rule-based next actions.
- Scheduler Engine using APScheduler.
- Dashboard 2.0 control center.
- Provider abstraction with Reddit as the first provider.

## Screenshots

Place screenshots here after capturing a local or deployed run:

```text
docs/assets/dashboard.png
docs/assets/accounts.png
docs/assets/account-session.png
docs/assets/campaign-workflow.png
docs/assets/behavior-library.png
docs/assets/scheduler.png
```

## Quick Start

Prerequisites:

- Python 3.12
- Node.js 20 or newer
- npm 10 or newer
- Docker Desktop or another Docker Compose compatible runtime
- Git

Clone and enter the repository:

```bash
git clone <your-fork-url>
cd Account_lifecycle
```

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Configure the backend:

```bash
cp backend/.env.example backend/.env
```

Install backend dependencies:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m playwright install chromium
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

- Platform: `http://localhost:5173`
- Backend health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

## Installation

### Backend

The backend is a Python package configured by `backend/pyproject.toml`.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional `uv` workflow:

```bash
cd backend
uv sync --extra dev
source .venv/bin/activate
```

Install Playwright browser binaries:

```bash
python -m playwright install chromium
```

### Frontend

The frontend uses npm and the checked-in `package-lock.json`.

```bash
cd frontend
npm install
```

## Environment

Backend settings are loaded from `backend/.env` by `pydantic-settings`.

Required local backend values:

```env
APP_NAME="Account Intelligence Platform"
ENVIRONMENT=local
API_V1_PREFIX=/api/v1
DATABASE_URL=postgresql+asyncpg://account:account@localhost:55432/account_intelligence
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

The Vite dev server proxies `/api` to `http://127.0.0.1:8000`. In local development, the frontend normally does not need an `.env` file.

## Project Structure

```text
backend/
  app/
    api/v1/             FastAPI routers
    core/               settings
    db/                 async SQLAlchemy session/base
    models/             ORM models and enums
    providers/          provider abstraction and Reddit provider
    repositories/       database access
    schemas/            Pydantic API contracts
    services/           application orchestration
    tasks/              reserved task namespace
  alembic/              migrations

frontend/
  src/
    api/                Axios API functions
    components/         feature and UI components
    hooks/              TanStack Query hooks
    pages/              route-level pages
    store/              Zustand state
    types/              frontend DTOs

storage/                runtime browser profiles and storage state
docs/                   engineering and deployment documentation
```

## Running Backend

Start PostgreSQL first:

```bash
docker compose up -d postgres
```

Then:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend starts APScheduler during FastAPI startup and reloads enabled campaign schedules from the database.

## Running Frontend

```bash
cd frontend
npm run dev
```

The app runs at `http://localhost:5173`.

Important: the Vite proxy is intentionally pinned to `http://127.0.0.1:8000` to avoid stale shell environment variables sending `/api` traffic to an old backend process.

## Running Migrations

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
alembic current
```

Current migration head:

```text
0013_scheduler_engine
```

## Playwright Setup

Install Chromium for the backend environment:

```bash
cd backend
source .venv/bin/activate
python -m playwright install chromium
```

If your operating system needs Playwright system packages, run:

```bash
python -m playwright install --with-deps chromium
```

On macOS this usually installs only browser binaries.

## Creating Accounts

1. Open `http://localhost:5173`.
2. Go to Accounts.
3. Click Add Account.
4. Use `reddit` as the platform.
5. Enter nickname and Reddit username.
6. Open the account detail page.
7. Use Session -> Create Session.
8. Log into Reddit manually in the opened browser.
9. Return to the app and click Finish Session.

After finishing, the backend writes and verifies:

```text
storage/reddit/<username>/storage_state.json
storage/reddit/<username>/profile/
```

## Running Campaigns

1. Create at least one logged-in account.
2. Open Campaigns.
3. Create a campaign with action type `UPVOTE`.
4. Add one or more accounts.
5. Open the campaign detail page.
6. Edit or apply a workflow template.
7. Click Run Workflow.

Workflow execution is sequential by account. The current Reddit provider supports:

- `OPEN_URL`
- `WAIT`
- `SCROLL`
- `OPEN_POST`
- `BACK`
- `UPVOTE`

## Behavior Library

Behavior templates are reusable workflow definitions stored in the database. Built-in templates are inserted by migration:

- Warm Up
- Quick Upvote
- Casual Reader
- Deep Reader

Open Behavior Library to inspect templates. Open a campaign and use Apply Template to generate workflow steps from a template.

## Scheduler

The Scheduler Engine uses APScheduler inside the FastAPI process.

Campaign schedules are stored in `campaign_schedules` and exposed through:

- `GET /api/v1/schedules`
- `GET /api/v1/campaigns/{campaign_id}/schedule`
- `POST /api/v1/campaigns/{campaign_id}/schedule`
- `PUT /api/v1/campaigns/{campaign_id}/schedule`
- `DELETE /api/v1/campaigns/{campaign_id}/schedule`
- `POST /api/v1/campaigns/{campaign_id}/schedule/run-now`

Open a campaign detail page to create a schedule or run it immediately. Scheduler jobs call `CampaignService.run()` and do not duplicate workflow logic.

## Dashboard

Dashboard 2.0 is the central control center. It displays:

- Health summary cards
- Account health overview
- Recommended actions
- Recent campaigns
- Activity timeline
- Upcoming scheduled runs
- Quick actions

## Provider Architecture

Provider interfaces live under `backend/app/providers/`.

Current provider:

```text
backend/app/providers/reddit/
```

High-level services resolve providers through `ProviderManager`. Reddit-specific browser selectors, session cookies, profile scraping, and actions should remain inside the Reddit provider.

## Known Limitations

- Reddit is the only implemented provider.
- Campaign action type is currently limited to `UPVOTE`.
- Browser automation depends on Reddit's current web UI and may need selector updates over time.
- Scheduler is in-process. It is not a distributed scheduler and should not be run by multiple backend replicas without additional coordination.
- There is no retry engine, queue, notification system, CAPTCHA handling, or AI layer.
- Runtime Playwright profiles can contain sensitive login state and must not be committed.
- No project license file is currently present.

## Future Roadmap

- Additional providers behind `ProviderManager`.
- More campaign action types.
- Safer execution controls and rate-limit policies.
- Richer run history and analytics.
- Optional distributed scheduler or queue.
- Provider-specific profile sync improvements.
- Production deployment hardening.

## Contributing

Read `CONTRIBUTING.md` before opening a pull request.

Minimum verification before a PR:

```bash
cd backend
ruff check app alembic
python -m compileall app alembic

cd ../frontend
npm run build
```

## License

No license file is currently included. Add a license before public distribution.
