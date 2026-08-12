"""Dashboard constants and non-secret configuration."""
from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

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


def _read_streamlit_secrets() -> dict[str, str] | None:
    try:
        if not hasattr(st, "secrets") or not st.secrets:
            return None
    except StreamlitSecretNotFoundError:
        return None
    if "mysql" in st.secrets and isinstance(st.secrets["mysql"], dict):
        values = st.secrets["mysql"]
        return {
            "MYSQL_HOST": str(values.get("host", "") or "").strip(),
            "MYSQL_PORT": str(values.get("port", "") or "").strip(),
            "MYSQL_USER": str(values.get("user", "") or "").strip(),
            "MYSQL_PASSWORD": str(values.get("password", "") or "").strip(),
            "MYSQL_DATABASE": str(values.get("database", "") or "").strip(),
        }
    return {
        key: str(st.secrets.get(key, "") or "").strip()
        for key in (
            "MYSQL_HOST",
            "MYSQL_PORT",
            "MYSQL_USER",
            "MYSQL_PASSWORD",
            "MYSQL_DATABASE",
        )
    }


def _normalize_database_config(values: dict[str, str]) -> DatabaseConfig:
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ValueError("Missing database credential(s): " + ", ".join(missing))
    try:
        port = int(values["MYSQL_PORT"])
    except ValueError as exc:
        raise ValueError("MYSQL_PORT must be an integer") from exc
    return DatabaseConfig(
        host=values["MYSQL_HOST"],
        port=port,
        user=values["MYSQL_USER"],
        password=values["MYSQL_PASSWORD"],
        database=values["MYSQL_DATABASE"],
    )


def get_database_config() -> DatabaseConfig:
    secrets = _read_streamlit_secrets()
    if secrets is not None and any(secrets.values()):
        return _normalize_database_config(secrets)
    return _normalize_database_config({
        key: os.getenv(key, "").strip()
        for key in (
            "MYSQL_HOST",
            "MYSQL_PORT",
            "MYSQL_USER",
            "MYSQL_PASSWORD",
            "MYSQL_DATABASE",
        )
    })
