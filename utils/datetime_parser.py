from datetime import datetime, timedelta
import re
from zoneinfo import ZoneInfo


TIME_RE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)\b")
MONTH_RE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(?:,\s*(\d{4}))?",
    re.I,
)
MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def parse_match_start(text: str, timezone_name: str) -> datetime | None:
    time_match = TIME_RE.search(text)
    if not time_match:
        return None

    tz = ZoneInfo(timezone_name)
    now = datetime.now(tz)
    hour = int(time_match.group(1))
    minute = int(time_match.group(2) or "0")
    meridiem = time_match.group(3).lower()
    if meridiem == "pm" and hour != 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0

    lowered = text.lower()
    if "tomorrow" in lowered:
        day = now + timedelta(days=1)
        return day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if "today" in lowered:
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    month_match = MONTH_RE.search(text)
    if month_match:
        month = MONTHS[month_match.group(1).lower()[:4].rstrip("t")]
        day = int(month_match.group(2))
        year = int(month_match.group(3) or now.year)
        candidate = datetime(year, month, day, hour, minute, tzinfo=tz)
        if candidate < now - timedelta(days=1) and not month_match.group(3):
            candidate = candidate.replace(year=year + 1)
        return candidate

    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate < now - timedelta(hours=2):
        candidate += timedelta(days=1)
    return candidate
