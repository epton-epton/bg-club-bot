interface SectionHeaderProps {
  title: string;
  action?: string;
  onAction?: () => void;
}

export function SectionHeader({ title, action, onAction }: SectionHeaderProps) {
  return (
    <div className="section-header">
      <h2 className="section-header__title">{title}</h2>
      {action ? (
        onAction ? (
          <button type="button" className="section-header__action" onClick={onAction}>
            {action}
          </button>
        ) : (
          <span className="section-header__action">{action}</span>
        )
      ) : null}
    </div>
  );
}
