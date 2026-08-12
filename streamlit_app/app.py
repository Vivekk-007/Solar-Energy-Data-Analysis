"""Entry point: streamlit run streamlit_app/app.py."""
from datetime import date
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from streamlit_app.calculations import correlation_label, model_metrics, monthly_model
from streamlit_app.charts import bar, heatmap, line, scatter
from streamlit_app.components import financial_disclaimer, metric, section
from streamlit_app.config import DATA_SOURCE, LATITUDE, LOCATION, LONGITUDE, MAX_DATE, MIN_DATE, get_database_config
from streamlit_app.database import DashboardDatabaseError, get_database_health
from streamlit_app.queries import load_daily_summary, load_hourly_profile, load_monthly_summary, load_solar_data
from streamlit_app.styles import apply_styles

st.set_page_config(page_title="Solar Energy & Business Analytics", page_icon="☀️", layout="wide")
apply_styles()
LOGGER = logging.getLogger("solar_dashboard")


def fmt_inr(value: float) -> str: return f"₹{value:,.0f}"
def fmt_num(value: float, unit: str = "") -> str: return f"{value:,.2f}{unit}"


def sidebar() -> tuple[date, date, dict[str, float]]:
    st.sidebar.header("Solar Energy Platform")
    st.sidebar.caption(f"{LOCATION}\n\n{LATITUDE}, {LONGITUDE}")
    start, end = st.sidebar.date_input("Analysis date range", value=(MIN_DATE, MAX_DATE), min_value=MIN_DATE, max_value=MAX_DATE)
    st.sidebar.divider(); st.sidebar.subheader("Business assumptions")
    st.sidebar.caption("Scenario inputs — not actual project costs or tariffs.")
    scenario = {
        "capacity_kw": st.sidebar.number_input("System capacity (kW)", 1.0, 10000.0, 100.0, 10.0),
        "performance_ratio": st.sidebar.slider("Performance ratio", 0.1, 1.0, 0.80, 0.01),
        "tariff": st.sidebar.number_input("Electricity tariff (₹/kWh)", 0.0, 1000.0, 8.0, 0.5),
        "capex": st.sidebar.number_input("Installation cost (₹)", 0.0, 1_000_000_000.0, 5_000_000.0, 100_000.0),
        "om_rate": st.sidebar.slider("O&M rate (% of CAPEX)", 0.0, 20.0, 2.0, 0.1) / 100,
        "co2_factor": st.sidebar.number_input("CO₂ emission factor (kg/kWh)", 0.0, 5.0, 0.70, 0.05),
    }
    if st.sidebar.button("Refresh Data", width="stretch"):
        st.cache_data.clear(); st.rerun()
    return start, end, scenario


def executive(raw, daily, monthly, metrics, scenario):
    st.title("SOLAR ENERGY & BUSINESS ANALYTICS")
    st.caption("Jabalpur | Aug 2024 – Aug 2026 · Historical irradiance and weather analytics")
    cols = st.columns(3)
    items = [("Average Solar Radiation", fmt_num(daily.average_solar_radiation.mean(), " W/m²")), ("Peak Solar Radiation", fmt_num(daily.peak_solar_radiation.max(), " W/m²")), ("Annual Energy Potential", fmt_num(metrics["annual_energy"] / 1000, " MWh")), ("Estimated Annual Revenue", fmt_inr(metrics["annual_revenue"])), ("Estimated Payback", "N/A" if metrics["payback"] is None else fmt_num(metrics["payback"], " years")), ("Annual CO₂ Avoided", fmt_num(metrics["co2"] / 1000, " t"))]
    for row in (items[:3], items[3:]):
        for col, (label, value) in zip(cols, row):
            with col: metric(label, value)
    section("Solar resource and business trend")
    a, b = st.columns(2)
    with a: st.plotly_chart(line(monthly, "period", "average_solar_radiation", "Monthly Solar Resource Trend", "Month", "Average solar radiation (W/m²)"), width="stretch")
    model = monthly_model(raw, scenario)
    with b: st.plotly_chart(line(model, "period", "energy_kwh", "Monthly Estimated Energy Generation", "Month", "Estimated energy (kWh)", "#2E8B57"), width="stretch")
    st.plotly_chart(line(model, "period", "revenue", "Monthly Estimated Revenue", "Month", "Estimated revenue (₹)", "#0B1F3A"), width="stretch")
    section("Business scenario summary")
    st.dataframe(pd.DataFrame({"Assumption": ["Capacity", "Performance ratio", "Tariff", "CAPEX", "O&M rate"], "Selected value": [f'{scenario["capacity_kw"]:,.0f} kW', f'{scenario["performance_ratio"]:.0%}', fmt_inr(scenario["tariff"]), fmt_inr(scenario["capex"]), f'{scenario["om_rate"]:.1%}']}), hide_index=True)


