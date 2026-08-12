# Solar Energy Dataset Data Dictionary

This project stores hourly historical weather and solar-irradiance data for **Jabalpur, Madhya Pradesh, India**. The data originates from the Open-Meteo Historical API and is loaded into the MySQL table `test1.solar_energy` by the existing ETL pipeline.

Important: irradiance values describe the available solar resource and weather conditions. They are **not measured electricity output from a physical solar plant**.

| Column | Type | Unit | Description |
|---|---|---:|---|
| `id` | BIGINT | — | Auto-incremented internal identifier for the database row. |
| `timestamp` | DATETIME | Local time | Timestamp for the hourly observation in the `Asia/Kolkata` timezone. One row represents one hour. |
| `latitude` | DECIMAL | Degrees | Latitude of the observation location: `23.1815`. |
| `longitude` | DECIMAL | Degrees | Longitude of the observation location: `79.9864`. |
| `temperature` | DECIMAL | °C | Air temperature measured at 2 metres above ground level. |
| `humidity` | DECIMAL | % | Relative humidity at 2 metres above ground level. |
| `cloud_cover` | DECIMAL | % | Portion of the sky estimated to be covered by clouds. `0` means clear sky and `100` means fully overcast. |
| `wind_speed` | DECIMAL | km/h | Wind speed measured at 10 metres above ground level. |
| `solar_radiation` | DECIMAL | W/m² | Shortwave solar radiation received on a horizontal surface. This is the primary solar-resource measure used in the dashboard. |
| `direct_radiation` | DECIMAL | W/m² | Solar radiation reaching the surface directly from the sun, excluding light scattered by the atmosphere. |
| `diffuse_radiation` | DECIMAL | W/m² | Solar radiation scattered by clouds, aerosols, and the atmosphere before reaching the surface. |
| `dni` | DECIMAL | W/m² | Direct Normal Irradiance: direct solar radiation on a surface always perpendicular to the sun’s rays. It is useful for concentrating solar and solar-resource analysis. |
| `gti` | DECIMAL | W/m² | Global Tilted Irradiance: total solar irradiance on the configured tilted plane (tilt `23°`, azimuth `0°`). The dashboard uses GTI to model estimated energy generation. |
| `sunshine_duration` | DECIMAL | seconds | Sunshine duration recorded during the hourly interval. It indicates how long direct sunshine was present. |
| `created_at` | TIMESTAMP | Database server time | Time at which the row was first created in MySQL. |

## Time Period and Frequency

- Location: Jabalpur, Madhya Pradesh, India
- Coordinates: `23.1815`, `79.9864`
- Timezone: `Asia/Kolkata`
- Frequency: hourly
- Historical period: 12 August 2024 through 11 August 2026

## Data Quality and Missing Values

Measurement columns are nullable. A `NULL` value means the source did not provide a usable value for that observation; it does not mean zero solar radiation or zero weather measurement. The ETL keeps source missingness and enforces uniqueness using `timestamp`, `latitude`, and `longitude`.

## Dashboard Energy Estimate

The Streamlit dashboard calculates an **estimated** hourly energy value using:

```text
Estimated energy (kWh) = GTI (W/m²) / 1000 × system capacity (kW) × performance ratio
```

This is a scenario model based on historical irradiance, not actual meter data. Actual generation depends on installation-specific factors such as panel orientation, shading, equipment efficiency, downtime, degradation, and maintenance.
