import { useAppSettings } from "../contexts/AppSettingsContext";

export function useMe() {
  const { me, displayName, isAdmin, refreshMe } = useAppSettings();
  return { me, displayName, isAdmin, refreshMe };
}
