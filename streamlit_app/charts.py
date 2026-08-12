"""Consistent Plotly chart constructors."""
import plotly.express as px
import plotly.graph_objects as go

NAVY, YELLOW, GREEN = "#0B1F3A", "#F6C344", "#2E8B57"


def line(frame, x, y, title, x_label, y_label, color=YELLOW):
    fig = px.line(frame, x=x, y=y, title=title, markers=True, template="plotly_white")
    fig.update_traces(line_color=color, hovertemplate=f"%{{x}}<br>{y_label}: %{{y:,.2f}}<extra></extra>")
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def scatter(frame, x, y, title, x_label, y_label):
    fig = px.scatter(frame, x=x, y=y, title=title, opacity=0.45, template="plotly_white", trendline=None)
    fig.update_traces(marker_color=GREEN)
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def bar(frame, x, y, title, x_label, y_label, color=YELLOW):
    fig = px.bar(frame, x=x, y=y, title=title, template="plotly_white")
    fig.update_traces(marker_color=color, hovertemplate=f"%{{x}}<br>{y_label}: %{{y:,.2f}}<extra></extra>")
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def heatmap(values, x, y, title, colorbar_title):
    fig = go.Figure(go.Heatmap(z=values, x=x, y=y, colorscale="YlGn", colorbar_title=colorbar_title, hovertemplate="Capacity: %{y} kW<br>Tariff: ₹%{x}/kWh<br>Value: %{z:,.0f}<extra></extra>"))
    fig.update_layout(title=title, xaxis_title="Electricity tariff (₹/kWh)", yaxis_title="Capacity (kW)", margin=dict(l=10, r=10, t=50, b=10))
    return fig
