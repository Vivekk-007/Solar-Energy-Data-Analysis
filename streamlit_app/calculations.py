"""Pure business-model calculations, separate from the dashboard UI."""
import numpy as np
import pandas as pd


def estimated_energy(frame: pd.DataFrame, capacity_kw: float, performance_ratio: float) -> pd.Series:
    return frame["gti"].fillna(0).clip(lower=0).div(1000).mul(capacity_kw).mul(performance_ratio)


def annualize(total_energy_kwh: float, selected_days: int) -> float:
    return total_energy_kwh / selected_days * 365.25 if selected_days > 0 else 0.0


def annual_revenue(annual_energy_kwh: float, tariff: float) -> float:
    return annual_energy_kwh * tariff


def annual_om(capex: float, om_rate: float) -> float:
    return capex * om_rate


def net_benefit(revenue: float, om_cost: float) -> float:
    return revenue - om_cost


def payback_years(capex: float, benefit: float) -> float | None:
    return capex / benefit if benefit > 0 else None


def roi(benefit: float, capex: float) -> float:
    return benefit / capex if capex > 0 else 0.0


def co2_avoided(energy_kwh: float, factor: float) -> float:
    return energy_kwh * factor


def specific_yield(annual_energy_kwh: float, capacity_kw: float) -> float:
    return annual_energy_kwh / capacity_kw if capacity_kw > 0 else 0.0


def capacity_factor(annual_energy_kwh: float, capacity_kw: float) -> float:
    return annual_energy_kwh / (capacity_kw * 8760) if capacity_kw > 0 else 0.0


def model_metrics(frame: pd.DataFrame, days: int, scenario: dict[str, float]) -> dict[str, float | None]:
    energy = estimated_energy(frame, scenario["capacity_kw"], scenario["performance_ratio"])
    annual_energy = annualize(float(energy.sum()), days)
    revenue = annual_revenue(annual_energy, scenario["tariff"])
    om_cost = annual_om(scenario["capex"], scenario["om_rate"])
    benefit = net_benefit(revenue, om_cost)
    return {"selected_energy": float(energy.sum()), "annual_energy": annual_energy, "annual_revenue": revenue,
            "annual_om": om_cost, "net_benefit": benefit, "payback": payback_years(scenario["capex"], benefit),
            "roi": roi(benefit, scenario["capex"]), "co2": co2_avoided(annual_energy, scenario["co2_factor"]),
            "specific_yield": specific_yield(annual_energy, scenario["capacity_kw"]),
            "capacity_factor": capacity_factor(annual_energy, scenario["capacity_kw"])}


def monthly_model(frame: pd.DataFrame, scenario: dict[str, float]) -> pd.DataFrame:
    copy = frame.copy()
    copy["period"] = copy["timestamp"].dt.to_period("M").dt.to_timestamp()
    copy["energy_kwh"] = estimated_energy(copy, scenario["capacity_kw"], scenario["performance_ratio"])
    result = copy.groupby("period", as_index=False)["energy_kwh"].sum()
    result["revenue"] = result["energy_kwh"] * scenario["tariff"]
    return result


def correlation_label(value: float) -> str:
    if pd.isna(value): return "insufficient data"
    strength = "weak" if abs(value) < 0.3 else "moderate" if abs(value) < 0.7 else "strong"
    direction = "positive" if value >= 0 else "negative"
    return f"{strength} {direction} relationship"
