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
    <ol className={["pipeline-strip", compact ? "pipeline-strip--compact" : "", className].filter(Boolean).join(" ")}>
      {steps.map((step, index) => (
        <li className={`pipeline-step pipeline-step--${step.state}`} key={`${step.label}-${index}`}>
          <span className="pipeline-step__index">{index + 1}</span>
          <div>
            <strong>{step.label}</strong>
            <p>{step.description}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
