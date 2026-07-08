import { useState } from "react";
import { BookOpen, Layers } from "lucide-react";

import { useBehaviorTemplates } from "../hooks/useBehaviorTemplates";
import { cn } from "../lib/utils";
import type { BehaviorTemplate } from "../types/behaviorTemplate";

export function BehaviorLibraryPage() {
  const templates = useBehaviorTemplates();
  const [selectedTemplate, setSelectedTemplate] = useState<BehaviorTemplate | null>(null);

  if (templates.isLoading) {
    return <StatePanel title="Loading behavior templates..." />;
  }

  if (templates.isError) {
    return <StatePanel title="Unable to load behavior templates." tone="error" />;
  }

  const items = templates.data ?? [];
  const activeTemplate = selectedTemplate ?? items[0] ?? null;

  return (
    <div className="space-y-5">
      <div className="border-b border-border pb-5">
        <h1 className="text-2xl font-semibold">Behavior Library</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Reusable workflow templates for campaign behavior.
        </p>
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_380px]">
        <div className="grid gap-4 md:grid-cols-2">
          {items.map((template) => (
            <button
              key={template.id}
              type="button"
              onClick={() => setSelectedTemplate(template)}
              className={cn(
                "rounded-md border bg-white p-5 text-left transition hover:border-primary",
                activeTemplate?.id === template.id ? "border-primary" : "border-border"
              )}
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
