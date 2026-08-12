"""MySQL setup, idempotent upserts, and verification queries."""
from pathlib import Path
from typing import Any
import mysql.connector
from mysql.connector import Error
from .config import DatabaseConfig

class DatabaseError(RuntimeError):
    pass

INSERT_COLUMNS = ("timestamp", "latitude", "longitude", "temperature", "humidity", "cloud_cover", "wind_speed", "solar_radiation", "direct_radiation", "diffuse_radiation", "dni", "gti", "sunshine_duration")
UPSERT_SQL = f"""INSERT INTO solar_energy ({', '.join('`' + c + '`' for c in INSERT_COLUMNS)})
VALUES ({', '.join(['%s'] * len(INSERT_COLUMNS))})
ON DUPLICATE KEY UPDATE temperature=VALUES(temperature), humidity=VALUES(humidity), cloud_cover=VALUES(cloud_cover), wind_speed=VALUES(wind_speed), solar_radiation=VALUES(solar_radiation), direct_radiation=VALUES(direct_radiation), diffuse_radiation=VALUES(diffuse_radiation), dni=VALUES(dni), gti=VALUES(gti), sunshine_duration=VALUES(sunshine_duration)"""

def _connect(config: DatabaseConfig, include_database: bool = True):
    settings: dict[str, Any] = {"host": config.host, "port": config.port, "user": config.user, "password": config.password}
    if include_database:
        settings["database"] = config.database
    try:
        return mysql.connector.connect(**settings)
    except Error as exc:
        raise DatabaseError(f"MySQL connection failed: {exc}") from exc

def initialize_database(config: DatabaseConfig, sql_directory: Path) -> None:
    connection = _connect(config, include_database=False)
    cursor = connection.cursor()
    try:
        for path in (sql_directory / "init.sql", sql_directory / "views.sql"):
            for statement in path.read_text(encoding="utf-8").split(";"):
                if statement.strip(): cursor.execute(statement)
        connection.commit()
    except Error as exc:
        connection.rollback()
        raise DatabaseError(f"Database initialization failed: {exc}") from exc
    finally:
        cursor.close(); connection.close()

def upsert_records(config: DatabaseConfig, records: list[tuple]) -> int:
    connection = _connect(config)
    cursor = connection.cursor()
    try:
        cursor.executemany(UPSERT_SQL, records)
        connection.commit()
        return cursor.rowcount
    except Error as exc:
        connection.rollback()
        raise DatabaseError(f"MySQL upsert failed: {exc}") from exc
    finally:
        cursor.close(); connection.close()

def verify_load(config: DatabaseConfig) -> dict[str, Any]:
    connection = _connect(config); cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS row_count, MIN(`timestamp`) AS minimum_timestamp, MAX(`timestamp`) AS maximum_timestamp FROM solar_energy WHERE latitude=%s AND longitude=%s", (23.1815, 79.9864))
        result = cursor.fetchone() or {}
        cursor.execute("SELECT COUNT(*) AS duplicate_groups FROM (SELECT `timestamp`, latitude, longitude FROM solar_energy GROUP BY `timestamp`, latitude, longitude HAVING COUNT(*) > 1) duplicates")
        result["duplicate_groups"] = (cursor.fetchone() or {})["duplicate_groups"]
        return result
    except Error as exc:
        raise DatabaseError(f"MySQL verification failed: {exc}") from exc
    finally:
        cursor.close(); connection.close()
