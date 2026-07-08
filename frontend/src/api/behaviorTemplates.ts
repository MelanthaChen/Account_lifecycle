import { api } from "./client";
import type { Workflow } from "../types/campaign";
import type { BehaviorTemplate, BehaviorTemplateInput } from "../types/behaviorTemplate";

export async function listBehaviorTemplates(): Promise<BehaviorTemplate[]> {
  const response = await api.get<BehaviorTemplate[]>("/behavior-templates");
  return response.data;
}

export async function getBehaviorTemplate(templateId: string): Promise<BehaviorTemplate> {
  const response = await api.get<BehaviorTemplate>(`/behavior-templates/${templateId}`);
  return response.data;
}

export async function createBehaviorTemplate(input: BehaviorTemplateInput): Promise<BehaviorTemplate> {
  const response = await api.post<BehaviorTemplate>("/behavior-templates", input);
  return response.data;
}

export async function deleteBehaviorTemplate(templateId: string): Promise<void> {
  await api.delete(`/behavior-templates/${templateId}`);
}

export async function applyBehaviorTemplate(campaignId: string, templateId: string): Promise<Workflow> {
  const response = await api.post<Workflow>(`/campaigns/${campaignId}/apply-template`, {
    template_id: templateId
  });
  return response.data;
}
