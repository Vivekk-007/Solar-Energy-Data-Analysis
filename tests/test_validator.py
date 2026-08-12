import pytest
from src.validator import ValidationError, validate_api_payload

def test_valid_payload_returns_count(payload):
    assert validate_api_payload(payload) == 3

def test_missing_api_field_fails(copied_payload):
    del copied_payload["hourly"]["direct_normal_irradiance"]
    with pytest.raises(ValidationError, match="direct_normal_irradiance"):
        validate_api_payload(copied_payload)

def test_mismatched_lengths_fail(copied_payload):
    copied_payload["hourly"]["temperature_2m"] = [22]
    with pytest.raises(ValidationError, match="temperature_2m"):
        validate_api_payload(copied_payload)
