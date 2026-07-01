import { useAppSettings } from "../contexts/AppSettingsContext";

export function LoadingState({ label }: { label?: string }) {
  const { t } = useAppSettings();
  return <p className="state-message">{label ?? t("common.loading")}</p>;
}
