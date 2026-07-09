import { useEffect, useState } from "react";
import { ArrowDown, ArrowLeft, ArrowUp, Layers, Play, Plus, Save, Trash2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  useCampaign,
  useCampaignWorkflow,
  useReplaceCampaignWorkflow,
  useRunCampaignWorkflow
} from "../hooks/useCampaigns";
import { useApplyBehaviorTemplate, useBehaviorTemplates } from "../hooks/useBehaviorTemplates";
import {
  useCampaignSchedule,
  useDeleteCampaignSchedule,
  useRunCampaignScheduleNow,
  useSaveCampaignSchedule
} from "../hooks/useSchedules";
import { cn } from "../lib/utils";
import { useToast } from "../store/useToast";
import type { BehaviorTemplate } from "../types/behaviorTemplate";
import type { CampaignRunResponse, WorkflowActionType, WorkflowInputStep } from "../types/campaign";
import type { CampaignSchedule, ScheduleType } from "../types/schedule";

export function CampaignDetailPage() {
  const { campaignId = "" } = useParams();
  const campaign = useCampaign(campaignId);
  const workflow = useCampaignWorkflow(campaignId);
  const schedule = useCampaignSchedule(campaignId);
  const templates = useBehaviorTemplates();
  const replaceWorkflow = useReplaceCampaignWorkflow(campaignId);
  const applyTemplate = useApplyBehaviorTemplate(campaignId);
  const runWorkflow = useRunCampaignWorkflow(campaignId);
  const saveSchedule = useSaveCampaignSchedule(campaignId, Boolean(schedule.data));
  const deleteSchedule = useDeleteCampaignSchedule(campaignId);
  const runScheduleNow = useRunCampaignScheduleNow(campaignId);
  const { notify } = useToast();
  const [steps, setSteps] = useState<WorkflowInputStep[]>([]);
  const [lastRun, setLastRun] = useState<CampaignRunResponse | null>(null);
  const [templatePanelOpen, setTemplatePanelOpen] = useState(false);
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [scheduleEnabled, setScheduleEnabled] = useState(true);
  const [scheduleType, setScheduleType] = useState<ScheduleType>("DAILY");
  const [scheduleTime, setScheduleTime] = useState("09:00");
  const [scheduleTimezone, setScheduleTimezone] = useState(defaultTimezone());
  const [scheduleCron, setScheduleCron] = useState("0 9 * * *");
  const [scheduleRunAt, setScheduleRunAt] = useState("");

  useEffect(() => {
    if (workflow.data) {
      setSteps(
        workflow.data.steps.map((step) => ({
          action_type: step.action_type,
          config: step.config
        }))
      );
    }
  }, [workflow.data]);

  useEffect(() => {
    if (!schedule.data) {
      return;
    }
    setScheduleEnabled(schedule.data.enabled);
    setScheduleType(schedule.data.schedule_type);
    setScheduleTimezone(schedule.data.timezone);
    setScheduleCron(schedule.data.cron_expression ?? "0 9 * * *");
    setScheduleRunAt(schedule.data.next_run_at ? toDateTimeLocal(schedule.data.next_run_at) : "");
    const parsedTime = timeFromCron(schedule.data.cron_expression);
    if (parsedTime) {
      setScheduleTime(parsedTime);
    }
  }, [schedule.data]);

  function addStep() {
    setSteps((current) => [...current, { action_type: "WAIT", config: { min_seconds: 5, max_seconds: 12 } }]);
  }

  function deleteStep(index: number) {
    setSteps((current) => current.filter((_, itemIndex) => itemIndex !== index));
  }

  function moveStep(index: number, direction: -1 | 1) {
    setSteps((current) => {
      const next = [...current];
      const target = index + direction;
      if (target < 0 || target >= next.length) {
        return current;
      }
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  }

  function updateStep(index: number, actionType: WorkflowActionType) {
    setSteps((current) =>
      current.map((step, itemIndex) =>
        itemIndex === index
          ? {
              action_type: actionType,
              config: defaultConfig(actionType, campaign.data?.target_url ?? "")
            }
          : step
      )
    );
  }

  function updateStepUrl(index: number, targetUrl: string) {
    setSteps((current) =>
      current.map((step, itemIndex) =>
        itemIndex === index ? { ...step, config: { ...step.config, target_url: targetUrl } } : step
      )
    );
  }

  function updateStepNumber(index: number, key: string, value: string) {
    const parsedValue = Number(value);
    setSteps((current) =>
      current.map((step, itemIndex) =>
        itemIndex === index
          ? { ...step, config: { ...step.config, [key]: Number.isNaN(parsedValue) ? 0 : parsedValue } }
          : step
      )
    );
  }

  function saveWorkflow() {
    replaceWorkflow.mutate(
      { steps },
      {
        onSuccess: () => notify("Workflow saved.", "success"),
        onError: () => notify("Unable to save workflow.", "error")
      }
    );
  }

  function run() {
    setLastRun(null);
    runWorkflow.mutate(undefined, {
      onSuccess: (response) => {
        setLastRun(response);
        notify(response.success ? "Workflow completed." : "Workflow finished with failures.", response.success ? "success" : "error");
      },
      onError: () => notify("Unable to run workflow.", "error")
    });
  }

  function applySelectedTemplate() {
    if (!selectedTemplateId) {
      notify("Choose a template first.", "error");
      return;
    }
    applyTemplate.mutate(selectedTemplateId, {
      onSuccess: (response) => {
        setSteps(
          response.steps.map((step) => ({
            action_type: step.action_type,
            config: step.config
          }))
        );
        notify("Template applied.", "success");
        setTemplatePanelOpen(false);
      },
      onError: () => notify("Unable to apply template.", "error")
    });
  }

  function saveCampaignSchedule() {
    const input = scheduleInput({
      enabled: scheduleEnabled,
      scheduleType,
      scheduleTime,
      timezone: scheduleTimezone,
      cron: scheduleCron,
      runAt: scheduleRunAt
    });
    saveSchedule.mutate(input, {
      onSuccess: () => notify("Schedule saved.", "success"),
      onError: () => notify("Unable to save schedule.", "error")
    });
  }

  function disableCampaignSchedule() {
    if (!schedule.data) {
      return;
    }
    deleteSchedule.mutate(undefined, {
      onSuccess: () => notify("Schedule disabled.", "success"),
      onError: () => notify("Unable to disable schedule.", "error")
    });
  }

  function runNow() {
    setLastRun(null);
    runScheduleNow.mutate(undefined, {
      onSuccess: (response) => {
        setLastRun(response);
        notify(response.success ? "Scheduled run completed." : "Scheduled run finished with failures.", response.success ? "success" : "error");
      },
      onError: () => notify("Unable to run schedule.", "error")
    });
  }

  if (campaign.isLoading || workflow.isLoading) {
    return <StatePanel title="Loading campaign..." />;
  }

  if (campaign.isError || workflow.isError || !campaign.data) {
    return <StatePanel title="Unable to load campaign." tone="error" />;
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-4 border-b border-border pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <Link to="/campaigns" className="mb-3 inline-flex items-center gap-2 text-sm text-muted-foreground">
            <ArrowLeft size={15} />
            Campaigns
          </Link>
          <h1 className="text-2xl font-semibold">{campaign.data.name}</h1>
          <p className="mt-1 break-all text-sm text-muted-foreground">{campaign.data.target_url}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" onClick={addStep}>
            <Plus size={16} />
            Add Step
          </Button>
          <Button type="button" variant="secondary" onClick={() => setTemplatePanelOpen((value) => !value)}>
            <Layers size={16} />
            Apply Template
          </Button>
          <Button type="button" variant="secondary" onClick={saveWorkflow} disabled={replaceWorkflow.isPending || steps.length === 0}>
            <Save size={16} />
            Save
          </Button>
          <Button type="button" onClick={run} disabled={runWorkflow.isPending || steps.length === 0}>
            <Play size={16} />
            {runWorkflow.isPending ? "Running..." : "Run Workflow"}
          </Button>
        </div>
      </div>

      {templatePanelOpen ? (
        <TemplateChooser
          templates={templates.data ?? []}
          selectedTemplateId={selectedTemplateId}
          isLoading={templates.isLoading}
          isPending={applyTemplate.isPending}
          onSelect={setSelectedTemplateId}
          onApply={applySelectedTemplate}
        />
      ) : null}

      <section className="rounded-md border border-border bg-white">
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-sm font-semibold">Workflow</h2>
        </div>
        <div className="divide-y divide-border">
          {steps.map((step, index) => (
            <div key={`${step.action_type}-${index}`} className="grid gap-4 px-4 py-4 lg:grid-cols-[48px_minmax(0,1fr)_auto] lg:items-start">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-sm font-semibold">
                {index + 1}
              </div>
              <div className="grid gap-3 md:grid-cols-[220px_minmax(0,1fr)]">
                <select
                  value={step.action_type}
                  onChange={(event) => updateStep(index, event.target.value as WorkflowActionType)}
                  className="flex h-10 w-full rounded-md border border-input bg-white px-3 text-sm outline-none"
                >
                  <option value="OPEN_URL">OPEN_URL</option>
                  <option value="WAIT">WAIT</option>
                  <option value="SCROLL">SCROLL</option>
                  <option value="OPEN_POST">OPEN_POST</option>
                  <option value="BACK">BACK</option>
                  <option value="UPVOTE">UPVOTE</option>
                </select>
                <StepConfigFields
                  step={step}
                  campaignTargetUrl={campaign.data.target_url}
                  onUrlChange={(value) => updateStepUrl(index, value)}
                  onNumberChange={(key, value) => updateStepNumber(index, key, value)}
                />
              </div>
              <div className="flex flex-wrap gap-2">
                <IconButton label="Move Up" disabled={index === 0} onClick={() => moveStep(index, -1)}>
                  <ArrowUp size={15} />
                </IconButton>
                <IconButton label="Move Down" disabled={index === steps.length - 1} onClick={() => moveStep(index, 1)}>
                  <ArrowDown size={15} />
                </IconButton>
                <IconButton label="Delete Step" onClick={() => deleteStep(index)}>
                  <Trash2 size={15} />
                </IconButton>
              </div>
            </div>
          ))}
        </div>
      </section>

      <SchedulePanel
        schedule={schedule.data ?? null}
        enabled={scheduleEnabled}
        scheduleType={scheduleType}
        time={scheduleTime}
        timezone={scheduleTimezone}
        cron={scheduleCron}
        runAt={scheduleRunAt}
        isLoading={schedule.isLoading}
        isSaving={saveSchedule.isPending}
        isDeleting={deleteSchedule.isPending}
        isRunning={runScheduleNow.isPending}
        onEnabledChange={setScheduleEnabled}
        onScheduleTypeChange={setScheduleType}
        onTimeChange={setScheduleTime}
        onTimezoneChange={setScheduleTimezone}
        onCronChange={setScheduleCron}
        onRunAtChange={setScheduleRunAt}
        onSave={saveCampaignSchedule}
        onDisable={disableCampaignSchedule}
        onRunNow={runNow}
      />

      {lastRun ? <WorkflowRunPanel run={lastRun} /> : null}
    </div>
  );
}

function SchedulePanel({
  schedule,
  enabled,
  scheduleType,
  time,
  timezone,
  cron,
  runAt,
  isLoading,
  isSaving,
  isDeleting,
  isRunning,
  onEnabledChange,
  onScheduleTypeChange,
  onTimeChange,
  onTimezoneChange,
  onCronChange,
  onRunAtChange,
  onSave,
  onDisable,
  onRunNow
}: {
  schedule: CampaignSchedule | null;
  enabled: boolean;
  scheduleType: ScheduleType;
  time: string;
  timezone: string;
  cron: string;
  runAt: string;
  isLoading: boolean;
  isSaving: boolean;
  isDeleting: boolean;
  isRunning: boolean;
  onEnabledChange: (value: boolean) => void;
  onScheduleTypeChange: (value: ScheduleType) => void;
  onTimeChange: (value: string) => void;
  onTimezoneChange: (value: string) => void;
  onCronChange: (value: string) => void;
  onRunAtChange: (value: string) => void;
  onSave: () => void;
  onDisable: () => void;
  onRunNow: () => void;
}) {
  return (
    <section className="rounded-md border border-border bg-white p-5">
      <div className="flex flex-col gap-3 border-b border-border pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-base font-semibold">Schedule</h2>
          <p className="mt-1 text-sm text-muted-foreground">Automatically run this campaign through the Scheduler Engine.</p>
        </div>
        <div className="text-sm text-muted-foreground">
          {schedule?.next_run_at ? `Next: ${formatDate(schedule.next_run_at)}` : "No upcoming run"}
        </div>
      </div>

      {isLoading ? (
        <div className="py-6 text-sm text-muted-foreground">Loading schedule...</div>
      ) : (
        <div className="mt-4 grid gap-4 lg:grid-cols-[160px_180px_180px_minmax(0,1fr)]">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(event) => onEnabledChange(event.target.checked)}
              className="h-4 w-4 rounded border-border"
            />
            Enabled
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-muted-foreground">Schedule Type</span>
            <select
              value={scheduleType}
              onChange={(event) => onScheduleTypeChange(event.target.value as ScheduleType)}
              className="flex h-10 w-full rounded-md border border-input bg-white px-3 text-sm outline-none"
            >
              <option value="ONCE">ONCE</option>
              <option value="DAILY">DAILY</option>
              <option value="WEEKLY">WEEKLY</option>
              <option value="CUSTOM_CRON">CUSTOM_CRON</option>
            </select>
          </label>
          <label className="space-y-1">
            <span className="text-xs font-medium text-muted-foreground">Timezone</span>
            <Input value={timezone} onChange={(event) => onTimezoneChange(event.target.value)} />
          </label>
          {scheduleType === "ONCE" ? (
            <label className="space-y-1">
              <span className="text-xs font-medium text-muted-foreground">Run At</span>
              <Input type="datetime-local" value={runAt} onChange={(event) => onRunAtChange(event.target.value)} />
            </label>
          ) : scheduleType === "CUSTOM_CRON" ? (
            <label className="space-y-1">
              <span className="text-xs font-medium text-muted-foreground">Cron</span>
              <Input value={cron} onChange={(event) => onCronChange(event.target.value)} placeholder="0 9 * * *" />
            </label>
          ) : (
            <label className="space-y-1">
              <span className="text-xs font-medium text-muted-foreground">Time</span>
              <Input type="time" value={time} onChange={(event) => onTimeChange(event.target.value)} />
            </label>
          )}
        </div>
      )}

      <div className="mt-4 flex flex-wrap gap-2">
        <Button type="button" onClick={onSave} disabled={isSaving}>
          <Save size={16} />
          {isSaving ? "Saving..." : "Save Schedule"}
        </Button>
        <Button type="button" variant="secondary" onClick={onRunNow} disabled={!schedule || isRunning}>
          <Play size={16} />
          {isRunning ? "Running..." : "Run Now"}
        </Button>
        <Button type="button" variant="secondary" onClick={onDisable} disabled={!schedule || isDeleting}>
          <Trash2 size={16} />
          {isDeleting ? "Disabling..." : "Disable Schedule"}
        </Button>
      </div>

      {schedule?.last_status ? (
        <div className="mt-3 text-sm text-muted-foreground">
          Last status: {schedule.last_status}
          {schedule.last_run_at ? ` · ${formatDate(schedule.last_run_at)}` : ""}
        </div>
      ) : null}
    </section>
  );
}

function TemplateChooser({
  templates,
  selectedTemplateId,
  isLoading,
  isPending,
  onSelect,
  onApply
}: {
  templates: BehaviorTemplate[];
  selectedTemplateId: string;
  isLoading: boolean;
  isPending: boolean;
  onSelect: (templateId: string) => void;
  onApply: () => void;
}) {
  const selectedTemplate = templates.find((template) => template.id === selectedTemplateId) ?? templates[0] ?? null;

  useEffect(() => {
    if (!selectedTemplateId && templates[0]) {
      onSelect(templates[0].id);
    }
  }, [onSelect, selectedTemplateId, templates]);

  return (
    <section className="grid gap-4 rounded-md border border-border bg-white p-5 lg:grid-cols-[minmax(0,1fr)_360px]">
      <div className="space-y-3">
        <h2 className="text-sm font-semibold">Choose Template</h2>
        {isLoading ? (
          <div className="text-sm text-muted-foreground">Loading templates...</div>
        ) : (
          <div className="grid gap-2">
            {templates.map((template) => (
              <button
                key={template.id}
                type="button"
                onClick={() => onSelect(template.id)}
                className={cn(
                  "rounded-md border px-3 py-2 text-left text-sm transition hover:border-primary",
                  selectedTemplate?.id === template.id ? "border-primary" : "border-border"
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{template.name}</span>
                  {template.is_builtin ? <span className="text-xs text-blue-700">Built-in</span> : null}
                </div>
                <div className="mt-1 text-xs text-muted-foreground">
                  {template.category} · {template.workflow_json.length} steps
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="space-y-4">
        <h2 className="text-sm font-semibold">Preview</h2>
        {selectedTemplate ? (
          <div className="space-y-2">
            {selectedTemplate.workflow_json.map((step, index) => (
              <div key={`${step.action}-${index}`} className="flex items-center gap-3 rounded-md border border-border px-3 py-2 text-sm">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-muted text-xs font-semibold">
                  {index + 1}
                </span>
                <span>{step.action}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">No template selected.</div>
        )}
        <Button type="button" onClick={onApply} disabled={!selectedTemplate || isPending}>
          {isPending ? "Applying..." : "Apply"}
        </Button>
      </div>
    </section>
  );
}

function IconButton({
  label,
  disabled,
  onClick,
  children
}: {
  label: string;
  disabled?: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      disabled={disabled}
      onClick={onClick}
      className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-white text-muted-foreground transition hover:bg-muted disabled:pointer-events-none disabled:opacity-40"
    >
      {children}
    </button>
  );
}

function WorkflowRunPanel({ run }: { run: CampaignRunResponse }) {
  return (
    <section className="rounded-md border border-border bg-white p-5">
      <h2 className="text-base font-semibold">Execution Log</h2>
      <div className="mt-4 divide-y divide-border">
        {run.results.map((accountResult) => (
          <div key={accountResult.account} className="py-4">
            <div className="font-medium">{accountResult.account}</div>
            <div className="mt-3 space-y-2">
              {accountResult.steps.map((step, index) => (
                <div key={`${accountResult.account}-${step.action_type}-${index}`} className="flex items-center justify-between gap-4 text-sm">
                  <span>{step.action_type}</span>
                  <span className={cn(step.success ? "text-emerald-700" : "text-red-700")}>
                    {step.success
                      ? step.detail
                        ? `Success · ${step.detail}`
                        : "Success"
                      : formatReason(step.reason ?? "failed")}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function StepConfigFields({
  step,
  campaignTargetUrl,
  onUrlChange,
  onNumberChange
}: {
  step: WorkflowInputStep;
  campaignTargetUrl: string;
  onUrlChange: (value: string) => void;
  onNumberChange: (key: string, value: string) => void;
}) {
  if (step.action_type === "OPEN_URL") {
    return (
      <Input
        value={String(step.config.target_url ?? campaignTargetUrl)}
        onChange={(event) => onUrlChange(event.target.value)}
      />
    );
  }

  if (step.action_type === "WAIT") {
    return (
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="space-y-1">
          <span className="text-xs font-medium text-muted-foreground">Minimum Seconds</span>
          <Input
            type="number"
            min={0}
            value={String(step.config.min_seconds ?? 5)}
            onChange={(event) => onNumberChange("min_seconds", event.target.value)}
          />
        </label>
        <label className="space-y-1">
          <span className="text-xs font-medium text-muted-foreground">Maximum Seconds</span>
          <Input
            type="number"
            min={0}
            value={String(step.config.max_seconds ?? 12)}
            onChange={(event) => onNumberChange("max_seconds", event.target.value)}
          />
        </label>
      </div>
    );
  }

  if (step.action_type === "SCROLL") {
    return (
      <label className="space-y-1">
        <span className="text-xs font-medium text-muted-foreground">Scroll Count</span>
        <Input
          type="number"
          min={1}
          value={String(step.config.count ?? 3)}
          onChange={(event) => onNumberChange("count", event.target.value)}
        />
      </label>
    );
  }

  const labels: Record<WorkflowActionType, string> = {
    OPEN_URL: "",
    WAIT: "",
    SCROLL: "",
    OPEN_POST: "Randomly opens one visible post.",
    BACK: "Returns to the previous page.",
    UPVOTE: "Uses campaign target URL."
  };
  return (
    <div className="flex h-10 items-center rounded-md border border-border bg-muted px-3 text-sm text-muted-foreground">
      {labels[step.action_type]}
    </div>
  );
}

function defaultConfig(actionType: WorkflowActionType, targetUrl: string): Record<string, unknown> {
  if (actionType === "OPEN_URL") {
    return { target_url: targetUrl };
  }
  if (actionType === "WAIT") {
    return { min_seconds: 5, max_seconds: 12 };
  }
  if (actionType === "SCROLL") {
    return { count: 3 };
  }
  if (actionType === "OPEN_POST") {
    return { strategy: "random" };
  }
  return {};
}

function scheduleInput({
  enabled,
  scheduleType,
  scheduleTime,
  timezone,
  cron,
  runAt
}: {
  enabled: boolean;
  scheduleType: ScheduleType;
  scheduleTime: string;
  timezone: string;
  cron: string;
  runAt: string;
}) {
  return {
    enabled,
    schedule_type: scheduleType,
    cron_expression: scheduleType === "CUSTOM_CRON" ? cron : recurringCron(scheduleType, scheduleTime),
    timezone,
    next_run_at: scheduleType === "ONCE" && runAt ? new Date(runAt).toISOString() : null
  };
}

function recurringCron(scheduleType: ScheduleType, time: string) {
  if (scheduleType === "ONCE") {
    return null;
  }
  const [hour = "9", minute = "0"] = time.split(":");
  if (scheduleType === "WEEKLY") {
    return `${Number(minute)} ${Number(hour)} * * 1`;
  }
  return `${Number(minute)} ${Number(hour)} * * *`;
}

function timeFromCron(value: string | null) {
  if (!value) {
    return null;
  }
  const parts = value.trim().split(/\s+/);
  if (parts.length < 2) {
    return null;
  }
  const minute = parts[0].padStart(2, "0");
  const hour = parts[1].padStart(2, "0");
  return `${hour}:${minute}`;
}

function defaultTimezone() {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
}

function toDateTimeLocal(value: string) {
  const date = new Date(value);
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function StatePanel({ title, tone = "default" }: { title: string; tone?: "default" | "error" }) {
  return (
    <div
      className={
        tone === "error"
          ? "rounded-md border border-red-200 bg-red-50 px-4 py-12 text-center text-sm text-red-700"
          : "rounded-md border border-border bg-white px-4 py-12 text-center text-sm text-muted-foreground"
      }
    >
      {title}
    </div>
  );
}

function formatReason(reason: string) {
  const labels: Record<string, string> = {
    login_required: "Login Required",
    button_not_found: "Button Not Found",
    click_failed: "Click Failed",
    verification_failed: "Verification Failed",
    navigation_failed: "Navigation Failed",
    account_not_found: "Account Not Found",
    post_not_found: "Post Not Found",
    browser_unavailable: "Browser Unavailable"
  };
  return labels[reason] ?? reason;
}
