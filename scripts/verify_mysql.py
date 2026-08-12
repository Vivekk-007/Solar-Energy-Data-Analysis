"""Verify local or remote MySQL health and expected solar_energy records."""
from src.config import get_database_config
import mysql.connector
from mysql.connector import Error


def main() -> int:
    config = get_database_config()
    try:
        connection = mysql.connector.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
        )
    except Error as exc:
        raise SystemExit(f"Connection failed: {exc}") from exc

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total_records, MIN(`timestamp`) AS minimum_timestamp, MAX(`timestamp`) AS maximum_timestamp FROM solar_energy")
        result = cursor.fetchone() or {}
        cursor.execute("SELECT COUNT(*) AS duplicate_groups FROM (SELECT `timestamp`, latitude, longitude FROM solar_energy GROUP BY `timestamp`, latitude, longitude HAVING COUNT(*) > 1) duplicates")
        duplicates = cursor.fetchone().get("duplicate_groups", 0)
        print(f"database={result.get('total_records', 'n/a')}")
        print(f"minimum_timestamp={result.get('minimum_timestamp')}")
        print(f"maximum_timestamp={result.get('maximum_timestamp')}")
        print(f"duplicate_groups={duplicates}")
        return 0
    except Error as exc:
        raise SystemExit(f"Verification query failed: {exc}") from exc
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    raise SystemExit(main())
