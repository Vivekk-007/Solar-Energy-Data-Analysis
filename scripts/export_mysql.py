"""Export local MySQL schema and data for migration to a remote instance."""
from pathlib import Path
from datetime import datetime
from src.config import get_database_config
import mysql.connector
from mysql.connector import Error

OUTPUT_PATH = Path(__file__).resolve().parents[0] / "test1_export.sql"
TABLE_NAME = "solar_energy"
VIEWS = ["vw_daily_solar_summary", "vw_monthly_solar_summary", "vw_hourly_solar_profile"]


def quote(value):
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def export():
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

    output = OUTPUT_PATH
    with output.open("w", encoding="utf-8") as handle:
        handle.write(f"-- Export generated {datetime.utcnow().isoformat()}Z\n")
        handle.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
        handle.write(f"CREATE DATABASE IF NOT EXISTS `{config.database}`;\nUSE `{config.database}`;\n\n")

        cursor = connection.cursor()
        try:
            cursor.execute(f"SHOW CREATE TABLE `{TABLE_NAME}`")
            row = cursor.fetchone()
            if row is None:
                raise SystemExit(f"Table {TABLE_NAME} not found")
            handle.write(row[1] + ";\n\n")

            for view in VIEWS:
                cursor.execute(f"SHOW CREATE VIEW `{view}`")
                row = cursor.fetchone()
                if row is None:
                    raise SystemExit(f"View {view} not found")
                handle.write(row[1] + ";\n\n")

            cursor.execute(f"SELECT * FROM `{TABLE_NAME}` ORDER BY `timestamp`")
            columns = [desc[0] for desc in cursor.description]
            column_list = ", ".join(f"`{col}`" for col in columns)
            for row in cursor:
                values = ", ".join(quote(value) for value in row)
                handle.write(f"INSERT INTO `{TABLE_NAME}` ({column_list}) VALUES ({values});\n")
        finally:
            cursor.close()
            connection.close()

    print(f"Export complete: {output}")


if __name__ == "__main__":
    export()
