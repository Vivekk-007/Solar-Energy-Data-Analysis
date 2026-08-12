"""Configuration loaded from environment, with non-secret API constants."""
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

LATITUDE = 23.1815
LONGITUDE = 79.9864
TIMEZONE = "Asia/Kolkata"
START_DATE = "2024-08-12"
END_DATE = "2026-08-11"
API_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_VARIABLES = (
    "temperature_2m", "relative_humidity_2m", "cloud_cover", "wind_speed_10m",
    "shortwave_radiation", "direct_radiation", "diffuse_radiation",
    "direct_normal_irradiance", "global_tilted_irradiance", "sunshine_duration",
)
RENAME_COLUMNS = {
    "temperature_2m": "temperature", "relative_humidity_2m": "humidity",
    "cloud_cover": "cloud_cover", "wind_speed_10m": "wind_speed",
    "shortwave_radiation": "solar_radiation", "direct_radiation": "direct_radiation",
    "diffuse_radiation": "diffuse_radiation", "direct_normal_irradiance": "dni",
    "global_tilted_irradiance": "gti", "sunshine_duration": "sunshine_duration",
}

@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

def get_database_config() -> DatabaseConfig:
    """Return MySQL configuration without ever logging its password."""
    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError as exc:
        raise ValueError("MYSQL_PORT must be an integer") from exc
    return DatabaseConfig(
        host=os.getenv("MYSQL_HOST", "localhost"), port=port,
        user=os.getenv("MYSQL_USER", "root"), password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "test1"),
    )
