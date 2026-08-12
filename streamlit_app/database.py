"""Read-only MySQL access for the Streamlit dashboard."""
from typing import Any
from decimal import Decimal

import mysql.connector
from mysql.connector import Error

from .config import DatabaseConfig


class DashboardDatabaseError(RuntimeError):
    """Raised when a dashboard query cannot be completed."""


def _diagnose_connection_error(exc: Error, database: str) -> str:
    errno = getattr(exc, "errno", None)
    message = str(exc)
    if errno == 2003 or errno == 2005:
        return "Database host or port is unreachable. Configure a remotely accessible MySQL server for cloud deployment."
    if errno == 1045:
        return "Database authentication failed. Verify the configured MySQL username and password."
    if errno == 1049:
        return f"Database '{database}' was not found on the configured MySQL server."
    if errno == 2006 or errno == 2013:
        return "The database connection was lost. Please verify network connectivity and the MySQL server status."
    if "Can't connect" in message or "Connection refused" in message:
        return "Unable to connect to the configured MySQL host. Ensure the server is reachable from this environment."
    return "Database connection failed. Please verify the configured MySQL host, port, user, password, and database."


def _diagnose_query_error(exc: Error) -> str:
    errno = getattr(exc, "errno", None)
    if errno == 1146 or errno == 1051:
        return "A required table or view is missing. Ensure the database schema and views are initialized."
    if errno == 1142 or errno == 1044:
        return "Database access is not permitted. Verify the configured MySQL user has sufficient privileges."
    return "Database query failed. Please verify the data source, schema, and SQL query."


def fetch_dataframe(config: DatabaseConfig, sql: str, params: tuple[Any, ...] = ()): 
    """Run a read-only query and always release its MySQL resources."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host=config.host, port=config.port, user=config.user,
            password=config.password, database=config.database,
        )
    except Error as exc:
        raise DashboardDatabaseError(_diagnose_connection_error(exc, config.database)) from exc

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        import pandas as pd
        frame = pd.DataFrame(rows)
        # mysql-connector returns DECIMAL values as Decimal objects. Dashboard
        # calculations combine these measurements with float scenario inputs.
        return frame.apply(lambda column: column.map(lambda value: float(value) if isinstance(value, Decimal) else value))
    except Error as exc:
        raise DashboardDatabaseError(_diagnose_query_error(exc)) from exc
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


def get_database_health(config: DatabaseConfig) -> dict[str, str | int | None]:
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host=config.host, port=config.port, user=config.user,
            password=config.password, database=config.database,
        )
    except Error as exc:
        raise DashboardDatabaseError(_diagnose_connection_error(exc, config.database)) from exc

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DATABASE() AS database_name, COUNT(*) AS total_records, MIN(`timestamp`) AS minimum_timestamp, MAX(`timestamp`) AS maximum_timestamp FROM solar_energy")
        result = cursor.fetchone() or {}
        return {
            "database_name": result.get("database_name"),
            "total_records": int(result.get("total_records", 0) or 0),
            "minimum_timestamp": result.get("minimum_timestamp"),
            "maximum_timestamp": result.get("maximum_timestamp"),
        }
    except Error as exc:
        raise DashboardDatabaseError(_diagnose_query_error(exc)) from exc
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
