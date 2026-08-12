"""Cached, reusable queries against the ETL-managed MySQL data set."""
from datetime import date
import pandas as pd
import streamlit as st

from .config import get_database_config
from .database import fetch_dataframe

DATE_FILTER = "`timestamp` >= %s AND `timestamp` < DATE_ADD(%s, INTERVAL 1 DAY)"


def _dates(start: date, end: date) -> tuple[str, str]:
    return start.isoformat(), end.isoformat()


@st.cache_data(show_spinner=False, ttl=900)
def load_solar_data(start: date, end: date) -> pd.DataFrame:
    columns = "`timestamp`, temperature, humidity, cloud_cover, wind_speed, solar_radiation, dni, gti, sunshine_duration"
    frame = fetch_dataframe(get_database_config(), f"SELECT {columns} FROM solar_energy WHERE {DATE_FILTER} ORDER BY `timestamp`", _dates(start, end))
    if not frame.empty:
        frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    return frame


@st.cache_data(show_spinner=False, ttl=900)
def load_daily_summary(start: date, end: date) -> pd.DataFrame:
    sql = f"""SELECT `date`, average_temperature, average_humidity, average_cloud_cover,
        average_solar_radiation, peak_solar_radiation, average_dni, average_gti, total_sunshine_duration
        FROM vw_daily_solar_summary WHERE `date` >= %s AND `date` <= %s ORDER BY `date`"""
    frame = fetch_dataframe(get_database_config(), sql, _dates(start, end))
    if not frame.empty:
        frame["date"] = pd.to_datetime(frame["date"])
    return frame


@st.cache_data(show_spinner=False, ttl=900)
def load_monthly_summary(start: date, end: date) -> pd.DataFrame:
    sql = f"""SELECT YEAR(`timestamp`) AS year, MONTH(`timestamp`) AS month,
        AVG(solar_radiation) AS average_solar_radiation, MAX(solar_radiation) AS peak_solar_radiation,
        AVG(dni) AS average_dni, AVG(gti) AS average_gti
        FROM solar_energy WHERE {DATE_FILTER}
        GROUP BY YEAR(`timestamp`), MONTH(`timestamp`) ORDER BY year, month"""
    frame = fetch_dataframe(get_database_config(), sql, _dates(start, end))
    if not frame.empty:
        frame["period"] = pd.to_datetime(dict(year=frame.year, month=frame.month, day=1))
    return frame


@st.cache_data(show_spinner=False, ttl=900)
def load_hourly_profile(start: date, end: date) -> pd.DataFrame:
    sql = f"""SELECT HOUR(`timestamp`) AS hour_of_day, AVG(solar_radiation) AS average_solar_radiation,
        AVG(dni) AS average_dni, AVG(gti) AS average_gti
        FROM solar_energy WHERE {DATE_FILTER} GROUP BY HOUR(`timestamp`) ORDER BY hour_of_day"""
    return fetch_dataframe(get_database_config(), sql, _dates(start, end))


@st.cache_data(show_spinner=False, ttl=900)
def load_data_quality() -> pd.DataFrame:
    sql = """SELECT COUNT(*) AS total_records, MIN(`timestamp`) AS minimum_timestamp,
        MAX(`timestamp`) AS maximum_timestamp,
        (SELECT COUNT(*) FROM (SELECT `timestamp`, latitude, longitude FROM solar_energy
          GROUP BY `timestamp`, latitude, longitude HAVING COUNT(*) > 1) AS duplicates) AS duplicate_count
        FROM solar_energy"""
    return fetch_dataframe(get_database_config(), sql)
