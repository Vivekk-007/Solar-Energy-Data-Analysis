from src.transformer import prepare_database_records, transform_payload

def test_transformation_maps_columns_and_coordinates(payload):
    frame, report = transform_payload(payload)
    assert {"timestamp", "temperature", "humidity", "solar_radiation", "dni", "gti", "latitude", "longitude"} <= set(frame.columns)
    assert len(frame) == 3 and report.records_validated == 3
    assert frame["latitude"].iloc[0] == 23.1815

def test_duplicate_removal_and_database_preparation(copied_payload):
    copied_payload["hourly"]["time"][2] = copied_payload["hourly"]["time"][1]
    frame, report = transform_payload(copied_payload)
    records = prepare_database_records(frame)
    assert len(frame) == 2 and report.duplicates_removed == 1
    assert len(records) == 2 and len(records[0]) == 13
