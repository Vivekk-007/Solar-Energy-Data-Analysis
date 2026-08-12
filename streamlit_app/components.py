"""Reusable Streamlit dashboard components."""
import streamlit as st


def section(title: str, description: str | None = None) -> None:
    st.subheader(title)
    if description:
        st.caption(description)


def metric(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label, value, help=help_text)


def financial_disclaimer() -> None:
    st.warning("Financial metrics are scenario estimates based on configurable assumptions and historical irradiance data. They are not actual plant financial results or investment advice. Not modelled: financing costs, taxes, degradation, equipment replacement, downtime, insurance, maintenance details, tariff changes, actual plant losses, inverter efficiency, panel orientation, or shading.")
