import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  applyBehaviorTemplate,
  createBehaviorTemplate,
  deleteBehaviorTemplate,
  getBehaviorTemplate,
  listBehaviorTemplates
} from "../api/behaviorTemplates";
import type { BehaviorTemplateInput } from "../types/behaviorTemplate";

export function useBehaviorTemplates() {
  return useQuery({ queryKey: ["behavior-templates"], queryFn: listBehaviorTemplates });
}

export function useBehaviorTemplate(templateId: string) {
  return useQuery({
    queryKey: ["behavior-templates", templateId],
    queryFn: () => getBehaviorTemplate(templateId),
    enabled: Boolean(templateId)
  });
}

export function useCreateBehaviorTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: BehaviorTemplateInput) => createBehaviorTemplate(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["behavior-templates"] })
  });
}

export function useDeleteBehaviorTemplate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteBehaviorTemplate,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["behavior-templates"] })
  });
}

export function useApplyBehaviorTemplate(campaignId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (templateId: string) => applyBehaviorTemplate(campaignId, templateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns", campaignId, "workflow"] });
    }
  });
}
