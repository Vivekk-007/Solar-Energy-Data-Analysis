"""Dashboard constants and non-secret configuration."""
from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

LOCATION = "Jabalpur, Madhya Pradesh, India"
LATITUDE = 23.1815
LONGITUDE = 79.9864
DATA_SOURCE = "Open-Meteo Historical API"
MIN_DATE = date(2024, 8, 12)
MAX_DATE = date(2026, 8, 11)


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def get_database_config() -> DatabaseConfig:
    try:
        port = int(os.getenv("MYSQL_PORT", "3306"))
    except ValueError as exc:
        raise ValueError("MYSQL_PORT must be an integer") from exc
    return DatabaseConfig(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=port,
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "test1"),
    )
