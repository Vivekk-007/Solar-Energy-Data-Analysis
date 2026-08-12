CREATE DATABASE IF NOT EXISTS test1;
USE test1;

CREATE TABLE IF NOT EXISTS solar_energy (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    `timestamp` DATETIME NOT NULL,
    latitude DECIMAL(10,6) NOT NULL,
    longitude DECIMAL(10,6) NOT NULL,
    temperature DECIMAL(7,3) NULL,
    humidity DECIMAL(6,3) NULL,
    cloud_cover DECIMAL(6,3) NULL,
    wind_speed DECIMAL(8,3) NULL,
    solar_radiation DECIMAL(10,3) NULL,
    direct_radiation DECIMAL(10,3) NULL,
    diffuse_radiation DECIMAL(10,3) NULL,
    dni DECIMAL(10,3) NULL,
    gti DECIMAL(10,3) NULL,
    sunshine_duration DECIMAL(12,3) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_solar_energy_timestamp_location UNIQUE (`timestamp`, latitude, longitude),
    INDEX idx_solar_energy_location_timestamp (latitude, longitude, `timestamp`)
) ENGINE=InnoDB;
