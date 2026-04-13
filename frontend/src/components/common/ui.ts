import { DocumentStatus } from "@/lib/types";
import { cn } from "@/lib/utils";

export const pageContainer = "mx-auto w-[min(1440px,calc(100vw-32px))]";
export const appShell =
  "relative min-h-screen pb-10 before:pointer-events-none before:fixed before:right-[-120px] before:top-[10%] before:-z-10 before:h-80 before:w-80 before:rounded-full before:bg-[#9fe870]/15 before:blur-3xl before:content-[''] after:pointer-events-none after:fixed after:bottom-[8%] after:left-[-80px] after:-z-10 after:h-60 after:w-60 after:rounded-full after:bg-[#ffc091]/15 after:blur-3xl after:content-['']";
export const pageGrid = "grid gap-7";
export const eyebrow =
  "text-[0.72rem] font-bold uppercase tracking-[0.14em] text-[#6c7268]";
export const inverseEyebrow =
  "text-[0.72rem] font-bold uppercase tracking-[0.14em] text-white/65";
export const displayFont =
  "[font-family:'Arial_Black',Impact,Inter,sans-serif] font-black tracking-[-0.06em] leading-[0.88]";
export const label =
  "grid gap-2 text-[0.96rem] font-semibold text-[#0e0f0c]";
export const input =
  "w-full rounded-[18px] border border-black/[0.12] bg-white/95 px-4 py-3 text-sm text-[#0e0f0c] outline-none transition duration-200 placeholder:text-[#6c7268] focus:border-[#163300]/30 focus:shadow-[inset_0_0_0_1px_rgba(22,51,0,0.22)] disabled:cursor-not-allowed disabled:opacity-60";
export const textarea = cn(input, "min-h-28 resize-y");
export const sectionCard =
  "rounded-[40px] border border-black/[0.12] bg-white/[0.88] p-6 shadow-[0_0_0_1px_rgba(14,15,12,0.04)] backdrop-blur-sm md:p-8";
export const sectionCardDark =
  "rounded-[40px] border border-white/10 bg-[#0f160c] p-6 text-[#ecf3e2] shadow-[0_24px_60px_rgba(8,17,10,0.28)] md:p-8";
export const feedbackError =
  "rounded-[20px] border border-[#d03238]/20 bg-[#d03238]/10 px-4 py-3 text-sm font-medium text-[#8b1e24]";
export const emptyState =
  "rounded-[24px] border border-dashed border-black/10 bg-black/[0.03] px-5 py-6 text-sm text-[#454745]";

const buttonBase =
  "inline-flex items-center justify-center rounded-full px-5 py-3 text-sm font-semibold tracking-[-0.01em] transition duration-200 disabled:cursor-not-allowed disabled:opacity-60";
const buttonVariants = {
  primary:
    "bg-[#9fe870] text-[#163300] hover:scale-[1.03] hover:bg-[#b7f58f] active:scale-[0.98]",
  secondary:
    "bg-[#163300]/[0.08] text-[#0e0f0c] hover:scale-[1.03] hover:bg-[#d3f2c0] active:scale-[0.98]",
  success:
    "bg-[#054d28] text-white hover:scale-[1.03] hover:bg-[#0a6f3c] active:scale-[0.98]",
  danger:
    "bg-[#d03238] text-white hover:scale-[1.03] hover:bg-[#b5292f] active:scale-[0.98]",
  warning:
    "bg-[#ffd11a] text-[#4f3b00] hover:scale-[1.03] hover:bg-[#ffe05c] active:scale-[0.98]",
} as const;

export function buttonStyles(
  variant: keyof typeof buttonVariants = "secondary",
  className?: string,
) {
  return cn(buttonBase, buttonVariants[variant], className);
}

const signalPillBase =
  "inline-flex items-center justify-center rounded-full px-3 py-1.5 text-[0.76rem] font-semibold tracking-[-0.01em]";
