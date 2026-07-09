# Behavior Library Module

## Purpose

Stores reusable workflow templates.

## Responsibilities

- List built-in and custom templates.
- Validate template workflow JSON.
- Create custom templates.
- Delete custom templates.
- Apply templates to campaign workflows.

## Inputs

- `BehaviorTemplateCreate`
- `template_id`
- `campaign_id`

## Outputs

- `BehaviorTemplateRead`
- `WorkflowRead` when applying a template.

## Related APIs

- `GET /api/v1/behavior-templates`
- `GET /api/v1/behavior-templates/{template_id}`
- `POST /api/v1/behavior-templates`
- `DELETE /api/v1/behavior-templates/{template_id}`
- `POST /api/v1/campaigns/{campaign_id}/apply-template`

## Related Database Tables

- `behavior_templates`
- `workflow_steps`

## Related Services

- `BehaviorTemplateService`
- `BehaviorTemplateRepository`
- `WorkflowService`

## Sequence Diagram

```text
Apply Template
  -> BehaviorTemplateService.get_template
  -> parse workflow_json
  -> WorkflowService.replace_workflow
  -> workflow_steps table
```

## Extension Guide

- Add built-in templates through migrations.
- Use `action` plus optional `config`.
- Keep template execution out of this module.

