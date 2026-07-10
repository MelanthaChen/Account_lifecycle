# Sessions Module

## Purpose

Manages account browser session lifecycle and persists login state.

## Responsibilities

- Start manual login sessions.
- Finish sessions and persist `storage_state.json`.
- Validate and refresh sessions.
- Delete session storage.
- Open browser profiles.
- Record related activity rows.

## Inputs

- Account UUID path parameters.
- Existing account `platform`, `storage_directory`, and `browser_profile_path`.

## Outputs

- Updated `AccountRead`.
- Session activity records.

## Related APIs

- `POST /api/v1/accounts/{account_id}/session/create`
- `POST /api/v1/accounts/{account_id}/session/finish`
- `POST /api/v1/accounts/{account_id}/session/validate`
- `POST /api/v1/accounts/{account_id}/session/refresh`
- `DELETE /api/v1/accounts/{account_id}/session`
- `POST /api/v1/accounts/{account_id}/browser/open`
- `POST /api/v1/accounts/{account_id}/browser/open-home`

## Related Database Tables

- `accounts`
- `activities`

## Related Services

- `BrowserSessionService`
- `BrowserManager`
- `ProviderManager`
- `RedditProvider`
- `ActivityService`

## Sequence Diagram

```text
Create Session
  -> BrowserSessionService
  -> ActivityService RUNNING
  -> BrowserManager
  -> ProviderManager
  -> RedditProvider
  -> launch persistent context
  -> open Reddit login
  -> ActivityService SUCCESS
  -> update accounts.session_status
```

## Extension Guide

- Implement `Provider` for the new platform.
- Register it in `ProviderManager`.
- Keep provider-specific URLs inside the provider.