def performance(raw, daily, monthly, profile, metrics):
    st.title("Solar Energy Performance")
    cols = st.columns(3)
    values = [("Average Solar Radiation", fmt_num(daily.average_solar_radiation.mean(), " W/m²")), ("Average DNI", fmt_num(daily.average_dni.mean(), " W/m²")), ("Average GTI", fmt_num(daily.average_gti.mean(), " W/m²")), ("Peak Solar Radiation", fmt_num(daily.peak_solar_radiation.max(), " W/m²")), ("Specific Yield", fmt_num(metrics["specific_yield"], " kWh/kW/year")), ("Capacity Factor", fmt_num(metrics["capacity_factor"] * 100, "%"))]
    for row in (values[:3], values[3:]):
        for col, (label, value) in zip(cols, row):
            with col: metric(label, value)
    for column, title in [("solar_radiation", "Hourly Solar Radiation"), ("dni", "Hourly DNI"), ("gti", "Hourly GTI")]:
        st.plotly_chart(line(raw, "timestamp", column, title, "Timestamp", "W/m²"), width="stretch")
    a, b = st.columns(2)
    with a: st.plotly_chart(bar(profile, "hour_of_day", "average_solar_radiation", "Average Solar Radiation by Hour", "Hour", "W/m²"), width="stretch")
    with b: st.plotly_chart(bar(profile, "hour_of_day", "average_gti", "Average GTI by Hour", "Hour", "W/m²", "#2E8B57"), width="stretch")
    st.plotly_chart(line(monthly, "period", "average_solar_radiation", "Monthly Solar Resource", "Month", "Average W/m²"), width="stretch")


def weather(raw, daily):
    st.title("Weather Impact Analysis")
    cols = st.columns(5)
    values = [("Average Temperature", fmt_num(daily.average_temperature.mean(), " °C")), ("Average Humidity", fmt_num(daily.average_humidity.mean(), "%")), ("Average Cloud Cover", fmt_num(daily.average_cloud_cover.mean(), "%")), ("Average Wind Speed", fmt_num(raw.wind_speed.mean(), " km/h")), ("Average Solar Radiation", fmt_num(daily.average_solar_radiation.mean(), " W/m²"))]
    for col, (label, value) in zip(cols, values):
        with col: metric(label, value)
    section("Correlation Analysis", "Correlation does not imply causation.")
    fields = [("cloud_cover", "Cloud Cover"), ("temperature", "Temperature"), ("humidity", "Humidity"), ("wind_speed", "Wind Speed")]
    corrs = {key: raw[key].corr(raw["solar_radiation"]) for key, _ in fields}
    cols = st.columns(4)
    for col, (key, label) in zip(cols, fields):
        with col: metric(f"{label}/Solar correlation", fmt_num(corrs[key]))
    for key, label in fields:
        st.plotly_chart(scatter(raw, key, "solar_radiation", f"{label} vs Solar Radiation", label, "Solar radiation (W/m²)"), width="stretch")
    st.info(" · ".join(f"{label} and solar radiation show a {correlation_label(corrs[key])} (r={corrs[key]:.2f}) in the selected data" for key, label in fields) + ". Correlation does not imply causation.")


