import { api } from "./client";
import type { Activity, ActivityFilters } from "../types/activity";

function buildParams(filters: ActivityFilters = {}) {
  return {
    limit: filters.limit,
    offset: filters.offset,
    activity_type: filters.activity_type,
    status: filters.status
  };
}

export async function listActivities(filters: ActivityFilters = {}) {
  const url = filters.accountId ? `/accounts/${filters.accountId}/activities` : "/activities";
  const response = await api.get<Activity[]>(url, { params: buildParams(filters) });
  return response.data;
}

export async function getActivity(activityId: string) {
  const response = await api.get<Activity>(`/activities/${activityId}`);
  return response.data;
}

export async function deleteActivity(activityId: string) {
  await api.delete(`/activities/${activityId}`);
}

export async function createTestActivity(accountId?: string) {
  const url = accountId ? `/accounts/${accountId}/activities/test` : "/activities/test";
  const response = await api.post<Activity>(url);
  return response.data;
}
