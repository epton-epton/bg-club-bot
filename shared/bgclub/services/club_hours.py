import re
from dataclasses import dataclass
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo

DAY_ABBR = {
    "пн": 0,
    "вт": 1,
    "ср": 2,
    "чт": 3,
    "пт": 4,
    "сб": 5,
    "вс": 6,
}

DAY_LABELS = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

LINE_PATTERN = re.compile(
    r"([ПпВвСсЧч][нтрбс]?)"
    r"(?:[–\-—]([ПпВвСсЧч][нтрбс]?))?"
    r"\s*:\s*"
    r"(\d{1,2}):(\d{2})\s*[–\-—]\s*(\d{1,2}):(\d{2})"
)


@dataclass(frozen=True)
class DaySchedule:
    weekday: int
    open_time: time
    close_time: time


@dataclass(frozen=True)
class OpenStatus:
    is_open: bool | None
    label: str


def _weekday_from_abbr(value: str) -> int | None:
    key = value.strip().lower()[:2]
    return DAY_ABBR.get(key)


def _expand_weekdays(start: int, end: int | None) -> list[int]:
    if end is None:
        return [start]
    if start <= end:
        return list(range(start, end + 1))
    return list(range(start, 7)) + list(range(0, end + 1))


def parse_hours_text(hours: str) -> list[DaySchedule]:
    schedules: list[DaySchedule] = []

    for line in hours.splitlines():
        line = line.strip()
        if not line:
            continue

        match = LINE_PATTERN.search(line)
        if not match:
            continue

        start_day = _weekday_from_abbr(match.group(1))
        if start_day is None:
            continue

        end_day = _weekday_from_abbr(match.group(2)) if match.group(2) else None
        if match.group(2) and end_day is None:
            continue

        open_time = time(int(match.group(3)), int(match.group(4)))
        close_time = time(int(match.group(5)), int(match.group(6)))

        for weekday in _expand_weekdays(start_day, end_day):
            schedules.append(
                DaySchedule(weekday=weekday, open_time=open_time, close_time=close_time)
            )

    return schedules


def compute_open_status(
    schedules: list[DaySchedule],
    *,
    now: datetime | None = None,
    override: str | None = None,
    club_timezone: str = "Europe/Kyiv",
) -> OpenStatus:
    if override and override.strip():
        return OpenStatus(is_open=None, label=override.strip())

    if not schedules:
        return OpenStatus(is_open=None, label="Часы работы не указаны")

    moment = now or datetime.now(timezone.utc)
    local_now = moment.astimezone(ZoneInfo(club_timezone))
    today = local_now.weekday()
    current_time = local_now.time()

    today_schedules = sorted(
        [item for item in schedules if item.weekday == today],
        key=lambda item: item.open_time,
    )

    for item in today_schedules:
        if item.open_time <= current_time <= item.close_time:
            return OpenStatus(
                is_open=True,
                label=f"Открыто до {item.close_time.strftime('%H:%M')}",
            )

    for item in today_schedules:
        if current_time < item.open_time:
            return OpenStatus(
                is_open=False,
                label=f"Откроемся в {item.open_time.strftime('%H:%M')}",
            )

    for offset in range(1, 8):
        weekday = (today + offset) % 7
        day_schedules = sorted(
            [item for item in schedules if item.weekday == weekday],
            key=lambda item: item.open_time,
        )
        if not day_schedules:
            continue

        next_open = day_schedules[0]
        if offset == 1:
            return OpenStatus(
                is_open=False,
                label=f"Откроемся завтра в {next_open.open_time.strftime('%H:%M')}",
            )
        return OpenStatus(
            is_open=False,
            label=(
                f"Откроемся в {DAY_LABELS[weekday]} "
                f"в {next_open.open_time.strftime('%H:%M')}"
            ),
        )

    return OpenStatus(is_open=False, label="Закрыто")