def financial(raw, scenario, metrics):
    st.title("FINANCIAL & ROI SIMULATOR")
    st.caption("Adjust the scenario assumptions in the sidebar to model a different configuration.")
    cols = st.columns(3)
    vals = [("Estimated Annual Energy", fmt_num(metrics["annual_energy"] / 1000, " MWh")), ("Estimated Annual Revenue", fmt_inr(metrics["annual_revenue"])), ("Annual O&M", fmt_inr(metrics["annual_om"])), ("Annual Net Benefit", fmt_inr(metrics["net_benefit"])), ("Estimated ROI", fmt_num(metrics["roi"] * 100, "%")), ("Estimated Payback", "N/A" if metrics["payback"] is None else fmt_num(metrics["payback"], " years"))]
    for row in (vals[:3], vals[3:]):
        for col, (label, value) in zip(cols, row):
            with col: metric(label, value)
    model = monthly_model(raw, scenario)
    a, b, c = st.columns(3)
    with a: st.plotly_chart(bar(model, "period", "energy_kwh", "Monthly Energy Generation", "Month", "kWh", "#2E8B57"), width="stretch")
    with b: st.plotly_chart(bar(model, "period", "revenue", "Monthly Revenue", "Month", "₹"), width="stretch")
    net_monthly = model.assign(net_benefit=model.revenue - metrics["annual_om"] / 12)
    with c: st.plotly_chart(bar(net_monthly, "period", "net_benefit", "Monthly Net Benefit", "Month", "₹", "#0B1F3A"), width="stretch")
    capacities, tariffs = [50, 100, 150, 200, 250, 500], [4, 6, 8, 10, 12]
    base_gti_energy = raw.gti.fillna(0).clip(lower=0).sum() / 1000 * scenario["performance_ratio"] / max((raw.timestamp.max().date() - raw.timestamp.min().date()).days + 1, 1) * 365.25
    matrix = [[base_gti_energy * capacity * tariff for tariff in tariffs] for capacity in capacities]
    st.plotly_chart(heatmap(matrix, tariffs, capacities, "Revenue Sensitivity: Capacity vs Tariff", "Annual revenue (₹)"), width="stretch")
    capex_values = [scenario["capex"] * x for x in (0.6, 0.8, 1, 1.2, 1.5)]
    paybacks = [capex / metrics["net_benefit"] if metrics["net_benefit"] > 0 else None for capex in capex_values]
    st.plotly_chart(line(pd.DataFrame({"CAPEX": capex_values, "payback_years": paybacks}), "CAPEX", "payback_years", "CAPEX Sensitivity: Payback Period", "CAPEX (₹)", "Payback period (years)", "#0B1F3A"), width="stretch")
    financial_disclaimer()


def operations(raw, daily, monthly, profile):
    st.title("Operations & Decision Support")
    section("Best Solar Hours")
    ranked_hours = profile.sort_values("average_solar_radiation", ascending=False)
    st.plotly_chart(bar(ranked_hours, "hour_of_day", "average_solar_radiation", "Average Solar Radiation by Hour", "Hour of day", "Average W/m²"), width="stretch")
    st.dataframe(ranked_hours.head(3).style.format(precision=2), hide_index=True)
    section("Best Solar Months")
    ranked_months = monthly.sort_values("average_solar_radiation", ascending=False).copy(); ranked_months["month"] = ranked_months.period.dt.strftime("%b %Y")
    st.dataframe(ranked_months[["month", "average_solar_radiation", "peak_solar_radiation", "average_dni", "average_gti"]].style.format(precision=2), hide_index=True)
    section("Highest and lowest solar-resource days")
    columns = ["date", "average_solar_radiation", "peak_solar_radiation", "average_dni", "average_gti", "average_cloud_cover"]
    a, b = st.columns(2)
    with a: st.dataframe(daily.nlargest(10, "average_solar_radiation")[columns].style.format(precision=2), hide_index=True)
    with b: st.dataframe(daily.nsmallest(10, "average_solar_radiation")[columns].style.format(precision=2), hide_index=True)
    section("Data quality and source")
    missing = int(raw[["temperature", "humidity", "cloud_cover", "wind_speed", "solar_radiation", "dni", "gti", "sunshine_duration"]].isna().sum().sum())
    duplicates = int(raw.duplicated(subset=["timestamp"]).sum())
    cols = st.columns(5)
    for col, (label, value) in zip(cols, [("Total records", f"{len(raw):,}"), ("Minimum timestamp", raw.timestamp.min().strftime("%d %b %Y %H:%M")), ("Maximum timestamp", raw.timestamp.max().strftime("%d %b %Y %H:%M")), ("Duplicate count", str(duplicates)), ("Missing values", f"{missing:,}")]):
        with col: metric(label, value)
    st.caption(f"Data source: {DATA_SOURCE} · Location: {LOCATION} · Coordinates: {LATITUDE}, {LONGITUDE} · Frequency: Hourly")