const signalPillVariants = {
  positive: "bg-[#054d28]/[0.12] text-[#054d28]",
  soft: "bg-[#163300]/[0.08] text-[#454745]",
  danger: "bg-[#d03238]/[0.12] text-[#9d2329]",
  warning: "bg-[#ffd11a]/20 text-[#7a5a00]",
  neutral: "bg-black/[0.06] text-[#454745]",
  inverse: "bg-white/10 text-[#ecf3e2]",
} as const;

export function signalPillStyles(
  variant: keyof typeof signalPillVariants = "soft",
  className?: string,
) {
  return cn(signalPillBase, signalPillVariants[variant], className);
}

const statusToneMap: Record<DocumentStatus | "draft" | "under_review", string> = {
  uploaded: "bg-[#163300]/[0.08] text-[#454745]",
  processing: "bg-sky-400/[0.12] text-sky-700",
  processed: "bg-[#9fe870]/25 text-[#163300]",
  needs_review: "bg-[#ffd11a]/20 text-[#7a5a00]",
  approved: "bg-[#054d28]/[0.12] text-[#054d28]",
  rejected: "bg-[#d03238]/[0.12] text-[#9d2329]",
  failed: "bg-[#d03238]/[0.12] text-[#9d2329]",
  draft: "bg-black/[0.06] text-[#454745]",
  under_review: "bg-[#ffd11a]/20 text-[#7a5a00]",
};

const statusDotMap: Record<DocumentStatus | "draft" | "under_review", string> = {
  uploaded: "bg-[#6c7268]",
  processing: "bg-sky-500",
  processed: "bg-[#9fe870]",
  needs_review: "bg-[#ffd11a]",
  approved: "bg-[#054d28]",
  rejected: "bg-[#d03238]",
  failed: "bg-[#d03238]",
  draft: "bg-[#6c7268]",
  under_review: "bg-[#ffd11a]",
};

export function statusBadgeStyles(status: string) {
  return cn(
    "inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-[0.76rem] font-semibold tracking-[-0.01em]",
    statusToneMap[status as keyof typeof statusToneMap] || statusToneMap.draft,
  );
}

export function statusDotStyles(status: string) {
  return cn("h-2.5 w-2.5 rounded-full", statusDotMap[status as keyof typeof statusDotMap] || statusDotMap.draft);
}

const progressToneMap = {
  brand: "bg-[#9fe870]",
  positive: "bg-[#054d28]",
  warning: "bg-[#ffd11a]",
  danger: "bg-[#d03238]",
  neutral: "bg-[#6c7268]",
} as const;

export function progressFillStyles(
  tone: keyof typeof progressToneMap = "brand",
  className?: string,
) {
  return cn("absolute inset-y-0 left-0 rounded-full", progressToneMap[tone], className);
}

const pipelineToneMap = {
  done: "border-[#9fe870]/40 bg-[#9fe870]/[0.12] text-[#163300]",
  active: "border-sky-400/30 bg-sky-400/10 text-sky-700",
  pending: "border-black/10 bg-black/[0.03] text-[#454745]",
  warning: "border-[#ffd11a]/40 bg-[#ffd11a]/[0.12] text-[#7a5a00]",
} as const;

const pipelineIndexToneMap = {
  done: "bg-[#9fe870] text-[#163300]",
  active: "bg-sky-500 text-white",
  pending: "bg-black/[0.06] text-[#454745]",
  warning: "bg-[#ffd11a] text-[#7a5a00]",
} as const;

export function pipelineStepStyles(
  state: keyof typeof pipelineToneMap,
  className?: string,
) {
  return cn(
    "grid gap-3 rounded-[28px] border px-4 py-4",
    pipelineToneMap[state],
    className,
  );
}

export function pipelineStepIndexStyles(state: keyof typeof pipelineIndexToneMap) {
  return cn(
    "inline-flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold",
    pipelineIndexToneMap[state],
  );
}
