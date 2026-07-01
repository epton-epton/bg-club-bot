import type { Locale } from "../i18n";

const intlLocales: Record<Locale, string> = {
  ru: "ru-RU",
  en: "en-US",
  ua: "uk-UA",
};

function intlLocale(locale: Locale): string {
  return intlLocales[locale];
}

export function formatDateTime(value: string, locale: Locale): string {
  return new Intl.DateTimeFormat(intlLocale(locale), {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function formatDateParts(
  value: string,
  locale: Locale,
): { day: string; month: string; time: string } {
  const date = new Date(value);
  const loc = intlLocale(locale);
  return {
    day: new Intl.DateTimeFormat(loc, { day: "2-digit" }).format(date),
    month: new Intl.DateTimeFormat(loc, { month: "short" }).format(date),
    time: new Intl.DateTimeFormat(loc, { hour: "2-digit", minute: "2-digit" }).format(date),
  };
}

export function formatPlayers(
  min: number | null,
  max: number | null,
  t: (path: string, vars?: Record<string, string | number>) => string,
): string {
  if (min !== null && max !== null) {
    return t("games.players", { min, max });
  }
  if (max !== null) {
    return t("games.playersUpTo", { max });
  }
  if (min !== null) {
    return t("games.playersFrom", { min });
  }
  return t("games.playersAny");
}

export function formatEventType(
  value: string,
  t: (path: string) => string,
): string {
  const key = `calendar.types.${value}`;
  const translated = t(key);
  return translated === key ? t("calendar.types.other") : translated;
}

export function formatMonthYear(value: string, locale: Locale): string {
  return new Intl.DateTimeFormat(intlLocale(locale), { month: "long", year: "numeric" }).format(
    new Date(value),
  );
}

export function formatSessionStatus(
  value: string,
  t: (path: string) => string,
): string {
  const key = `sessionStatus.${value}`;
  const translated = t(key);
  return translated === key ? value : translated;
}

export function formatBookingStatus(
  value: string,
  t: (path: string) => string,
): string {
  const key = `bookingStatus.${value}`;
  const translated = t(key);
  return translated === key ? value : translated;
}

export function formatVisitSource(
  value: string,
  t: (path: string) => string,
): string {
  const key = `visitSource.${value}`;
  const translated = t(key);
  return translated === key ? value : translated;
}

export function toDatetimeLocalValue(iso: string): string {
  const date = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}
