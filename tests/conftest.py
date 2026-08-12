import copy
import pytest
from src.config import HOURLY_VARIABLES

@pytest.fixture
def payload():
    hourly = {"time": ["2024-08-12T00:00", "2024-08-12T01:00", "2024-08-12T02:00"]}
    for index, name in enumerate(HOURLY_VARIABLES):
        hourly[name] = [index + 1.0, index + 2.0, index + 3.0]
    return {"hourly": hourly}

@pytest.fixture
def copied_payload(payload):
    return copy.deepcopy(payload)
