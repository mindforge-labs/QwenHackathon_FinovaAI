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
    <div className="dashboard-chart dashboard-chart--donut">
      <div className="dashboard-chart__visual">
        <svg className="dashboard-donut" viewBox="0 0 120 120" aria-hidden="true">
          <circle className="dashboard-donut__track" cx="60" cy="60" r="42" />
          {segments.map((segment) => {
            if (segment.value <= 0 || total <= 0) {
              return null;
            }

            const angle = (segment.value / total) * 360;
            const startAngle = currentAngle;
            currentAngle += angle;

            return (
              <path
                className="dashboard-donut__slice"
                d={describeArc(60, 60, 42, startAngle, currentAngle)}
                key={segment.label}
                stroke={segment.color}
              />
            );
          })}
        </svg>
        <div className="dashboard-chart__center">
          <strong>{total}</strong>
          <span>{totalLabel}</span>
        </div>
      </div>

      <div className="dashboard-chart__legend">
        {segments.map((segment) => (
          <div className="dashboard-legend-item" key={segment.label}>
            <span className="dashboard-legend-item__swatch" style={{ backgroundColor: segment.color }} />
            <div>
              <strong>{segment.label}</strong>
              <p>{segment.detail}</p>
            </div>
            <span>{segment.value}</span>
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
    <div className="dashboard-chart dashboard-chart--trend">
      <div className="dashboard-trend-chart">
        <svg viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
          {[0, 0.5, 1].map((step) => {
            const y = paddingTop + usableHeight * step;
            return <line className="dashboard-grid-line" key={step} x1={paddingX} x2={width - paddingX} y1={y} y2={y} />;
          })}
          {chartPoints.map((seriesItem) => (
            <g key={seriesItem.key}>
              <path className="dashboard-line" d={seriesItem.path} stroke={seriesItem.color} />
              {seriesItem.values.map((point, index) => (
                <circle
                  className="dashboard-line__point"
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

      <div className="dashboard-trend-footer">
        <div className="dashboard-trend-legend">
          {chartPoints.map((seriesItem) => (
            <div className="dashboard-trend-legend__item" key={seriesItem.key}>
              <span className="dashboard-trend-legend__swatch" style={{ backgroundColor: seriesItem.color }} />
              <strong>{seriesItem.label}</strong>
            </div>
          ))}
        </div>

        <div className="dashboard-trend-labels">
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
    <div className="dashboard-funnel">
      {stages.map((stage) => (
        <article className={`dashboard-funnel-stage dashboard-funnel-stage--${stage.tone}`} key={stage.label}>
          <div className="dashboard-funnel-stage__header">
            <strong>{stage.label}</strong>
            <span>{stage.value}</span>
          </div>
          <div className="dashboard-funnel-stage__track">
            <span
              className={`dashboard-funnel-stage__fill dashboard-funnel-stage__fill--${stage.tone}`}
              style={{ width: `${(stage.value / maxValue) * 100}%` }}
            />
          </div>
          <p>{stage.detail}</p>
        </article>
      ))}
    </div>
  );
}
