import { useEffect, useState } from "react";
import { ArrowDown, ArrowLeft, ArrowUp, Play, Plus, Save, Trash2 } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  useCampaign,
  useCampaignWorkflow,
  useReplaceCampaignWorkflow,
  useRunCampaignWorkflow
} from "../hooks/useCampaigns";
import { cn } from "../lib/utils";
import { useToast } from "../store/useToast";
import type { CampaignRunResponse, WorkflowActionType, WorkflowInputStep } from "../types/campaign";

export function CampaignDetailPage() {
  const { campaignId = "" } = useParams();
  const campaign = useCampaign(campaignId);
  const workflow = useCampaignWorkflow(campaignId);
  const replaceWorkflow = useReplaceCampaignWorkflow(campaignId);
  const runWorkflow = useRunCampaignWorkflow(campaignId);
  const { notify } = useToast();
  const [steps, setSteps] = useState<WorkflowInputStep[]>([]);
  const [lastRun, setLastRun] = useState<CampaignRunResponse | null>(null);

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

  function addStep() {
    setSteps((current) => [...current, { action_type: "UPVOTE", config: {} }]);
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
              config: actionType === "OPEN_URL" ? { target_url: campaign.data?.target_url ?? "" } : {}
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
                  <option value="UPVOTE">UPVOTE</option>
                </select>
                {step.action_type === "OPEN_URL" ? (
                  <Input
                    value={String(step.config.target_url ?? campaign.data.target_url)}
                    onChange={(event) => updateStepUrl(index, event.target.value)}
                  />
                ) : (
                  <div className="flex h-10 items-center rounded-md border border-border bg-muted px-3 text-sm text-muted-foreground">
                    Uses campaign target URL.
                  </div>
                )}
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

      {lastRun ? <WorkflowRunPanel run={lastRun} /> : null}
    </div>
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
                    {step.success ? "Success" : formatReason(step.reason ?? "failed")}
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
    account_not_found: "Account Not Found"
  };
  return labels[reason] ?? reason;
}
