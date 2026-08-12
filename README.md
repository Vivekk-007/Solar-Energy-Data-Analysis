# Solar Energy Data Analysis and Reporting with Power BI & MySQL

## Project Overview

This project extracts real hourly weather and solar-irradiance measurements for Jabalpur, Madhya Pradesh from Open-Meteo, validates and transforms them, and idempotently loads them into MySQL for Power BI reporting. It does not claim that irradiance measurements are plant-generation measurements.

## Business Problem

Solar planning and reporting need a consistent view of irradiance and weather conditions. This pipeline provides a reproducible analytical data set for that purpose.

## Project Objectives

Collect approximately two complete years of hourly data, enforce data quality, prevent duplicate loads, expose Power BI-friendly summaries, and clearly separate measured values from modelled financial metrics.

## Architecture

```mermaid
flowchart LR
    A[Open-Meteo Historical API] --> B[Python API Client] --> C[Validation] --> D[Transformation] --> E[MySQL test1]
    E --> F[solar_energy] --> G[SQL Views] --> H[Streamlit dashboard]
    F --> I[Optional Power BI]
```

## Technology Stack

Python, Requests, pandas, Plotly, Streamlit, mysql-connector-python, pytest, MySQL, and optional Power BI Desktop.

## Data Source

[Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api), queried without an API key. The API request asks for temperature, humidity, cloud cover, wind speed, shortwave/direct/diffuse radiation, DNI, GTI, and sunshine duration.

## API Configuration

The client uses `https://archive-api.open-meteo.com/v1/archive`, a 60-second timeout, `Asia/Kolkata`, latitude `23.1815`, longitude `79.9864`, tilt `23°`, and azimuth `0°` for GTI.

## Historical Dataset

The configured inclusive period is 2024-08-12 through 2026-08-11 at hourly frequency. The program reports the actual returned count; it never assumes a fixed count.

## Jabalpur Location

Jabalpur, Madhya Pradesh, India (`23.1815`, `79.9864`) is the sole pipeline location.

## ETL Pipeline

`python -m src.main` runs Extract → Validate → Transform → Load → Verify. API errors, malformed fields, invalid timestamps, and MySQL transaction errors are surfaced with readable messages. Re-running safely upserts by timestamp and coordinates.

## Data Validation

Raw payload validation requires all hourly arrays, equal array lengths, valid timestamps, and numeric-or-null measurements. Transformation sorts rows, removes duplicate timestamps, and reports counts, timestamps, nulls, rejections, and duplicate removals.

## MySQL Schema

`sql/init.sql` creates database `test1` and table `solar_energy`. The unique key is `timestamp, latitude, longitude`; numeric measurements are nullable to preserve source missingness.

## Database Views

`sql/views.sql` creates `vw_daily_solar_summary`, `vw_monthly_solar_summary`, and `vw_hourly_solar_profile`, intended as Power BI import/direct-query sources.

## Project Structure

