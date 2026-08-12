"""Validation for raw Open-Meteo payloads and transformed records."""
from dataclasses import dataclass, field
from typing import Any
import pandas as pd
from .config import HOURLY_VARIABLES

class ValidationError(ValueError):
    pass

@dataclass
class QualityReport:
    records_fetched: int = 0
    records_validated: int = 0
    records_rejected: int = 0
    duplicates_removed: int = 0
    missing_values: int = 0
    minimum_timestamp: str | None = None
    maximum_timestamp: str | None = None
    issues: list[str] = field(default_factory=list)

def validate_api_payload(payload: dict[str, Any]) -> int:
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise ValidationError("Response has no valid hourly object")
    required = ("time",) + HOURLY_VARIABLES
    missing = [key for key in required if key not in hourly]
    if missing:
        raise ValidationError(f"Response is missing required hourly fields: {', '.join(missing)}")
    if not isinstance(hourly["time"], list):
        raise ValidationError("hourly.time must be an array")
    expected = len(hourly["time"])
    if expected == 0:
        raise ValidationError("Response contains no hourly records")
    for key in required:
        values = hourly[key]
        if not isinstance(values, list) or len(values) != expected:
            raise ValidationError(f"hourly.{key} must be an array of {expected} values")
    timestamps = pd.to_datetime(hourly["time"], errors="coerce")
    if timestamps.isna().any():
        raise ValidationError("Response contains invalid timestamps")
    for key in HOURLY_VARIABLES:
        values = pd.to_numeric(pd.Series(hourly[key]), errors="coerce")
        # Nulls are allowed and reported; non-null unparseable values are not.
        for original, converted in zip(hourly[key], values, strict=True):
            if original is not None and pd.isna(converted):
                raise ValidationError(f"hourly.{key} contains a non-numeric value")
    return expected

def assess_dataframe(frame: pd.DataFrame) -> QualityReport:
    report = QualityReport(records_fetched=len(frame))
    report.missing_values = int(frame.isna().sum().sum())
    report.records_validated = len(frame)
    if not frame.empty:
        report.minimum_timestamp = frame["timestamp"].min().strftime("%Y-%m-%d %H:%M:%S")
        report.maximum_timestamp = frame["timestamp"].max().strftime("%Y-%m-%d %H:%M:%S")
    return report
