USE test1;

SELECT COUNT(*) AS total_rows
FROM solar_energy;

SELECT
    MIN(timestamp) AS start_date,
    MAX(timestamp) AS end_date
FROM solar_energy;

SELECT *
FROM solar_energy
ORDER BY timestamp DESC
LIMIT 10;

SELECT *
FROM solar_energy
ORDER BY timestamp
LIMIT 10;

SELECT
    timestamp,
    latitude,
    longitude,
    COUNT(*) AS duplicate_count
FROM solar_energy
GROUP BY timestamp, latitude, longitude
HAVING COUNT(*) > 1;

SHOW FULL TABLES IN test1 WHERE TABLE_TYPE = 'VIEW';

SELECT *
FROM vw_daily_solar_summary
LIMIT 10;

SELECT *
FROM vw_hourly_solar_profile;