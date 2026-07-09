# Project Structure

## backend/

Python FastAPI application.

```text
backend/app/api/v1/
```

HTTP routers. Routers should validate HTTP boundaries and call services.

```text
backend/app/core/
```

Settings and cross-cutting configuration.

```text
backend/app/db/
```

Async SQLAlchemy base and session factory.

```text
backend/app/models/
```

SQLAlchemy ORM models and enums.

```text
backend/app/repositories/
```

Database query and persistence helpers.

```text
backend/app/schemas/
```

Pydantic v2 API contracts.

```text
backend/app/services/
```

Business workflows and orchestration.

```text
backend/app/services/browser_sessions/
```

Provider-specific browser session implementations.

```text
backend/alembic/
```

Database migrations.

## frontend/

React application.

```text
frontend/src/api/
```

Typed Axios API functions.

```text
frontend/src/hooks/
```

TanStack Query hooks and cache invalidation.

```text
frontend/src/pages/
```

Route-level pages.

```text
frontend/src/components/
```

Feature components, layout components, and local shadcn-style primitives.

```text
frontend/src/store/
```

Zustand UI state.

```text
frontend/src/types/
```

Frontend DTO types.

## storage/

Runtime browser identity storage. Example:

```text
storage/reddit/<account>/
  profile/
  storage_state.json
  screenshots/
  downloads/
  logs/
  exports/
```

Runtime browser files should not be treated as source files.

## docs/

Engineering documentation for architecture, APIs, modules, database, roadmap, and developer workflows.

