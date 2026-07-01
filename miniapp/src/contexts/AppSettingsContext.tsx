import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { api } from "../api/client";
import {
  DEFAULT_THEME,
  getMessages,
  interpolate,
  resolveLocale,
  resolveTheme,
  type Locale,
  type Messages,
  type ThemeId,
} from "../i18n";
import type { Me, MePreferencesUpdate } from "../types/api";

const THEME_STORAGE_KEY = "bgclub_theme";
/** Bump to wipe stale language cache in Telegram WebView (v1 stored ru from Windows). */
const LANGUAGE_CACHE_VERSION = "2";
const LANGUAGE_CACHE_VERSION_KEY = "bgclub_language_cache_v";

interface AppSettingsContextValue {
  me: Me | null;
  locale: Locale;
  theme: ThemeId;
  messages: Messages;
  t: (path: string, vars?: Record<string, string | number>) => string;
  savedLanguage: Locale | null;
  savedTheme: ThemeId | null;
  settingsReady: boolean;
  settingsSaving: boolean;
  settingsSaved: boolean;
  settingsError: string | null;
  updatePreferences: (prefs: MePreferencesUpdate) => Promise<void>;
  refreshMe: () => Promise<void>;
  displayName: string | null;
  isAdmin: boolean;
}

const AppSettingsContext = createContext<AppSettingsContextValue | null>(null);

function getTelegramLanguageCode(): string | undefined {
  const fromUnsafe = window.Telegram?.WebApp?.initDataUnsafe?.user?.language_code;
  if (fromUnsafe) {
    return fromUnsafe;
  }

  const initData = window.Telegram?.WebApp?.initData;
  if (!initData) {
    return undefined;
  }

  try {
    const userJson = new URLSearchParams(initData).get("user");
    if (userJson) {
      const user = JSON.parse(userJson) as { language_code?: string };
      return user.language_code;
    }
  } catch {
    // ignore malformed init data
  }
  return undefined;
}

function isTelegramWebApp(): boolean {
  const webApp = window.Telegram?.WebApp;
  if (!webApp) {
    return false;
  }
  return Boolean(
    webApp.initData ||
      webApp.initDataUnsafe?.user ||
      (webApp.platform && webApp.platform !== "unknown"),
  );
}

function migrateLanguageCache() {
  if (localStorage.getItem(LANGUAGE_CACHE_VERSION_KEY) === LANGUAGE_CACHE_VERSION) {
    return;
  }
  localStorage.removeItem("bgclub_language");
  localStorage.setItem(LANGUAGE_CACHE_VERSION_KEY, LANGUAGE_CACHE_VERSION);
}

function readCachedTheme(): ThemeId | null {
  const value = localStorage.getItem(THEME_STORAGE_KEY);
  if (
    value === "synthwave" ||
    value === "midnight" ||
    value === "aurora" ||
    value === "daylight"
  ) {
    return value;
  }
  if (value === "ember") {
    return "daylight";
  }
  return null;
}

function clearCachedLanguage() {
  localStorage.removeItem("bgclub_language");
}

function getByPath(messages: Messages, path: string): string | undefined {
  const value = path.split(".").reduce<unknown>((acc, key) => {
    if (acc && typeof acc === "object" && key in acc) {
      return (acc as Record<string, unknown>)[key];
    }
    return undefined;
  }, messages);
  return typeof value === "string" ? value : undefined;
}

export function AppSettingsProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [settingsReady, setSettingsReady] = useState(false);
  const [settingsSaving, setSettingsSaving] = useState(false);
  const [settingsSaved, setSettingsSaved] = useState(false);
  const [settingsError, setSettingsError] = useState<string | null>(null);
  const [prefsLoaded, setPrefsLoaded] = useState(false);
  const [pendingLanguage, setPendingLanguage] = useState<Locale | null>(null);
  const [localTheme, setLocalTheme] = useState<ThemeId | null>(() => readCachedTheme());

  // DB choice after sync; pending = optimistic click; before sync → Telegram default
  const savedLanguage = pendingLanguage ?? (prefsLoaded ? (me?.language ?? null) : null);
  const savedTheme = me?.theme ?? localTheme;
  const locale = resolveLocale(
    savedLanguage,
    getTelegramLanguageCode(),
    isTelegramWebApp(),
  );
  const theme = resolveTheme(savedTheme);
  const messages = useMemo(() => getMessages(locale), [locale]);

  const t = useCallback(
    (path: string, vars?: Record<string, string | number>) => {
      const value = getByPath(messages, path) ?? path;
      return vars ? interpolate(value, vars) : value;
    },
    [messages],
  );

  const applyTheme = useCallback((nextTheme: ThemeId) => {
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    setLocalTheme(nextTheme);
  }, []);

  const refreshMe = useCallback(async () => {
    const data = await api.getMe();
    setMe(data);
    setPendingLanguage(null);
    if (!data.language) {
      clearCachedLanguage();
    }
    if (data.theme) {
      applyTheme(data.theme);
    }
  }, [applyTheme]);

  useEffect(() => {
    migrateLanguageCache();
    applyTheme(readCachedTheme() ?? DEFAULT_THEME);
    refreshMe()
      .catch(() => setMe(null))
      .finally(() => {
        setPrefsLoaded(true);
        setSettingsReady(true);
      });
  }, [applyTheme, refreshMe]);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  useEffect(() => {
    applyTheme(theme);
  }, [applyTheme, theme]);

  const updatePreferences = useCallback(
    async (prefs: MePreferencesUpdate) => {
      if (prefs.language) {
        setPendingLanguage(prefs.language);
      }
      if (prefs.theme) {
        applyTheme(prefs.theme);
      }

      setSettingsSaving(true);
      setSettingsSaved(false);
      setSettingsError(null);

      try {
        const updated = await api.updatePreferences(prefs);
        setMe(updated);
        setPendingLanguage(null);
        if (updated.theme) {
          applyTheme(updated.theme);
        }
        setSettingsSaved(true);
        window.setTimeout(() => setSettingsSaved(false), 2000);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Error";
        setSettingsError(message);
      } finally {
        setSettingsSaving(false);
      }
    },
    [applyTheme],
  );

  const displayName =
    [me?.first_name, me?.last_name].filter(Boolean).join(" ") || me?.username || null;

  const value: AppSettingsContextValue = {
    me,
    locale,
    theme,
    messages,
    t,
    savedLanguage,
    savedTheme,
    settingsReady,
    settingsSaving,
    settingsSaved,
    settingsError,
    updatePreferences,
    refreshMe,
    displayName,
    isAdmin: me?.role === "admin",
  };

  return <AppSettingsContext.Provider value={value}>{children}</AppSettingsContext.Provider>;
}

export function useAppSettings() {
  const context = useContext(AppSettingsContext);
  if (!context) {
    throw new Error("useAppSettings must be used within AppSettingsProvider");
  }
  return context;
}
