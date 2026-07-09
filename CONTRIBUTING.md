# Contributing

## Coding Conventions

- Keep FastAPI routers thin.
- Put business logic in services.
- Use repositories for database access.
- Use async SQLAlchemy.
- Use Pydantic schemas for API boundaries.
- Keep provider-specific browser behavior behind provider implementations.
- Keep frontend API calls centralized in `frontend/src/api`.
- Keep TanStack Query hooks in `frontend/src/hooks`.
- Avoid unrelated refactors in feature PRs.

## Branch Naming

Use short branch names prefixed by scope:

```text
feature/<name>
fix/<name>
docs/<name>
chore/<name>
```

Codex-created branches may use `codex/<name>`.

## Commit Message Style

Use concise imperative messages:

```text
docs: add architecture documentation
fix: correct recommendation route
feature: add health evaluation page
```

## Pull Request Checklist

- [ ] Scope is limited to the stated task.
- [ ] Backend checks pass: `ruff check app alembic`.
- [ ] Python compile check passes: `python -m compileall app alembic`.
- [ ] Frontend build passes: `npm run build`.
- [ ] Alembic migration is included when schema changes.
- [ ] Runtime behavior is verified when relevant.
- [ ] Documentation is updated for public behavior changes.

