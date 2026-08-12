"""Executable extract, validate, transform, load, verify pipeline."""
from pathlib import Path
from .api_client import OpenMeteoClient, OpenMeteoError
from .config import END_DATE, START_DATE, get_database_config
from .database import DatabaseError, initialize_database, upsert_records, verify_load
from .logger import get_logger
from .transformer import prepare_database_records, transform_payload
from .validator import ValidationError, validate_api_payload

def print_report(report) -> None:
    print("\n----------------------------------------\nDATA QUALITY REPORT\n----------------------------------------")
    print(f"Records fetched: {report.records_fetched}\nRecords validated: {report.records_validated}\nRecords rejected: {report.records_rejected}\nDuplicates removed: {report.duplicates_removed}\nMissing values: {report.missing_values}\nMinimum timestamp: {report.minimum_timestamp}\nMaximum timestamp: {report.maximum_timestamp}")
    print("----------------------------------------")

def main() -> int:
    log = get_logger(); log.info("Pipeline started")
    try:
        log.info("Starting Open-Meteo historical API request")
        payload = OpenMeteoClient().fetch_historical(START_DATE, END_DATE)
        fetched = validate_api_payload(payload)
        log.info("API request completed; received %s hourly records", fetched)
        frame, report = transform_payload(payload)
        print_report(report)
        for issue in report.issues: log.warning(issue)
        config = get_database_config()
        log.info("Initializing MySQL database and views")
        initialize_database(config, Path(__file__).resolve().parents[1] / "sql")
        changed = upsert_records(config, prepare_database_records(frame))
        log.info("Database insert/update completed; affected rows: %s", changed)
        result = verify_load(config)
        log.info("Verified MySQL rows=%s, duplicates=%s", result["row_count"], result["duplicate_groups"])
        print(f"MySQL verification: rows={result['row_count']}, duplicates={result['duplicate_groups']}")
        log.info("Pipeline completed successfully")
        return 0
    except (OpenMeteoError, ValidationError, DatabaseError, ValueError) as exc:
        log.error("Pipeline failed: %s", exc)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
