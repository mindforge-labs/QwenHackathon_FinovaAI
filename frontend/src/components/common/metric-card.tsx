import { cn } from "@/lib/utils";

const toneStyles = {
  default: "border-black/10 bg-white/[0.82] text-[#0e0f0c]",
  neutral: "border-black/10 bg-white/[0.82] text-[#0e0f0c]",
  positive: "border-[#054d28]/15 bg-[#054d28]/[0.08] text-[#0e0f0c]",
  warning: "border-[#ffd11a]/30 bg-[#ffd11a]/[0.14] text-[#0e0f0c]",
  danger: "border-[#d03238]/[0.18] bg-[#d03238]/10 text-[#0e0f0c]",
} as const;

export function MetricCard({
  label,
  value,
  detail,
  tone = "default",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "default" | "positive" | "warning" | "danger" | "neutral";
}) {
  return (
    <article
      className={cn(
        "flex h-full flex-col justify-between gap-4 rounded-[30px] border p-5 shadow-[0_0_0_1px_rgba(14,15,12,0.04)] backdrop-blur-sm",
        toneStyles[tone],
      )}
    >
      <p className="text-[0.78rem] font-bold uppercase tracking-[0.14em] text-[#6c7268]">{label}</p>
      <strong className="[font-family:'Arial_Black',Impact,Inter,sans-serif] text-[clamp(2.4rem,4vw,3.5rem)] font-black leading-[0.88] tracking-[-0.06em]">
        {value}
      </strong>
      <p className="max-w-72 text-sm leading-6 text-[#454745]">{detail}</p>
    </article>
  );
}
