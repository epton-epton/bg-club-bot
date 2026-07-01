import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { api } from "../api/client";
import { useAppSettings } from "./AppSettingsContext";
import type { Club } from "../types/api";
import { computeOpenStatus } from "../utils/clubHours";

interface ClubContextValue {
  club: Club | null;
  loading: boolean;
  error: string | null;
  refreshClub: () => Promise<void>;
}

const ClubContext = createContext<ClubContextValue | null>(null);

function withOpenStatus(
  club: Club,
  locale: ReturnType<typeof useAppSettings>["locale"],
): Club {
  const timezone = club.timezone ?? "Europe/Kyiv";
  return {
    ...club,
    timezone,
    open_status: computeOpenStatus(club.hours, club.open_status_override, timezone, locale),
  };
}

export function ClubProvider({ children }: { children: ReactNode }) {
  const { locale } = useAppSettings();
  const [club, setClub] = useState<Club | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refreshClub = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getClub();
      setClub(withOpenStatus(data, locale));
    } catch (err) {
      setClub(null);
      setError(err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
    }
  }, [locale]);

  useEffect(() => {
    void refreshClub();
  }, [refreshClub]);

  return (
    <ClubContext.Provider value={{ club, loading, error, refreshClub }}>
      {children}
    </ClubContext.Provider>
  );
}

export function useClub() {
  const context = useContext(ClubContext);
  if (!context) {
    throw new Error("useClub must be used within ClubProvider");
  }
  return context;
}
