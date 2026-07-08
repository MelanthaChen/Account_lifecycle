import type { WorkflowInputStep } from "./campaign";

export interface BehaviorTemplate {
  id: string;
  name: string;
  description: string | null;
  platform: "reddit";
  category: string;
  workflow_json: Array<{ action: string; config?: Record<string, unknown> }>;
  is_builtin: boolean;
  created_at: string;
  updated_at: string;
}

export interface BehaviorTemplateInput {
  name: string;
  description?: string | null;
  platform: "reddit";
  category: string;
  workflow_json: Array<{ action: string; config?: Record<string, unknown> }>;
}

export function templateStepsToWorkflowInput(template: BehaviorTemplate): WorkflowInputStep[] {
  return template.workflow_json.map((step) => ({
    action_type: step.action as WorkflowInputStep["action_type"],
    config: step.config ?? {}
  }));
}
