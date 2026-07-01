import type { Locale } from "../i18n";
import type { ClubOpenStatus } from "../types/api";

const DAY_ABBR: Record<string, number> = {
  пн: 0,
  вт: 1,
  ср: 2,
  чт: 3,
  пт: 4,
  сб: 5,
  вс: 6,
};

const LINE_PATTERN =
  /([ПпВвСсЧч][нтрбс]?)(?:[–\-—]([ПпВвСсЧч][нтрбс]?))?\s*:\s*(\d{1,2}):(\d{2})\s*[–\-—]\s*(\d{1,2}):(\d{2})/;

interface DaySchedule {
  weekday: number;
  openMinutes: number;
  closeMinutes: number;
}

function weekdayFromAbbr(value: string): number | null {
  const key = value.trim().toLowerCase().slice(0, 2);
  return DAY_ABBR[key] ?? null;
}

function expandWeekdays(start: number, end: number | null): number[] {
  if (end === null) {
    return [start];
  }
  if (start <= end) {
    return Array.from({ length: end - start + 1 }, (_, index) => start + index);
  }
  return [
    ...Array.from({ length: 7 - start }, (_, index) => start + index),
    ...Array.from({ length: end + 1 }, (_, index) => index),
  ];
}

function parseTimeToMinutes(hour: string, minute: string): number {
  return Number(hour) * 60 + Number(minute);
}

function formatMinutes(totalMinutes: number): string {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

function formatWeekdayShort(weekday: number, locale: Locale): string {
  const monday = new Date(Date.UTC(2024, 0, 1));
  const date = new Date(monday);
  date.setUTCDate(monday.getUTCDate() + weekday);
  const intlLocale = locale === "ua" ? "uk" : locale;
  return new Intl.DateTimeFormat(intlLocale, { weekday: "short", timeZone: "UTC" }).format(date);
}

export function parseHoursText(hours: string): DaySchedule[] {
  const schedules: DaySchedule[] = [];

  for (const line of hours.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed) {
      continue;
    }

    const match = LINE_PATTERN.exec(trimmed);
    if (!match) {
      continue;
    }

    const startDay = weekdayFromAbbr(match[1]);
    if (startDay === null) {
      continue;
    }

    const endDay = match[2] ? weekdayFromAbbr(match[2]) : null;
    if (match[2] && endDay === null) {
      continue;
    }

    const openMinutes = parseTimeToMinutes(match[3], match[4]);
    const closeMinutes = parseTimeToMinutes(match[5], match[6]);

    for (const weekday of expandWeekdays(startDay, endDay)) {
      schedules.push({ weekday, openMinutes, closeMinutes });
    }
  }

  return schedules;
}

export function computeOpenStatus(
  hours: string,
  override?: string | null,
  timezone = "Europe/Kyiv",
  locale: Locale = "ru",
): ClubOpenStatus {
  if (override?.trim()) {
    return { is_open: null, label: override.trim() };
  }

  const schedules = parseHoursText(hours);
  if (!schedules.length) {
    return { is_open: null, messageKey: "club.status.hoursUnknown" };
  }

  const now = new Date();
  const formatter = new Intl.DateTimeFormat("en-GB", {
    timeZone: timezone,
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
  const parts = formatter.formatToParts(now);
  const weekdayPart = parts.find((part) => part.type === "weekday")?.value ?? "Mon";
  const hour = Number(parts.find((part) => part.type === "hour")?.value ?? "0");
  const minute = Number(parts.find((part) => part.type === "minute")?.value ?? "0");

  const weekdayMap: Record<string, number> = {
    Mon: 0,
    Tue: 1,
    Wed: 2,
    Thu: 3,
    Fri: 4,
    Sat: 5,
    Sun: 6,
  };
  const today = weekdayMap[weekdayPart] ?? 0;
  const currentMinutes = hour * 60 + minute;

  const todaySchedules = schedules
    .filter((item) => item.weekday === today)
    .sort((left, right) => left.openMinutes - right.openMinutes);

  for (const item of todaySchedules) {
    if (item.openMinutes <= currentMinutes && currentMinutes <= item.closeMinutes) {
      return {
        is_open: true,
        messageKey: "club.status.openUntil",
        messageVars: { time: formatMinutes(item.closeMinutes) },
      };
    }
  }

  for (const item of todaySchedules) {
    if (currentMinutes < item.openMinutes) {
      return {
        is_open: false,
        messageKey: "club.status.opensAt",
        messageVars: { time: formatMinutes(item.openMinutes) },
      };
    }
  }

  for (let offset = 1; offset < 8; offset += 1) {
    const weekday = (today + offset) % 7;
    const daySchedules = schedules
      .filter((item) => item.weekday === weekday)
      .sort((left, right) => left.openMinutes - right.openMinutes);

    if (!daySchedules.length) {
      continue;
    }

    const nextOpen = daySchedules[0];
    const time = formatMinutes(nextOpen.openMinutes);
    if (offset === 1) {
      return {
        is_open: false,
        messageKey: "club.status.opensTomorrow",
        messageVars: { time },
      };
    }

    return {
      is_open: false,
      messageKey: "club.status.opensOnDay",
      messageVars: { day: formatWeekdayShort(weekday, locale), time },
    };
  }

  return { is_open: false, messageKey: "club.status.closed" };
}

export function formatOpenStatusLabel(
  status: ClubOpenStatus,
  t: (path: string, vars?: Record<string, string | number>) => string,
): string {
  if (status.label) {
    return status.label;
  }
  if (status.messageKey) {
    return t(status.messageKey, status.messageVars);
  }
  return "";
}
