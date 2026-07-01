import { useAppSettings } from "../contexts/AppSettingsContext";
import type { ClubOpenStatus } from "../types/api";
import { formatOpenStatusLabel } from "../utils/clubHours";

interface ClubStatusBadgeProps {
  status: ClubOpenStatus | null | undefined;
}

export function ClubStatusBadge({ status }: ClubStatusBadgeProps) {
  const { t } = useAppSettings();

  if (!status) {
    return null;
  }

  const text = formatOpenStatusLabel(status, t);
  if (!text) {
    return null;
  }

  const tone =
    status.is_open === true ? "open" : status.is_open === false ? "closed" : "neutral";

  return (
    <div className={`app-bar__status app-bar__status--${tone}`} title={text}>
      <span className="app-bar__status-dot" />
      <span className="app-bar__status-text">{text}</span>
    </div>
  );
}
