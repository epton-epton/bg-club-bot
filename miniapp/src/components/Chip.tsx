interface ChipProps {
  children: string;
  tone?: "cyan" | "pink" | "muted";
}

export function Chip({ children, tone = "muted" }: ChipProps) {
  return <span className={`chip chip--${tone}`}>{children}</span>;
}
