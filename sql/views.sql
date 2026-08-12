USE test1;

CREATE OR REPLACE VIEW vw_daily_solar_summary AS
SELECT DATE(`timestamp`) AS `date`, AVG(temperature) AS average_temperature,
       AVG(humidity) AS average_humidity, AVG(cloud_cover) AS average_cloud_cover,
       AVG(solar_radiation) AS average_solar_radiation, MAX(solar_radiation) AS peak_solar_radiation,
       AVG(dni) AS average_dni, AVG(gti) AS average_gti, SUM(sunshine_duration) AS total_sunshine_duration
FROM solar_energy GROUP BY DATE(`timestamp`);

CREATE OR REPLACE VIEW vw_monthly_solar_summary AS
SELECT YEAR(`timestamp`) AS `year`, MONTH(`timestamp`) AS `month`, AVG(temperature) AS average_temperature,
       AVG(solar_radiation) AS average_solar_radiation, MAX(solar_radiation) AS peak_solar_radiation,
       AVG(dni) AS average_dni, AVG(gti) AS average_gti, SUM(sunshine_duration) AS total_sunshine_duration
FROM solar_energy GROUP BY YEAR(`timestamp`), MONTH(`timestamp`);

CREATE OR REPLACE VIEW vw_hourly_solar_profile AS
SELECT HOUR(`timestamp`) AS hour_of_day, AVG(temperature) AS average_temperature,
       AVG(solar_radiation) AS average_solar_radiation, AVG(dni) AS average_dni,
       AVG(gti) AS average_gti, AVG(cloud_cover) AS average_cloud_cover
FROM solar_energy GROUP BY HOUR(`timestamp`);
