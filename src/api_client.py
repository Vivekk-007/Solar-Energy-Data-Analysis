"""Small, reusable Open-Meteo historical API client."""
from typing import Any
import requests
from .config import API_URL, HOURLY_VARIABLES, LATITUDE, LONGITUDE, TIMEZONE

class OpenMeteoError(RuntimeError):
    pass

class OpenMeteoClient:
    def __init__(self, session: requests.Session | None = None, timeout: int = 60) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def fetch_historical(self, start_date: str, end_date: str) -> dict[str, Any]:
        params = {
            "latitude": LATITUDE, "longitude": LONGITUDE, "start_date": start_date,
            "end_date": end_date, "hourly": ",".join(HOURLY_VARIABLES),
            "timezone": TIMEZONE, "tilt": 23, "azimuth": 0,
        }
        try:
            response = self.session.get(API_URL, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise OpenMeteoError("Open-Meteo request timed out") from exc
        except requests.ConnectionError as exc:
            raise OpenMeteoError("Could not connect to Open-Meteo") from exc
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response else "unknown"
            raise OpenMeteoError(f"Open-Meteo returned HTTP {status}") from exc
        except requests.RequestException as exc:
            raise OpenMeteoError(f"Open-Meteo request failed: {exc}") from exc
        try:
            payload = response.json()
        except ValueError as exc:
            raise OpenMeteoError("Open-Meteo returned invalid JSON") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("hourly"), dict):
            raise OpenMeteoError("Open-Meteo response is missing an hourly object")
        return payload