def _is_development() -> bool:
    try:
        return st.config.get_option("global.developmentMode")
    except Exception:
        return False


def _mask_host(host: str) -> str:
    if not host or host in {"localhost", "127.0.0.1", "::1"}:
        return host
    if "." not in host:
        return host[:3] + "..."
    parts = host.split('.')
    return f"{parts[0]}.***.{parts[-1]}"


def _show_database_health() -> None:
    try:
        config = get_database_config()
    except ValueError as exc:
        with st.sidebar.expander("Database diagnostics", expanded=False):
            st.warning("Database credentials are not configured or are invalid.")
            if _is_development():
                st.caption(str(exc))
        return

    try:
        health = get_database_health(config)
        with st.sidebar.expander("Database diagnostics", expanded=False):
            st.write("**Database host:**", _mask_host(config.host))
            st.write("**Database:**", config.database)
            st.write("**Status:**", "Connected")
            st.write("**Records:**", f"{health['total_records']:,}")
            st.write("**Min timestamp:**", health['minimum_timestamp'])
            st.write("**Max timestamp:**", health['maximum_timestamp'])
    except DashboardDatabaseError as exc:
        with st.sidebar.expander("Database diagnostics", expanded=False):
            st.error(str(exc))
            if _is_development():
                st.caption(type(exc).__name__)


def _handle_dashboard_error(exc: Exception, production_message: str) -> None:
    LOGGER.exception("Dashboard error")
    if _is_development():
        st.error(f"Dashboard data error: {type(exc).__name__}")
        st.error(str(exc))
        return
    if isinstance(exc, DashboardDatabaseError):
        text = str(exc)
        if "host or port is unreachable" in text.lower() or "can't connect" in text.lower() or "connection refused" in text.lower():
            st.error("Cloud deployment cannot access your local MySQL server. Configure a remotely accessible MySQL database.")
            return
        if "authentication failed" in text.lower():
            st.error("Database authentication failed. Verify the configured username and password.")
            return
        if "database 'test1' was not found" in text.lower():
            st.error("Database 'test1' was not found on the configured MySQL server.")
            return
        if "table or view is missing" in text.lower():
            st.error("A required table or view is missing. Ensure the database schema is initialized.")
            return
        st.error("Unable to connect to the database. Please verify the configured MySQL host, port, user, password, and database.")
        return
    if isinstance(exc, ValueError):
        st.error("Database credentials are not configured or are invalid. Please verify the settings.")
        return
    st.error(production_message)


def main():
    start, end, scenario = sidebar()
    if _is_development():
        _show_database_health()
    try:
        raw = load_solar_data(start, end); daily = load_daily_summary(start, end); monthly = load_monthly_summary(start, end); profile = load_hourly_profile(start, end)
    except DashboardDatabaseError as exc:
        _handle_dashboard_error(exc, "Unable to connect to MySQL. Please ensure MySQL Server is running and .env credentials are correct.")
        return
    except ValueError as exc:
        _handle_dashboard_error(exc, "Unable to load dashboard configuration. Please verify the local environment variables.")
        return
    except Exception as exc:
        _handle_dashboard_error(exc, "Unable to load dashboard data. Please try again later.")
        return
    if raw.empty or daily.empty:
        st.warning("No database records were found for the selected date range.")
        return
    days = (end - start).days + 1
    metrics = model_metrics(raw, days, scenario)
    pages = {"01 Executive & Business Overview": executive, "02 Solar Energy Performance": performance, "03 Weather Impact Analysis": weather, "04 Financial & ROI Simulator": financial, "05 Operations & Decision Support": operations}
    page = st.sidebar.radio("Navigate", list(pages), label_visibility="collapsed")
    if page.startswith("01"): executive(raw, daily, monthly, metrics, scenario)
    elif page.startswith("02"): performance(raw, daily, monthly, profile, metrics)
    elif page.startswith("03"): weather(raw, daily)
    elif page.startswith("04"): financial(raw, scenario, metrics)
    else: operations(raw, daily, monthly, profile)
    export = raw[["timestamp", "temperature", "humidity", "cloud_cover", "wind_speed", "solar_radiation", "dni", "gti", "sunshine_duration"]]
    st.sidebar.download_button("Download filtered CSV", export.to_csv(index=False).encode("utf-8"), "solar_energy_filtered.csv", "text/csv", width="stretch")


if __name__ == "__main__": main()
