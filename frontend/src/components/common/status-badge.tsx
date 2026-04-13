import { formatStatusLabel } from "@/lib/utils";

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={`status-badge status-${status}`}>
      <span className="status-badge__dot" />
      {formatStatusLabel(status)}
    </span>
  );
}
