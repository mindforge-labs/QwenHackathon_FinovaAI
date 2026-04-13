import { statusBadgeStyles, statusDotStyles } from "@/components/common/ui";
import { formatStatusLabel } from "@/lib/utils";

export function StatusBadge({ status }: { status: string }) {
  return (
    <span className={statusBadgeStyles(status)}>
      <span className={statusDotStyles(status)} />
      {formatStatusLabel(status)}
    </span>
  );
}
