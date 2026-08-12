"""Transform a validated Open-Meteo payload into load-ready records."""
import pandas as pd
from .config import LATITUDE, LONGITUDE, RENAME_COLUMNS
from .validator import QualityReport

def transform_payload(payload: dict) -> tuple[pd.DataFrame, QualityReport]:
    frame = pd.DataFrame(payload["hourly"]).rename(columns=RENAME_COLUMNS)
    report = QualityReport(records_fetched=len(frame))
    frame["timestamp"] = pd.to_datetime(frame.pop("time"), errors="coerce")
    invalid_timestamps = int(frame["timestamp"].isna().sum())
    if invalid_timestamps:
        report.issues.append(f"Rejected {invalid_timestamps} rows with invalid timestamps")
        frame = frame.dropna(subset=["timestamp"])
    measurement_columns = list(RENAME_COLUMNS.values())
    for column in measurement_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    report.missing_values = int(frame[measurement_columns].isna().sum().sum())
    duplicate_count = int(frame.duplicated(subset=["timestamp"]).sum())
    if duplicate_count:
        report.issues.append(f"Removed {duplicate_count} duplicate timestamps")
        frame = frame.drop_duplicates(subset=["timestamp"], keep="first")
    frame["latitude"] = LATITUDE
    frame["longitude"] = LONGITUDE
    ordered = ["timestamp", "latitude", "longitude"] + measurement_columns
    frame = frame[ordered].sort_values("timestamp").reset_index(drop=True)
    report.records_validated = len(frame)
    report.records_rejected = invalid_timestamps
    report.duplicates_removed = duplicate_count
    if not frame.empty:
        report.minimum_timestamp = frame["timestamp"].min().strftime("%Y-%m-%d %H:%M:%S")
        report.maximum_timestamp = frame["timestamp"].max().strftime("%Y-%m-%d %H:%M:%S")
    return frame, report

def prepare_database_records(frame: pd.DataFrame) -> list[tuple]:
    columns = ["timestamp", "latitude", "longitude"] + list(RENAME_COLUMNS.values())
    records = []
    for row in frame[columns].itertuples(index=False, name=None):
        records.append(tuple(None if pd.isna(value) else value.to_pydatetime() if hasattr(value, "to_pydatetime") else value for value in row))
    return records
