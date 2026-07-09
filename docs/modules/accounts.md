# Accounts Module

## Purpose

Stores managed social account records. The current platform enum supports Reddit only.

## Responsibilities

- Create, list, update, and delete accounts.
- Enforce unique `(platform, username)`.
- Store profile, session, and operational metadata.

## Inputs

- `AccountCreate`
- `AccountUpdate`
- Account UUID path parameters
- Optional account search string

## Outputs

- `AccountRead`
- Lists of `AccountRead`
- HTTP 204 on delete

## Related APIs

- `GET /api/v1/accounts`
- `POST /api/v1/accounts`
- `GET /api/v1/accounts/{account_id}`
- `PATCH /api/v1/accounts/{account_id}`
- `DELETE /api/v1/accounts/{account_id}`

## Related Database Tables

- `accounts`
- Dependent tables cascade from `accounts.id`

## Related Services

- `AccountService`
- `AccountRepository`

## Sequence Diagram

```text
Frontend
  -> Accounts API
  -> accounts router
  -> AccountService
  -> AccountRepository
  -> accounts table
```

## Extension Guide

- Add new provider values to `Platform`.
- Update account forms and filters.
- Keep provider-specific behavior out of account CRUD.

