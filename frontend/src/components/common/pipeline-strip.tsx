import { cn } from "@/lib/utils";

import { pipelineStepIndexStyles, pipelineStepStyles } from "./ui";

export type PipelineStep = {
  label: string;
  description: string;
  state: "done" | "active" | "pending" | "warning";
};

export function PipelineStrip({
  steps,
  compact = false,
  className,
}: {
  steps: PipelineStep[];
  compact?: boolean;
  className?: string;
}) {
  return (
    <ol
      className={cn(
        "grid gap-3",
        compact ? "grid-cols-1" : "grid-cols-1 xl:grid-cols-2",
        className,
      )}
    >
      {steps.map((step, index) => (
        <li
          className={pipelineStepStyles(
            step.state,
            compact ? "grid-cols-[auto_minmax(0,1fr)] items-start" : "grid-cols-[auto_minmax(0,1fr)] items-start",
          )}
          key={`${step.label}-${index}`}
        >
          <span className={pipelineStepIndexStyles(step.state)}>{index + 1}</span>
          <div>
            <strong className="text-sm font-semibold">{step.label}</strong>
            <p className="mt-1 text-sm leading-6 opacity-80">{step.description}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
