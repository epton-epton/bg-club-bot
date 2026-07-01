import { en } from "./locales/en";
import { ru } from "./locales/ru";
import { ua } from "./locales/ua";
import type { Locale, Messages, ThemeId } from "./types";

export type { Locale, Messages, ThemeId };

export const LOCALES: Locale[] = ["ru", "en", "ua"];
export const THEMES: ThemeId[] = ["synthwave", "midnight", "aurora", "daylight"];
export const DEFAULT_THEME: ThemeId = "synthwave";

const catalogs: Record<Locale, Messages> = { ru, en, ua };

export function mapLanguageCode(code: string | undefined): Locale | null {
  const normalized = (code ?? "").toLowerCase();
  if (normalized.startsWith("ru")) return "ru";
  if (normalized.startsWith("uk") || normalized.startsWith("ua")) return "ua";
  if (normalized.startsWith("en")) return "en";
  return null;
}

/** Сохранённый в БД язык → иначе language_code Telegram → иначе en (в Telegram) / браузер. */
export function resolveLocale(
  saved: Locale | null | undefined,
  telegramLanguageCode: string | undefined,
  inTelegram = false,
): Locale {
  if (saved) {
    return saved;
  }
  const fromTelegram = mapLanguageCode(telegramLanguageCode);
  if (fromTelegram) {
    return fromTelegram;
  }
  if (inTelegram) {
    return "en";
  }
  if (typeof navigator !== "undefined") {
    return mapLanguageCode(navigator.language) ?? "en";
  }
  return "en";
}

export function resolveTheme(saved: ThemeId | null | undefined): ThemeId {
  if (saved === "ember") {
    return "daylight";
  }
  if (saved && THEMES.includes(saved)) {
    return saved;
  }
  return DEFAULT_THEME;
}

export function getMessages(locale: Locale): Messages {
  return catalogs[locale];
}

export function interpolate(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => String(vars[key] ?? ""));
}
