export function ProgressMeter({
  label,
  value,
  tone = "brand",
}: {
  label: string;
  value: number;
  tone?: "brand" | "positive" | "warning" | "danger" | "neutral";
}) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div className="progress-meter">
      <div className="progress-meter__header">
        <span>{label}</span>
        <strong>{Math.round(clamped)}%</strong>
      </div>
      <div className="progress-meter__track">
        <span
          className={`progress-meter__fill progress-meter__fill--${tone}`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
