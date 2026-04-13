import { cn } from "@/lib/utils";

import { progressFillStyles, sectionCard } from "./ui";

type ChartSegment = {
  label: string;
  value: number;
  color: string;
  detail: string;
};

type TrendSeries = {
  key: string;
  label: string;
  color: string;
};

type TrendPoint = {
  label: string;
  intake: number;
  review: number;
  risk: number;
};

type FunnelStage = {
  label: string;
  value: number;
  tone: "neutral" | "brand" | "warning" | "positive" | "danger";
  detail: string;
};

function polarToCartesian(centerX: number, centerY: number, radius: number, angle: number) {
  const radians = ((angle - 90) * Math.PI) / 180;
  return {
    x: centerX + radius * Math.cos(radians),
    y: centerY + radius * Math.sin(radians),
  };
}

function describeArc(centerX: number, centerY: number, radius: number, startAngle: number, endAngle: number) {
  const start = polarToCartesian(centerX, centerY, radius, endAngle);
  const end = polarToCartesian(centerX, centerY, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

  return [
    "M",
    start.x,
    start.y,
    "A",
    radius,
    radius,
    0,
    largeArcFlag,
    0,
    end.x,
    end.y,
  ].join(" ");
}

function buildLinePath(points: Array<{ x: number; y: number }>) {
  return points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
}

export function RiskDistributionChart({
  segments,
  totalLabel,
}: {
  segments: ChartSegment[];
  totalLabel: string;
}) {
  const total = segments.reduce((sum, segment) => sum + segment.value, 0);
  let currentAngle = 0;

  return (
    <div className={cn(sectionCard, "grid gap-6")}>
      <div className="relative mx-auto flex h-[220px] w-[220px] items-center justify-center">
        <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120" aria-hidden="true">
          <circle className="fill-none stroke-black/10 stroke-[10]" cx="60" cy="60" r="42" />
          {segments.map((segment) => {
            if (segment.value <= 0 || total <= 0) {
              return null;
            }

            const angle = (segment.value / total) * 360;
            const startAngle = currentAngle;
            currentAngle += angle;

            return (
              <path
                className="fill-none stroke-[10] stroke-linecap-round"
                d={describeArc(60, 60, 42, startAngle, currentAngle)}
                key={segment.label}
                stroke={segment.color}
              />
            );
          })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <strong className="[font-family:'Arial_Black',Impact,Inter,sans-serif] text-4xl font-black leading-none tracking-[-0.05em] text-[#0e0f0c]">
            {total}
          </strong>
          <span className="mt-2 text-sm text-[#454745]">{totalLabel}</span>
        </div>
      </div>

      <div className="grid gap-3">
        {segments.map((segment) => (
          <div className="flex items-start justify-between gap-4 rounded-[24px] bg-black/[0.03] px-4 py-3" key={segment.label}>
            <span className="mt-1 h-3 w-3 rounded-full" style={{ backgroundColor: segment.color }} />
            <div>
              <strong className="text-sm font-semibold text-[#0e0f0c]">{segment.label}</strong>
              <p className="mt-1 text-sm leading-6 text-[#454745]">{segment.detail}</p>
            </div>
            <span className="text-sm font-semibold text-[#0e0f0c]">{segment.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ProcessingTrendChart({
  points,
}: {
  points: TrendPoint[];
}) {
  const width = 360;
  const height = 180;
  const paddingX = 20;
  const paddingTop = 18;
  const paddingBottom = 32;
  const usableHeight = height - paddingTop - paddingBottom;
  const maxValue = Math.max(
    1,
    ...points.flatMap((point) => [point.intake, point.review, point.risk]),
  );
  const series: TrendSeries[] = [
    { key: "intake", label: "Intake", color: "#9fe870" },
    { key: "review", label: "Review activity", color: "#ffd11a" },
    { key: "risk", label: "Risk surfaced", color: "#d03238" },
  ];

  const chartPoints = series.map((seriesItem) => {
    const values = points.map((point, index) => {
      const rawValue = point[seriesItem.key as keyof TrendPoint];
      const value = typeof rawValue === "number" ? rawValue : 0;
      const x = paddingX + (index * (width - paddingX * 2)) / Math.max(points.length - 1, 1);
      const y = paddingTop + usableHeight - (value / maxValue) * usableHeight;
      return { x, y, value };
    });

    return {
      ...seriesItem,
      values,
      path: buildLinePath(values),
    };
  });

  return (
    <div className={cn(sectionCard, "grid gap-6")}>
      <div className="overflow-hidden rounded-[30px] bg-black/[0.03] p-4">
        <svg viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
          {[0, 0.5, 1].map((step) => {
            const y = paddingTop + usableHeight * step;
            return <line className="stroke-black/10" key={step} x1={paddingX} x2={width - paddingX} y1={y} y2={y} />;
          })}
          {chartPoints.map((seriesItem) => (
            <g key={seriesItem.key}>
              <path className="fill-none stroke-[3]" d={seriesItem.path} stroke={seriesItem.color} />
              {seriesItem.values.map((point, index) => (
                <circle
                  cx={point.x}
                  cy={point.y}
                  fill={seriesItem.color}
                  key={`${seriesItem.key}-${points[index]?.label || index}`}
                  r="3.5"
                />
              ))}
            </g>
          ))}
        </svg>
      </div>

      <div className="grid gap-4">
        <div className="flex flex-wrap items-center gap-4">
          {chartPoints.map((seriesItem) => (
            <div className="flex items-center gap-2 text-sm font-semibold text-[#0e0f0c]" key={seriesItem.key}>
              <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: seriesItem.color }} />
              <strong>{seriesItem.label}</strong>
            </div>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs font-semibold uppercase tracking-[0.12em] text-[#6c7268]">
          {points.map((point) => (
            <span key={point.label}>{point.label}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

export function PipelineFunnelChart({
  stages,
}: {
  stages: FunnelStage[];
}) {
  const maxValue = Math.max(1, ...stages.map((stage) => stage.value));

  return (
    <div className="grid gap-4">
      {stages.map((stage) => (
        <article className="rounded-[28px] border border-black/10 bg-white/[0.72] p-4" key={stage.label}>
          <div className="flex items-center justify-between gap-4">
            <strong className="text-sm font-semibold text-[#0e0f0c]">{stage.label}</strong>
            <span className="text-sm font-semibold text-[#0e0f0c]">{stage.value}</span>
          </div>
          <div className="relative mt-3 h-2.5 overflow-hidden rounded-full bg-black/[0.08]">
            <span
              className={progressFillStyles(stage.tone)}
              style={{ width: `${(stage.value / maxValue) * 100}%` }}
            />
          </div>
          <p className="mt-3 text-sm leading-6 text-[#454745]">{stage.detail}</p>
        </article>
      ))}
    </div>
  );
}
