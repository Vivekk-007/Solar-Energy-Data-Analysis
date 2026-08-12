"""Read-only MySQL access for the Streamlit dashboard."""
from typing import Any
from decimal import Decimal

import mysql.connector
from mysql.connector import Error

from .config import DatabaseConfig


class DashboardDatabaseError(RuntimeError):
    """Raised when a dashboard query cannot be completed."""


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
        raise DashboardDatabaseError(
            "Database connection failed. Please verify the configured MySQL host, port, user, password, and database."
        ) from exc

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
        raise DashboardDatabaseError(
            "Database query failed. Please verify the data source and query."
        ) from exc
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
