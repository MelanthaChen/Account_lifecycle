# Account Lifecycle Platform

## Project Overview

Account Lifecycle Platform is a production-oriented full-stack application for managing Reddit accounts, browser sessions, campaign workflows, behavior templates, health assessments, recommendations, and activity history.

The current implementation is Reddit-focused. The backend keeps provider-specific browser behavior behind a provider registry so additional providers can be added later without rewriting routers or high-level services.

## Problem Statement

Managing multiple social accounts requires more than a table of credentials. Operators need to know:

- Which accounts exist and what state they are in.
- Whether browser sessions are present and valid.
- What profile data has been synchronized.
- What campaigns and workflows are configured.
- What activity happened recently.
- Which accounts need attention before further work.

This project provides that control plane. It does not implement scheduling, AI, posting, commenting, or cross-platform provider support yet.

## Features

- Account CRUD for managed Reddit accounts.
- Account detail workspace with Overview, Session, Activity, and placeholder future tabs.
- Persistent Playwright browser profiles per account.
- Manual Reddit login flow with persisted `storage_state.json`.
- Session validation, refresh, browser open, home open, and deletion.
- Reddit profile synchronization through the persistent browser profile.
- Activity Engine audit log.
- Upvote Engine that opens Reddit URLs and attempts one upvote per selected account sequentially.
- Campaign Engine for reusable UPVOTE campaign plans.
- Workflow Engine with ordered steps: `OPEN_URL`, `WAIT`, `SCROLL`, `OPEN_POST`, `BACK`, `UPVOTE`.
- Behavior Engine for human-like workflow actions.
- Behavior Library with built-in and custom workflow templates.
- Health Engine with rule-based account scoring.
- Recommendation Engine with rule-based next-best actions.
- Dashboard 2.0 control center.

## Architecture Diagram

```text
                  +------------------------+
                  |      React/Vite UI     |
                  | pages, hooks, api/*    |
                  +-----------+------------+
                              |
                              | HTTP /api/v1
                              v
                  +------------------------+
                  |        FastAPI         |
                  | routers call services  |
                  +-----------+------------+
                              |
              +---------------+----------------+
              |                                |
              v                                v
   +----------------------+          +----------------------+
   |      Services        |          |     Repositories     |
   | business workflows   |<-------->| async SQLAlchemy     |
   +----------+-----------+          +----------+-----------+
              |                                 |
              v                                 v
   +----------------------+          +----------------------+
   |  BrowserManager      |          |     PostgreSQL       |
   | provider registry    |          | accounts, campaigns  |
   +----------+-----------+          +----------------------+
              |
              v
   +----------------------+
   | RedditSessionProvider|
   | Playwright profile   |
   +----------+-----------+
              |
              v
   storage/reddit/<account>/
```

## Technology Stack

Backend:

- Python 3.12
- FastAPI
- SQLAlchemy 2.x async ORM
- Alembic
- PostgreSQL
- Pydantic v2
- asyncpg
- Playwright async API
- APScheduler dependency reserved for future task work
- Docker

Frontend:

- React
- TypeScript
- Vite
- TailwindCSS
- shadcn-style local UI primitives
- TanStack Query
- Zustand
- React Router
- Recharts dependency retained; Dashboard 2.0 does not currently use charts

## Project Structure

```text
backend/
  app/
    api/v1/           FastAPI routers
    core/             settings
    db/               SQLAlchemy base/session
    models/           database models and enums
    repositories/     persistence operations
    schemas/          Pydantic request/response models
    services/         application and domain orchestration
    tasks/            reserved scheduler namespace
  alembic/            migrations
frontend/
  src/
    api/              Axios API functions
    components/       UI and feature components
    hooks/            TanStack Query hooks
    pages/            route-level pages
    store/            Zustand state
    types/            frontend DTO types
storage/
  reddit/<account>/   persistent browser identity and artifacts
docs/                 engineering documentation
```

## Data Flow

```text
User action in React
  -> TanStack Query hook
  -> frontend/src/api/*
  -> FastAPI router
  -> service
  -> repository / BrowserManager / provider
  -> PostgreSQL and/or storage/
  -> Pydantic response
  -> Query cache invalidation
  -> UI refresh
```

## Screenshots

Add screenshots after deployment or local capture:

- `docs/assets/dashboard.png`
- `docs/assets/accounts.png`
- `docs/assets/account-session.png`
- `docs/assets/campaign-workflow.png`
- `docs/assets/behavior-library.png`

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ for local frontend development
- Python 3.12 for local backend development
- Playwright browser binaries installed in the backend environment

### Installation

```bash
git clone <repository-url>
cd Account_lifecycle
```

### Running With Docker

```bash
docker compose up --build
```

Run migrations:

```bash
docker compose exec backend alembic upgrade head
```

Open:

- Frontend: `http://localhost:5173`
- Backend health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`

### Running Backend

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Default database URL:

```text
postgresql+asyncpg://account:account@localhost:55432/account_intelligence
```

### Running Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api` to `http://localhost:8000` unless `VITE_BACKEND_PROXY_TARGET` is set.

## Database Migration

```bash
cd backend
alembic upgrade head
alembic current
```

Create migrations manually and keep them small. The current migration head is `0012_recommendation_engine`.

## Development Workflow

```bash
cd backend
ruff check app alembic
python -m compileall app alembic

cd ../frontend
npm run build
```

Keep business logic out of routers. Routers call services, services coordinate repositories and providers, and repositories own persistence operations.

## Example API Flow

Create an account:

```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{"nickname":"Michael","username":"Michael-Geo","platform":"reddit"}'
```

Create a browser session:

```bash
curl -X POST http://localhost:8000/api/v1/accounts/<account_id>/session/create
```

After manual Reddit login:

```bash
curl -X POST http://localhost:8000/api/v1/accounts/<account_id>/session/finish
```

Evaluate account health:

```bash
curl -X POST http://localhost:8000/api/v1/accounts/<account_id>/health/evaluate
```

Evaluate recommendations:

```bash
curl -X POST http://localhost:8000/api/v1/accounts/<account_id>/recommendations/evaluate
```

## Future Roadmap

- Additional providers behind the browser/session provider registry.
- More workflow actions and campaign action types.
- Scheduler/background task integration.
- Richer activity reporting and analytics.
- Provider-specific profile sync improvements.
- Safer operational controls around browser automation.

## License

No license file is currently included. Add a project license before public distribution.
