"""Read current Tampa, FL weather from Open-Meteo; no API key required."""
import json
from urllib.request import urlopen

# Approximate central Tampa coordinates, NOT the user's device location.
URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=27.9506&longitude=-82.4572"
    "&current=temperature_2m,relative_humidity_2m,weather_code"
    "&temperature_unit=fahrenheit&timezone=America%2FNew_York"
)

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Fog", 51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
    61: "Rain", 63: "Rain", 65: "Heavy rain", 71: "Snow",
    73: "Snow", 75: "Heavy snow", 80: "Rain showers", 81: "Rain showers",
    82: "Heavy showers", 95: "Thunderstorms", 96: "Thunderstorms", 99: "Thunderstorms",
}


def get_weather():
    with urlopen(URL, timeout=10) as response:
        data = json.load(response)
    current = data["current"]
    return {
        "temperature": round(float(current["temperature_2m"])),
        "condition": WEATHER_CODES.get(current.get("weather_code"), "Weather available"),
        "humidity": current.get("relative_humidity_2m"),
        "observed_at": current.get("time", ""),
    }
