import { FormEvent, useState } from "react";
import { BookOpen, Layers, Plus, RefreshCw, Trash2 } from "lucide-react";

import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";
import { useBehaviorTemplates } from "../hooks/useBehaviorTemplates";
import { useCreateBehaviorTemplate, useDeleteBehaviorTemplate } from "../hooks/useBehaviorTemplates";
import { cn } from "../lib/utils";
import { useToast } from "../store/useToast";
import type { BehaviorTemplate } from "../types/behaviorTemplate";

export function BehaviorLibraryPage() {
  const templates = useBehaviorTemplates();
  const createTemplate = useCreateBehaviorTemplate();
  const deleteTemplate = useDeleteBehaviorTemplate();
  const { notify } = useToast();
  const [selectedTemplate, setSelectedTemplate] = useState<BehaviorTemplate | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    category: "Custom",
    workflowJson: JSON.stringify(
      [
        { action: "OPEN_URL" },
        { action: "WAIT", config: { min_seconds: 5, max_seconds: 12 } },
        { action: "SCROLL", config: { count: 3 } },
        { action: "UPVOTE" }
      ],
      null,
      2
    )
  });

  if (templates.isLoading) {
    return <StatePanel title="Loading behavior templates..." />;
  }

  if (templates.isError) {
    return <StatePanel title="Unable to load behavior templates." tone="error" />;
  }

  const items = templates.data ?? [];
  const activeTemplate = selectedTemplate ?? items[0] ?? null;

  function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    let workflow_json: Array<{ action: string; config?: Record<string, unknown> }>;
    try {
      const parsed = JSON.parse(form.workflowJson) as unknown;
      if (!Array.isArray(parsed)) {
        throw new Error("Workflow JSON must be an array.");
      }
      workflow_json = parsed.map((item) => {
        if (!isRecord(item) || typeof item.action !== "string") {
          throw new Error("Each workflow step requires an action.");
        }
        return {
          action: item.action,
          config: isRecord(item.config) ? item.config : undefined
        };
      });
    } catch (error) {
      notify(error instanceof Error ? error.message : "Workflow JSON is invalid.", "error");
      return;
    }

    createTemplate.mutate(
      {
        name: form.name.trim(),
        description: form.description.trim() || null,
        platform: "reddit",
        category: form.category.trim() || "Custom",
        workflow_json
      },
      {
        onSuccess: (template) => {
          notify("Behavior template created.", "success");
          setSelectedTemplate(template);
          setShowCreate(false);
          setForm((current) => ({ ...current, name: "", description: "" }));
        },
        onError: () => notify("Unable to create behavior template.", "error")
      }
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Behavior Library</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Reusable workflow templates for campaign behavior.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" onClick={() => templates.refetch()}>
            <RefreshCw size={16} className={templates.isFetching ? "animate-spin" : ""} />
            Refresh
          </Button>
          <Button type="button" onClick={() => setShowCreate((value) => !value)}>
            <Plus size={16} />
            New Template
          </Button>
        </div>
      </div>

      {showCreate ? (
        <form onSubmit={handleCreate} className="space-y-4 rounded-md border border-border bg-white p-5">
          <div className="grid gap-4 md:grid-cols-2">
            <Field label="Name">
              <Input
                required
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
              />
            </Field>
            <Field label="Category">
              <Input
                required
                value={form.category}
                onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))}
              />
            </Field>
          </div>
          <Field label="Description">
            <Input
              value={form.description}
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
            />
          </Field>
          <Field label="Workflow JSON">
            <Textarea
              value={form.workflowJson}
              onChange={(event) => setForm((current) => ({ ...current, workflowJson: event.target.value }))}
              className="min-h-56 font-mono"
            />
          </Field>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={createTemplate.isPending}>
              {createTemplate.isPending ? "Saving..." : "Save Template"}
            </Button>
            <Button type="button" variant="secondary" onClick={() => setShowCreate(false)}>
              Cancel
            </Button>
          </div>
        </form>
      ) : null}

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((template) => (
            <article
              key={template.id}
              className={cn(
                "rounded-md border bg-white transition hover:border-primary",
                activeTemplate?.id === template.id ? "border-primary" : "border-border"
              )}
            >
              <button
                type="button"
                onClick={() => setSelectedTemplate(template)}
                className="block w-full p-5 text-left"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h2 className="font-semibold">{template.name}</h2>
                    <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{template.description}</p>
                  </div>
                  {template.is_builtin ? (
                    <span className="rounded bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700">Built-in</span>
                  ) : null}
                </div>
                <div className="mt-4 flex flex-wrap gap-2 text-xs text-muted-foreground">
                  <span className="inline-flex items-center gap-1 rounded bg-muted px-2 py-1">
                    <Layers size={13} />
                    {template.category}
                  </span>
                  <span className="rounded bg-muted px-2 py-1">{template.workflow_json.length} steps</span>
                </div>
              </button>
              {!template.is_builtin ? (
                <div className="border-t border-border px-5 py-3">
                  <Button
                    type="button"
                    variant="danger"
                    className="h-8"
                    disabled={deleteTemplate.isPending}
                    onClick={() => {
                      deleteTemplate.mutate(template.id, {
                        onSuccess: () => {
                          notify("Behavior template deleted.", "success");
                          if (selectedTemplate?.id === template.id) {
                            setSelectedTemplate(null);
                          }
                        },
                        onError: () => notify("Unable to delete behavior template.", "error")
                      });
                    }}
                  >
                    <Trash2 size={14} />
                    Delete
                  </Button>
                </div>
              ) : null}
            </article>
          ))}
        </div>

        <aside className="rounded-md border border-border bg-white">
          <div className="flex items-center gap-2 border-b border-border px-4 py-3">
            <BookOpen size={16} className="text-muted-foreground" />
            <h2 className="text-sm font-semibold">Workflow Preview</h2>
          </div>
          {activeTemplate ? (
            <WorkflowPreview template={activeTemplate} />
          ) : (
            <div className="px-4 py-10 text-sm text-muted-foreground">No templates available.</div>
          )}
        </aside>
      </div>
    </div>
  );
}

function Field({ children, label }: { children: React.ReactNode; label: string }) {
  return (
    <label className="space-y-2 text-sm font-medium">
      <span>{label}</span>
      {children}
    </label>
  );
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function WorkflowPreview({ template }: { template: BehaviorTemplate }) {
  return (
    <div className="space-y-3 p-4">
      <div>
        <div className="font-semibold">{template.name}</div>
        <div className="text-sm text-muted-foreground">{template.category}</div>
      </div>
      <div className="space-y-2">
        {template.workflow_json.map((step, index) => (
          <div key={`${step.action}-${index}`} className="flex items-center gap-3 rounded-md border border-border px-3 py-2 text-sm">
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-muted text-xs font-semibold">
              {index + 1}
            </span>
            <span className="font-medium">{step.action}</span>
          </div>
        ))}
      </div>
    </div>
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
