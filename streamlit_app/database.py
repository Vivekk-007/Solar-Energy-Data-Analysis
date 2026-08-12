"""Read-only MySQL access for the Streamlit dashboard."""
from typing import Any

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
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        import pandas as pd
        return pd.DataFrame(rows)
    except Error as exc:
        raise DashboardDatabaseError(str(exc)) from exc
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
