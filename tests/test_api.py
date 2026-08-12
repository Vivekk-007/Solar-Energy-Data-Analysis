from unittest.mock import Mock
from src.api_client import OpenMeteoClient, OpenMeteoError

def test_api_response_parsing():
    response = Mock(); response.raise_for_status.return_value = None
    response.json.return_value = {"hourly": {"time": []}}
    session = Mock(); session.get.return_value = response
    result = OpenMeteoClient(session=session).fetch_historical("2024-01-01", "2024-01-02")
    assert result["hourly"]["time"] == []
    assert session.get.call_args.kwargs["params"]["timezone"] == "Asia/Kolkata"

def test_api_invalid_json_is_clear_error():
    response = Mock(); response.raise_for_status.return_value = None; response.json.side_effect = ValueError("bad json")
    session = Mock(); session.get.return_value = response
    try:
        OpenMeteoClient(session=session).fetch_historical("2024-01-01", "2024-01-02")
    except OpenMeteoError as exc:
        assert "invalid JSON" in str(exc)
    else:
        raise AssertionError("Expected OpenMeteoError")