```text
src/       ETL modules
streamlit_app/  Streamlit dashboard, read-only query layer, calculations, charts, and UI components
sql/       idempotent schema and views
tests/     ETL and deterministic business-calculation tests
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Environment Configuration

Copy `.env.example` to `.env`, then set `MYSQL_PASSWORD`. Keep `.env` private; it is ignored by Git. No Open-Meteo API key is needed.

## Running the Pipeline

Run `.\.venv\Scripts\python.exe -m src.main`. A reachable MySQL service is required; initialization safely uses `CREATE ... IF NOT EXISTS` and creates no destructive operations.

## Streamlit Application

The primary interactive dashboard is Streamlit, built on the ETL-managed MySQL data. It reads only from MySQL; it never calls Open-Meteo during a dashboard load. Start it with:

```powershell
.\.venv\Scripts\activate
streamlit run streamlit_app/app.py
```

The sidebar provides the date filter and clearly labelled, configurable scenario assumptions: capacity, performance ratio, tariff, CAPEX, O&M rate, and CO₂ factor. The dashboard includes Executive & Business Overview, Solar Energy Performance, Weather Impact Analysis, Financial & ROI Simulator, and Operations & Decision Support. It also provides a data refresh control and a filtered CSV download.

Energy is always labelled **Estimated Energy Generation**, derived for each hourly record as `GTI / 1000 × capacity (kW) × performance ratio`. Annualized energy uses the selected days × 365.25. Revenue, O&M, net benefit, ROI, payback, specific yield, capacity factor, and avoided CO₂ are scenario calculations—not actual plant measurements or investment advice.

### Complete Dashboard Guide

The Streamlit application is the primary interactive layer for this project. It reads real hourly records from MySQL only; it does not create mock data, call Open-Meteo during page loads, or modify database records.

#### Shared sidebar controls

Every page uses these sidebar controls. The date range filters all KPIs, charts, rankings, correlations, and downloads.

| Control | Default | Explanation |
|---|---:|---|
| Analysis date range | 12 Aug 2024–11 Aug 2026 | Inclusive date filter, limited to the loaded historical period. |
| System capacity | 100 kW | Scenario capacity used in estimated-energy and financial calculations. |
| Performance ratio | 80% | Scenario multiplier for aggregate system performance/losses. |
| Electricity tariff | ₹8/kWh | Scenario tariff used for revenue calculations. |
| Installation cost (CAPEX) | ₹5,000,000 | Scenario initial cost used for O&M, ROI, and payback. |
| O&M rate | 2% of CAPEX | Annual operating-and-maintenance scenario assumption. |
| CO₂ emission factor | 0.70 kg/kWh | Scenario factor for the estimated avoided-emissions calculation. |
| Refresh Data | — | Clears the 15-minute query cache and reloads data from MySQL. It does not run the ETL. |
| Download filtered CSV | — | Exports selected hourly timestamps plus weather, radiation, DNI, GTI, and sunshine-duration fields. |

All financial values and the emissions factor are configurable scenario assumptions, not actual plant, market, or official emissions data.

#### 01 Executive & Business Overview

This management summary presents the selected period's resource quality and scenario outcomes.

| KPI or chart | Explanation |
|---|---|
| Average Solar Radiation | Mean of daily average `solar_radiation`, in W/m². |
| Peak Solar Radiation | Highest daily `solar_radiation`, in W/m². |
| Annual Energy Potential | Annualized estimated energy, displayed in MWh. |
| Estimated Annual Revenue | Annualized estimated energy × selected electricity tariff. |
| Estimated Payback | CAPEX ÷ annual net benefit; `N/A` when benefit is zero or negative. |
| Annual CO₂ Avoided | Annualized estimated energy × selected CO₂ factor, displayed in tonnes. |
| Monthly Solar Resource Trend | Monthly average solar radiation, showing seasonal resource patterns. |
| Monthly Estimated Energy Generation | Modelled monthly energy based on hourly GTI, capacity, and performance ratio. |
| Monthly Estimated Revenue | Modelled monthly energy × tariff. |
| Business Scenario Summary | The capacity, performance ratio, tariff, CAPEX, and O&M inputs currently in use. |

#### 02 Solar Energy Performance

This page provides detailed solar-resource trends and indicators.

| KPI or chart | Explanation |
|---|---|
| Average Solar Radiation | Mean daily horizontal shortwave solar radiation. |
| Average DNI | Mean daily Direct Normal Irradiance (direct radiation perpendicular to the sun). |
| Average GTI | Mean daily Global Tilted Irradiance; this is used by the energy model. |
| Peak Solar Radiation | Highest daily radiation observed in the selected range. |
| Specific Yield | Annualized estimated energy ÷ selected capacity, in kWh/kW/year. |
| Capacity Factor | Annualized estimated energy ÷ (capacity × 8,760 hours), as a percentage. |
| Hourly Solar Radiation / DNI / GTI | Interactive hourly time-series charts for the selected date range. |
| Average Radiation and GTI by Hour | Hour-of-day averages that identify typical strong solar hours. |
| Monthly Solar Resource | Monthly average solar-radiation trend. |

#### 03 Weather Impact Analysis

This page compares weather fields with hourly solar radiation.

| Item | Explanation |
|---|---|
| Average Temperature, Humidity, Cloud Cover, Wind Speed | Selected-period descriptive averages for weather measurements. |
| Correlation cards | Pearson correlation (`r`) of cloud cover, temperature, humidity, and wind speed against solar radiation. Values range from -1 to +1. |
| Scatter plots | Individual hourly observations for each weather field versus solar radiation. |
| Automated insight | Labels the calculated result as weak/moderate/strong and positive/negative. |

Negative correlation means the variables generally move in opposite directions in this historical data; positive correlation means they generally move together. Correlation does not imply causation.

#### 04 Financial & ROI Simulator

This page converts selected historical GTI into a transparent business scenario.

| KPI or chart | Explanation |
|---|---|
| Estimated Annual Energy | Selected-period estimated energy annualized to 365.25 days. |
| Estimated Annual Revenue | Annualized energy × tariff. |
| Annual O&M | CAPEX × O&M rate. |
| Annual Net Benefit | Annual revenue − annual O&M. |
| Estimated ROI | Annual net benefit ÷ CAPEX. |
| Estimated Payback | CAPEX ÷ annual net benefit; not shown when benefit is not positive. |
| Monthly Energy, Revenue, and Net Benefit | Modelled monthly values; monthly net benefit subtracts one twelfth of annual O&M each month. |
| Revenue Sensitivity: Capacity vs Tariff | Heatmap for capacities 50, 100, 150, 200, 250, and 500 kW and tariffs ₹4, ₹6, ₹8, ₹10, and ₹12/kWh. Values are calculated from selected real GTI data. |
| CAPEX Sensitivity: Payback Period | Payback at 60%, 80%, 100%, 120%, and 150% of selected CAPEX, using the same annual net benefit. |

The simulator does not model financing costs, taxes, degradation, equipment replacement, downtime, insurance, detailed maintenance, tariff changes, actual plant losses, inverter efficiency, panel orientation, or shading. It is not investment advice.

#### 05 Operations & Decision Support

This page supports planning with rankings and data-quality information.

| Item | Explanation |
|---|---|
| Best Solar Hours | Hour-of-day solar profile sorted by average solar radiation; the top three include average radiation, DNI, and GTI. |
| Best Solar Months | Selected months ranked by average solar radiation, with peak radiation, average DNI, and GTI. |
| Highest Solar-Resource Days | Top ten days by daily average solar radiation, including peak radiation, DNI, GTI, and cloud cover. |
| Lowest Solar-Resource Days | Bottom ten days by daily average solar radiation. |
| Data Quality | Selected-range record count, first/last timestamp, duplicate timestamp count, and missing measurement count. |
| Data Source | Shows Open-Meteo, Jabalpur, coordinates, and hourly frequency. |

#### Calculation definitions

The app always calls modelled output **Estimated Energy Generation** because the source dataset contains irradiance and weather data, not physical plant meter readings.

```text
Hourly estimated energy (kWh)
  = GTI (W/m²) / 1000 × system capacity (kW) × performance ratio

