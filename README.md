# Reddit Account Management Platform

Production-oriented scaffold for managing multiple Reddit accounts, syncing public or user-authorized account activity, and visualizing account analytics.

This is not a Reddit bot and does not implement voting, posting, commenting, or automation that manipulates Reddit engagement.

## Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL, Pydantic v2, APScheduler, httpx
- Frontend: React, TypeScript, Vite, TailwindCSS, shadcn-style components, TanStack Query, React Router, Recharts, Zustand
- Architecture: API routers, service layer, repositories, provider boundary for Reddit, async database access

## Local Run

```bash
docker compose up --build
```

Then run migrations:

```bash
docker compose exec backend alembic upgrade head
```

Open:

- Frontend: http://localhost:5173
- Backend health: http://localhost:8000/health
- API docs: http://localhost:8000/docs

## Project Layout

```text
backend/app/
  api/             FastAPI routers and dependencies
  core/            settings and cross-cutting config
  db/              async SQLAlchemy session/base
  models/          SQLAlchemy models
  repositories/    persistence operations
  reddit/          Reddit provider client
  schemas/         Pydantic v2 API contracts
  services/        business workflows
  tasks/           scheduler setup
frontend/src/
  api/             typed API client functions
  components/      layout and UI components
  hooks/           TanStack Query hooks
  pages/           route pages
  store/           Zustand UI state
  types/           shared frontend types
```

## Extensibility Notes

The Reddit integration is isolated behind `backend/app/reddit/client.py`. Future platforms can follow the same shape: provider client, normalized activity records, service workflow, and platform-specific account metadata.

OAuth/user-authorized sync can be added without changing the dashboard contract by extending the provider boundary and adding credential/token models.
