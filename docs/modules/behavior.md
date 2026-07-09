# Behavior Module

## Purpose

Executes human-like workflow actions inside a persistent browser context.

## Responsibilities

- Start and close behavior browser sessions.
- Execute `OPEN_URL`, `WAIT`, `SCROLL`, `OPEN_POST`, and `BACK`.
- Return structured success/failure results to WorkflowService.

## Inputs

- `Account`
- Workflow step config JSON
- Current browser page context

## Outputs

- `BehaviorResult`
- Step details such as wait duration or opened post title.

## Related APIs

Behavior is executed through workflow and campaign APIs.

## Related Database Tables

- `workflow_steps`
- `campaigns`
- `campaign_accounts`

## Related Services

- `BehaviorService`
- `WorkflowService`
- `BrowserManager`

## Sequence Diagram

```text
WorkflowService
  -> BehaviorService.start
  -> BrowserManager.open_persistent_context
  -> BehaviorService.open_url / wait / scroll / open_post / back
  -> WorkflowStepResult
  -> BehaviorService.close
```

## Extension Guide

- Add new action enum values and migrations.
- Add behavior implementation to `BehaviorService`.
- Delegate from `WorkflowService._execute_step`.
- Keep Playwright details out of routers.

