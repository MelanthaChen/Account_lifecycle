# Deployment Guide

This guide starts from zero and explains how to run Account Lifecycle Platform locally.

It assumes you have never used FastAPI, React, Playwright, or Alembic.

## What You Are Deploying

The project has three runtime pieces:

```text
PostgreSQL database
FastAPI backend on http://127.0.0.1:8000
React/Vite frontend on http://localhost:5173
```

The backend also starts an in-process APScheduler instance. Playwright runs from the backend process when browser workflows execute.

## System Requirements

- macOS, Linux, or Windows with WSL2
- Python 3.12
- Node.js 20 or newer
- npm 10 or newer
- Docker Desktop or Docker Compose compatible runtime
- Git

Check versions:

```bash
python3.12 --version
node --version
npm --version
docker compose version
git --version
```

## Clone The Repository

```bash
git clone <your-fork-url>
cd Account_lifecycle
```

## Database

The application expects PostgreSQL. The easiest local setup is Docker Compose:

```bash
docker compose up -d postgres
```

This creates:

```text
database: account_intelligence
user: account
password: account
host port: 55432
container port: 5432
```

Connection URL:

```text
postgresql+asyncpg://account:account@localhost:55432/account_intelligence
```

## Backend Environment

Create the backend environment file:

```bash
cp backend/.env.example backend/.env
```

The backend reads `backend/.env` through `pydantic-settings`.

## Backend Dependencies

Create a Python virtual environment:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -e ".[dev]"
```

Alternative with `uv`:

```bash
uv sync --extra dev
source .venv/bin/activate
```

## Playwright

The Python package installs the Playwright library, but not the browser binaries. Install Chromium:

```bash
python -m playwright install chromium
```

If your operating system reports missing system packages:

```bash
python -m playwright install --with-deps chromium
```

## Database Migrations

Alembic creates and updates database tables.

From `backend/`:

```bash
alembic upgrade head
alembic current
```

Expected current head:

```text
0013_scheduler_engine
```

## Start Backend

From `backend/` with the virtual environment active:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

```bash
curl http://127.0.0.1:8000/health
```

Open API docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend Environment

The frontend normally needs no `.env` file for local development. Vite proxies `/api` to `http://127.0.0.1:8000`.

Create one only if you need to override defaults:

```bash
cp frontend/.env.example frontend/.env
```

## Frontend Dependencies

In a second terminal:

```bash
cd frontend
npm install
```

Start:

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

## Create The First Account

1. Open the app.
2. Go to Accounts.
3. Click Add Account.
4. Set Platform to `reddit`.
5. Enter a nickname and Reddit username.
6. Save.

## Create A Browser Session

1. Open the account.
2. Go to Session.
3. Click Create Session.
4. A Chromium browser opens.
5. Log into Reddit manually.
6. Return to the app.
7. Click Finish Session.

The backend writes:

```text
storage/reddit/<username>/profile/
storage/reddit/<username>/storage_state.json
```

Validate the session from the UI. Open Browser or Open Reddit should reuse the logged-in profile.

## Sync Profile

In the account overview, click Sync Profile.

The backend opens the persistent profile, visits the Reddit profile page, scrapes available fields, and updates the account.

## Run A Campaign Workflow

1. Go to Campaigns.
2. Click New Campaign.
3. Enter a campaign name.
4. Enter a Reddit target URL.
5. Select one or more accounts.
6. Save.
7. Open the campaign.
8. Apply a Behavior Library template or edit workflow steps.
9. Click Run Workflow.

Execution is sequential by account.

## Schedule A Campaign

1. Open a campaign.
2. Use the Schedule section.
3. Choose `ONCE`, `DAILY`, `WEEKLY`, or `CUSTOM_CRON`.
4. Save Schedule.
5. Use Run Now to test immediately.

APScheduler loads enabled schedules when the backend starts.

## Docker Notes

`docker compose up --build` builds the backend and frontend containers plus PostgreSQL. For browser automation workflows, local non-container backend development is currently easier because Playwright browser dependencies and visible browser windows are host-sensitive.

If using Docker for backend browser execution, ensure the image has Playwright browser binaries and OS dependencies installed.

## Production Notes

This repository is local-development first. Before public production deployment:

- Add a license.
- Add secret management.
- Move runtime storage to a controlled persistent volume.
- Ensure only one scheduler instance runs active jobs.
- Configure HTTPS and production CORS.
- Add authentication/authorization.
- Review Reddit terms and automation risk.
