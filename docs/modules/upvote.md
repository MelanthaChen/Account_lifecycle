# Upvote Module

## Purpose

Sequentially attempts Reddit upvotes for selected accounts.

## Responsibilities

- Validate Reddit target URLs at the API boundary.
- Execute accounts sequentially.
- Restore persisted storage state.
- Detect login-required state.
- Locate an upvote control with selector fallbacks.
- Click once and attempt verification.
- Return per-account results.

## Inputs

- `account_ids`
- `target_url`
- Account persistent profile and `storage_state.json`

## Outputs

- `UpvoteResponse`
- Per-account result objects.

## Related APIs

- `POST /api/v1/upvote`

## Related Database Tables

- `accounts`

## Related Services

- `UpvoteService`
- `BrowserManager`
- `AccountRepository`

## Sequence Diagram

```text
POST /upvote
  -> UpvoteService
  -> for each account
       -> open persistent context
       -> restore storage state
       -> navigate target
       -> detect login state
       -> find upvote button
       -> click once
       -> verify best effort
       -> close browser
```

## Extension Guide

- Keep selector fallbacks local to UpvoteService.
- Add activity integration only when intentionally scoped.
- Avoid parallel execution unless rate-limit handling is designed.

