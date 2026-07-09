# Workflow Module

## Purpose

Stores and executes ordered campaign steps.

## Responsibilities

- Get, create, and replace workflow steps.
- Run steps sequentially per account.
- Stop a single account workflow after first failed step.
- Update campaign status after execution.

## Inputs

- `WorkflowWrite`
- `campaign_id`
- Stored campaign account assignments

## Outputs

- `WorkflowRead`
- `WorkflowRunResponse`

## Related APIs

- `GET /api/v1/campaigns/{campaign_id}/workflow`
- `POST /api/v1/campaigns/{campaign_id}/workflow`
- `PUT /api/v1/campaigns/{campaign_id}/workflow`
- `POST /api/v1/campaigns/{campaign_id}/workflow/run`

## Related Database Tables

- `workflow_steps`
- `campaigns`
- `campaign_accounts`

## Related Services

- `WorkflowService`
- `BehaviorService`
- `UpvoteService`

## Sequence Diagram

```text
Run Workflow
  -> load campaign
  -> load account order
  -> load workflow steps
  -> for each account
       -> execute steps in order
       -> delegate behavior/upvote steps
  -> set campaign Completed or Failed
```

## Extension Guide

- Add actions to `WorkflowActionType`.
- Add migrations for enum values.
- Extend frontend workflow editor.
- Delegate action execution to focused services.

