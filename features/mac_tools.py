"""macOS helpers: app launching, volume and weather."""
import subprocess
import requests


APP_NAMES = {
    "safari": "Safari",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "terminal": "Terminal",
    "finder": "Finder",
    "notes": "Notes",
    "calendar": "Calendar",
    "calender": "Calendar",
    "facetime": "FaceTime",
    "face time": "FaceTime",
    "music": "Music",
}


def open_mac_app(name: str) -> None:
    key = name.strip().lower()
    app = APP_NAMES.get(key, name.strip())
    subprocess.run(["open", "-a", app], check=True)


def set_volume(level: int) -> None:
    level = max(0, min(100, int(level)))
    subprocess.run(
        ["osascript", "-e", f"set volume output volume {level}"],
        check=True
    )


def get_weather(place: str) -> str:
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1, "language": "en", "format": "json"},
            timeout=12
        )
        geo.raise_for_status()
        results = geo.json().get("results", [])
        if not results:
            return f"I couldn't find the location {place}."
        location = results[0]
        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
            },
            timeout=12
        )
        weather.raise_for_status()
        current = weather.json()["current"]
        return (
            f"Weather in {location['name']}: {current['temperature_2m']} degrees Celsius, "
            f"feels like {current['apparent_temperature']} degrees, "
            f"humidity {current['relative_humidity_2m']} percent, "
            f"wind speed {current['wind_speed_10m']} kilometers per hour."
        )
    except requests.RequestException:
        return "Weather service is unavailable right now. Please check your internet connection."
