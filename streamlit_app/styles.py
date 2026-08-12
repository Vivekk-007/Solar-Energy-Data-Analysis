"""Small, shared visual treatment for the dashboard."""
import streamlit as st


def apply_styles() -> None:
    st.markdown("""<style>
    .stApp { background: #F7F9FC; } h1, h2, h3 { color: #0B1F3A; }
    [data-testid="stMetric"] { background: white; border-left: 4px solid #F6C344; padding: 0.65rem; border-radius: 0.35rem; }
    .dashboard-subtitle { color: #52606D; font-size: 1.05rem; }
    .disclaimer { background: #FFF8E1; border-left: 4px solid #F6C344; padding: 0.8rem; border-radius: 0.25rem; }
    </style>""", unsafe_allow_html=True)