Selected-period estimated energy = sum of hourly estimated energy
Annualized energy = selected-period energy / selected days × 365.25
Estimated annual revenue = annualized energy × tariff
Annual O&M = CAPEX × O&M rate
Annual net benefit = annual revenue − annual O&M
Estimated payback = CAPEX / annual net benefit, when benefit > 0
Estimated annual ROI = annual net benefit / CAPEX
Estimated CO₂ avoided (kg) = annualized energy × CO₂ factor
Specific yield = annualized energy / capacity
Capacity factor = annualized energy / (capacity × 8,760)
```

#### Database, cache, and error handling

- Raw hourly data supports detailed time series, weather correlations, energy calculations, data quality, and CSV export.
- Daily SQL summaries support daily KPIs and highest/lowest-day rankings.
- Monthly and hourly profile aggregations support resource trends and operational rankings.
- Query results use `st.cache_data` with a 900-second lifetime; **Refresh Data** clears this cache.
- If MySQL is unavailable, the app shows a clear connection message and does not expose credentials or a technical stack trace.
- The dashboard is read-only. The ETL remains responsible for acquiring, validating, transforming, and loading data.

For raw field descriptions, units, null handling, and source context, see [DATA_DICTIONARY.md](DATA_DICTIONARY.md).

## MySQL and Environment

Start the local MySQL Server before ETL or Streamlit. Configure these values in `.env` (never commit it): `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DATABASE`. `.env` is already excluded by `.gitignore`.

## Testing

```powershell
pytest
```

The test suite does not require MySQL or live internet. It covers the existing ETL plus energy, annualization, revenue, O&M, net benefit, ROI, payback, CO₂, specific-yield, and capacity-factor calculations.

## Deployment

For a cloud Streamlit deployment, use a cloud-accessible MySQL instance; Streamlit Cloud cannot directly reach a local MySQL server. Configure the same `MYSQL_*` environment variables as deployment secrets, install from `requirements.txt`, and use `streamlit_app/app.py` as the entry point. Power BI remains available as an optional reporting layer.

## MySQL Verification

```sql
SELECT COUNT(*) FROM solar_energy;
SELECT MIN(`timestamp`), MAX(`timestamp`) FROM solar_energy;
SELECT COUNT(*) FROM solar_energy WHERE latitude=23.1815 AND longitude=79.9864;
SELECT `timestamp`, latitude, longitude, COUNT(*) FROM solar_energy GROUP BY `timestamp`, latitude, longitude HAVING COUNT(*) > 1;
SELECT * FROM solar_energy ORDER BY `timestamp` LIMIT 10;
```

## Power BI Connection

In Power BI Desktop choose Get Data → MySQL database, server `localhost`, database `test1`, then select the three views. Install the MySQL connector if Power BI asks.

## Dashboard Design

- Executive Overview: average/peak solar radiation, average DNI/GTI, total sunshine duration, and temperature.
- Solar Performance: radiation, DNI, GTI, and daily radiation over date.
- Weather Impact: cloud cover, temperature, humidity, and wind speed compared with solar radiation.
- Hourly Solar Pattern: `vw_hourly_solar_profile`, hour of day versus average solar radiation.
- Energy & Sustainability: labelled estimated/modelled metrics only.

## Financial Analysis

Create Power BI parameters for `installed_capacity_kw`, `system_efficiency`, `electricity_tariff`, `installation_cost`, and `annual_maintenance_cost`. A transparent model may estimate energy as irradiance-derived peak-sun-hours × capacity × efficiency; revenue as estimated energy × tariff; payback as installation cost ÷ annual net benefit. These are estimates, not API measurements.

## Sustainability Analysis

Use a configurable `emission_factor` parameter: estimated CO₂ avoided = estimated energy × emission factor. Label this as modelled and document the factor’s source and unit in the report.

## Testing

Run `pytest`. Tests mock HTTP and cover response parsing, missing fields, length validation, transformation, duplicate removal, and database record preparation. They do not require MySQL or live internet.

## Error Handling

The pipeline handles timeouts, connection and HTTP errors, invalid JSON, schema issues, timestamp/numeric issues, unavailable MySQL, authentication failures, and transaction rollback.

## Security

Credentials come only from environment variables. Passwords are never written to source, SQL, README, or logs.

## Future Improvements

Add scheduled incremental loads, database integration tests, alerts for quality thresholds, capacity-specific model calibration, and a checked-in Power BI template when Power BI tooling is available.
