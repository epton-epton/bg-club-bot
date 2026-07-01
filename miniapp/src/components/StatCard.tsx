interface StatCardProps {
  label: string;
  value: string | number;
  hint?: string;
  trend?: string;
  variant?: "cyan" | "pink";
}

export function StatCard({ label, value, hint, trend, variant = "cyan" }: StatCardProps) {
  return (
    <div className={`stat-card stat-card--${variant}`}>
      <span className="stat-card__label">{label}</span>
      <strong className="stat-card__value">{value}</strong>
      {hint ? <span className="stat-card__hint">{hint}</span> : null}
      {trend ? <span className="stat-card__trend">{trend}</span> : null}
    </div>
  );
}
