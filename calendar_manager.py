"""Read future events from an optional public/private iCalendar (.ics) feed.

Set MAMBO_ICS_URL as an environment variable or put a local calendar.ics beside
this file. Do not commit a private feed URL to GitHub.
"""
import os
from datetime import datetime, timedelta, date, time
from pathlib import Path
from urllib.request import urlopen


def get_upcoming_events(limit=5):
    url = os.environ.get("MAMBO_ICS_URL", "").strip()
    local_file = Path(__file__).with_name("calendar.ics")
    if not url and not local_file.exists():
        return None  # Not configured

    try:
        from icalendar import Calendar
        import recurring_ical_events
    except ImportError as exc:
        raise RuntimeError("Install dependencies: python -m pip install -r requirements.txt") from exc

    if url:
        if not url.startswith("https://"):
            raise ValueError("Calendar URL must begin with https://")
        with urlopen(url, timeout=12) as response:
            content = response.read(5_000_001)
        if len(content) > 5_000_000:
            raise ValueError("Calendar feed is too large")
    else:
        content = local_file.read_bytes()

    calendar = Calendar.from_ical(content)
    now = datetime.now().astimezone()
    end = now + timedelta(days=30)
    result = []
    for event in recurring_ical_events.of(calendar).between(now, end):
        starts = event.decoded("DTSTART")
        if isinstance(starts, date) and not isinstance(starts, datetime):
            label = starts.strftime("%a %b %d") + " (all day)"
        else:
            if starts.tzinfo is None:
                starts = starts.replace(tzinfo=now.tzinfo)
            label = starts.astimezone().strftime("%a %b %d, %I:%M %p")
        result.append((starts, label, str(event.get("summary", "Untitled event"))))
    result.sort(key=lambda entry: entry[0].isoformat())
    return [f"{label} - {title}" for _, label, title in result[:limit]]
