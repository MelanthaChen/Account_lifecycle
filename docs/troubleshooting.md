# Troubleshooting

## Frontend Shows 404 For New API Routes

Check whether Vite is proxying to the correct backend:

```bash
curl http://127.0.0.1:8000/api/v1/recommendations
curl http://localhost:5173/api/v1/recommendations
```

Both should return `200`.

The dev proxy is pinned in `frontend/vite.config.ts`:

```text
http://127.0.0.1:8000
```

If the frontend still returns 404, stop duplicate Vite servers and restart:

```bash
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

## Backend Cannot Connect To PostgreSQL

Start the database:

```bash
docker compose up -d postgres
```

Verify the URL in `backend/.env`:

```text
postgresql+asyncpg://account:account@localhost:55432/account_intelligence
```

## Alembic Fails

Make sure:

- The virtual environment is active.
- PostgreSQL is running.
- `backend/.env` exists.

Then:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

## Playwright Browser Does Not Open

Install Chromium:

```bash
cd backend
source .venv/bin/activate
python -m playwright install chromium
```

If dependencies are missing:

```bash
python -m playwright install --with-deps chromium
```

## Session Finishes But No Login Is Persisted

Check for:

```text
storage/reddit/<username>/storage_state.json
```

If it is missing, the Finish Session workflow should raise an error. Recreate the session and finish only after manual Reddit login is complete.

## Scheduler Does Not Run Jobs

The scheduler starts with the backend. Restart the backend after creating or changing schedules if you suspect jobs were not registered.

Check schedules:

```bash
curl http://127.0.0.1:8000/api/v1/schedules
```

Use Run Now from the campaign detail page to verify execution without waiting for the clock.

## Port Already In Use

Backend:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

Frontend:

```bash
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

Stop stale processes or run on a different port.

## Runtime Storage Was Committed

Runtime profiles can include sensitive browser state. They should not be committed. Keep only `.gitkeep` placeholders in storage directories.

Audit currently detected tracked files under `backend/storage/`. Before making a public fork or release,
remove tracked runtime profile files from version control and rotate any accounts whose cookies may have
been committed.
