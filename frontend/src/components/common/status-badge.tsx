import { formatStatusLabel } from "@/lib/utils";

export function StatusBadge({ status }: { status: string }) {
  return <span className={`status-badge status-${status}`}>{formatStatusLabel(status)}</span>;
}
