"""Load *demonstration only* medication schedules from a local JSON file."""
import json
from pathlib import Path

FILE = Path(__file__).with_name("medications.json")
DAYS = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")


def get_medications(day):
    if day not in DAYS:
        raise ValueError("Invalid day")
    with FILE.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("schedule", {}).get(day, [])
