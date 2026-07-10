# Quick Start

This guide is the shortest path from a fresh clone to a running local platform.

## 1. Clone

```bash
git clone <your-fork-url>
cd Account_lifecycle
```

## 2. Start PostgreSQL

```bash
docker compose up -d postgres
```

PostgreSQL listens on host port `55432`.

## 3. Configure Backend

```bash
cp backend/.env.example backend/.env
```

Default database URL:

```text
postgresql+asyncpg://account:account@localhost:55432/account_intelligence
```

## 4. Install Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m playwright install chromium
alembic upgrade head
```

## 5. Start Backend

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal open.

## 6. Start Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

## 7. Open The App

Open `http://localhost:5173`.

Useful checks:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://localhost:5173/api/v1/accounts`

## 8. First Reddit Workflow

1. Go to Accounts.
2. Create a Reddit account entry.
3. Open the account detail page.
4. Click Create Session.
5. Log into Reddit manually in the browser.
6. Click Finish Session.
7. Click Validate Session.
8. Create a Campaign.
9. Apply a Behavior Library template.
10. Run the workflow.
