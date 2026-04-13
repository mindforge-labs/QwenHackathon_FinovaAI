import { progressFillStyles } from "./ui";

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
    <div className="grid gap-2">
      <div className="flex items-center justify-between gap-4 text-sm">
        <span className="text-[#454745]">{label}</span>
        <strong className="font-semibold text-[#0e0f0c]">{Math.round(clamped)}%</strong>
      </div>
      <div className="relative h-2.5 overflow-hidden rounded-full bg-black/[0.08]">
        <span
          className={progressFillStyles(tone)}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
