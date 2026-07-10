# Browser Module

## Purpose

Provides the platform-neutral browser orchestration boundary.

## Responsibilities

- Resolve providers by `Account.platform`.
- Track active manual login sessions in memory.
- Delegate storage/profile location to providers.
- Open and close Playwright persistent contexts.

## Inputs

- `Account` ORM models.
- URLs for provider browser navigation.

## Outputs

- `BrowserSessionResult`.
- Provider-owned active browser sessions.

## Related APIs

Browser actions are exposed through account session APIs, not through BrowserManager directly.

## Related Database Tables

- `accounts`

## Related Services

- `BrowserManager`
- `ProviderManager`
- `Provider`
- `RedditProvider`

## Sequence Diagram

```text
Service
  -> BrowserManager
  -> ProviderManager.get_provider(account.platform)
  -> Provider method
  -> Playwright async API
  -> storage/reddit/<account>/
```

## Extension Guide

- Add provider classes under `backend/app/providers/<provider>/`.
- Provider methods should remain generic: `create_session`, `finish_session`, `validate_session`, `refresh_session`, `delete_session`, `open_url`.
- Do not expose provider-specific methods to routers.
