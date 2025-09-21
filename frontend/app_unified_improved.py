"""
UrbanFlow360 - Improved Professional Dashboard

This Streamlit app focuses on a clean, responsive Professional dashboard
with tabs for Monitor, Analytics, Map and Data. It reuses the project's
simulation + prediction utilities while providing a polished UX.
"""

from datetime import datetime
import time
from typing import List, Dict, Any

import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Local imports from the project - using sys.path to ensure proper imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.simulate_data import simulate_traffic_stream
    from backend.predictor import predict_congestion
    from backend.alert_engine import generate_alert
except ImportError:
    # Fallback - create dummy functions if imports fail
    def simulate_traffic_stream(csv_path, sleep_time=0):
        """Dummy function for traffic stream simulation"""
        import pandas as pd
        # Return sample Kerala traffic data
        sample_data = [
            {"junction": "Kochi IT Hub", "vehicle_count": 2450, "avg_speed": 15, "timestamp": datetime.now()},
            {"junction": "Thiruvananthapuram Market", "vehicle_count": 1890, "avg_speed": 22, "timestamp": datetime.now()},
            {"junction": "Kozhikode Beach Road", "vehicle_count": 1234, "avg_speed": 35, "timestamp": datetime.now()},
            {"junction": "Thrissur Cultural Center", "vehicle_count": 1567, "avg_speed": 28, "timestamp": datetime.now()},
            {"junction": "Kannur Railway Station", "vehicle_count": 987, "avg_speed": 42, "timestamp": datetime.now()},
        ]
        for data in sample_data:
            yield data
    
    def predict_congestion(data):
        """Dummy prediction function"""
        return {"prediction": "Moderate", "confidence": 0.85}
    
    def generate_alert(data):
        """Dummy alert function"""
        if data.get("vehicle_count", 0) > 2000:
            return {"level": "HIGH", "message": "Heavy traffic detected"}
        elif data.get("vehicle_count", 0) > 1500:
            return {"level": "MEDIUM", "message": "Moderate traffic"}
        else:
            return {"level": "LOW", "message": "Light traffic"}


def _collect_samples(selected_city: str, traffic_csv_path: str, n: int = 5) -> List[Dict[str, Any]]:
    """Collect up to n samples from the stream and return rows with timestamp/alert."""
    rows: List[Dict[str, Any]] = []
    for i, row in enumerate(simulate_traffic_stream(traffic_csv_path, sleep_time=0)):
        if selected_city == "Delhi":
            row["Status"] = predict_congestion(row)
            alert = generate_alert(row, row.get("Status"), city="Delhi")
        else:
            alert = generate_alert(row, city="Bangalore")

        row["timestamp"] = datetime.now()
        row["alert"] = alert or "No Alert"
        rows.append(row)
        if i + 1 >= n:
            break
    return rows


def _resolve_df_for_analysis(state) -> pd.DataFrame:
    if state.get("prof_running") and state.get("prof_data_log"):
        return pd.DataFrame(state["prof_data_log"])  # live buffer
    if isinstance(state.get("simulation_results"), pd.DataFrame) and len(state["simulation_results"]) > 0:
        return state["simulation_results"]
    return pd.DataFrame()


def _map_view(df: pd.DataFrame, selected_city: str) -> None:
    if df.empty:
        st.info("No data available to plot on the map.")
        return

    mdf = df.copy()
    if "x" not in mdf.columns or "y" not in mdf.columns:
        if selected_city == "Delhi":
            mdf["x"] = np.random.uniform(77.1, 77.3, len(mdf))
            mdf["y"] = np.random.uniform(28.5, 28.7, len(mdf))
        else:
            mdf["x"] = np.random.uniform(77.5, 77.6, len(mdf))
            mdf["y"] = np.random.uniform(12.9, 13.0, len(mdf))

    if "speed" in mdf.columns:
        mdf["alert_level"] = pd.cut(pd.to_numeric(mdf["speed"], errors="coerce"),
                                     bins=[0, 10, 25, 50, 100], labels=[3, 2, 1, 0])
    else:
        mdf["alert_level"] = 0

    layers = []
    color_map = {0: [0, 255, 0], 1: [255, 255, 0], 2: [255, 165, 0], 3: [255, 0, 0]}
    for lvl in [0, 1, 2, 3]:
        chunk = mdf[mdf["alert_level"] == lvl]
        if not chunk.empty:
            layers.append(pdk.Layer(
                "ScatterplotLayer",
                data=chunk,
                get_position="[x, y]",
                get_color=color_map[lvl],
                get_radius=150,
                pickable=True,
            ))

    center_lat = 28.6 if selected_city == "Delhi" else 12.97
    center_lon = 77.2 if selected_city == "Delhi" else 77.59
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=11, pitch=0)
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state,
                             tooltip={"text": "Speed: {speed} km/h"}))


def _plot_histogram(series: pd.Series, label: str, bins: int = 12) -> go.Figure:
    s = pd.to_numeric(series, errors="coerce").dropna()
    df = pd.DataFrame({label: s})
    fig = px.histogram(
        df, x=label, nbins=bins, opacity=0.9, color_discrete_sequence=["#60a5fa"],
    )
    if len(s) > 0:
        mean_v = float(s.mean())
        med_v = float(s.median())
        fig.add_vline(x=mean_v, line_dash="dash", line_color="#10b981", annotation_text="mean", annotation_position="top")
        fig.add_vline(x=med_v, line_dash="dot", line_color="#f59e0b", annotation_text="median", annotation_position="top")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
    )
    fig.update_yaxes(title_text="Count", gridcolor="#334155")
    fig.update_xaxes(title_text=label, gridcolor="#334155")
    return fig


def _plot_trend(series: pd.Series, label: str, window: int = 10, timestamps: pd.Series | None = None) -> go.Figure:
    s = pd.to_numeric(series, errors="coerce")
    x_vals: pd.Series
    if timestamps is not None and len(timestamps) == len(series):
        try:
            x_vals = pd.to_datetime(timestamps, errors="coerce")
        except Exception:
            x_vals = pd.Series(range(len(s)))
    else:
        x_vals = pd.Series(range(len(s)))

    df = pd.DataFrame({"x": x_vals, "raw": s})
    # Compute smoothed series; guard against tiny windows
    win = max(1, min(window, max(1, len(s))))
    df["smooth"] = df["raw"].rolling(window=win).mean()
    df_clean = df.dropna(subset=["raw"])  # raw may still have NaNs

    fig = go.Figure()
    if df_clean["raw"].notna().any():
        fig.add_trace(go.Scatter(x=df_clean["x"], y=df_clean["raw"], mode="lines", name="Raw",
                                 line=dict(color="#9ca3af", width=1), opacity=0.5))
    if df["smooth"].notna().any():
        fig.add_trace(go.Scatter(x=df["x"], y=df["smooth"], mode="lines", name="Smoothed",
                                 line=dict(color="#60a5fa", width=3)))

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=0, r=0, t=10, b=0),
        height=300,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"),
    )
    fig.update_yaxes(title_text=label, gridcolor="#334155")
    fig.update_xaxes(title_text="Time" if (timestamps is not None and len(timestamps) == len(series)) else "Sample",
                     gridcolor="#334155")
    return fig


def main():
    st.set_page_config(page_title="VIN - Professional Dashboard",
                       layout="wide", initial_sidebar_state="expanded")

    # Layout + control alignment styles
    st.markdown(
        """
<style>
:root {
    --uf-gap: 12px;
    --uf-radius: 12px;
    --uf-border: 1px solid rgba(148,163,184,.22);
    --uf-surface: rgba(15,23,42,.5);
}
.main .block-container {
    max-width: 1120px;
    margin: 0 auto;
    padding-top: 0.8rem;
}
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(148,163,184,.18);
    background: rgba(15,23,42,.55);
}
[data-testid="stSidebar"] .block-container {
    padding-top: 1.05rem;
}
.stButton > button,
.stDownloadButton > button {
    width: 100%;
    height: 44px;
    border-radius: 11px;
    background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
    border: 0;
    color: #fff;
    font-weight: 700;
    letter-spacing: .2px;
    box-shadow: 0 8px 24px rgba(37,99,235,.28);
    transition: transform .05s ease, box-shadow .1s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 30px rgba(37,99,235,.32);
}
.stButton > button:active,
.stDownloadButton > button:active {
    transform: translateY(1px);
}
.uf-hero {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 1.5rem;
    background: linear-gradient(135deg, 
        rgba(59,130,246,0.15) 0%, 
        rgba(14,165,233,0.12) 50%, 
        rgba(37,99,235,0.18) 100%);
    padding: 2rem 2.5rem;
    border-radius: 20px;
    border: 2px solid rgba(59,130,246,0.25);
    margin-bottom: 2rem;
    backdrop-filter: blur(15px);
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(59,130,246,0.12), 
                inset 0 1px 0 rgba(255,255,255,0.1);
}
.uf-hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59,130,246,0.5), 
        transparent);
}
.uf-hero-content {
    display: grid;
    gap: 0.8rem;
    max-width: 680px;
}
.uf-hero-eyebrow {
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.3em;
    background: linear-gradient(135deg, #60a5fa, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 600;
    margin: 0;
}
.uf-hero-title {
    margin: 0;
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.uf-hero-lead {
    margin: 0;
    color: rgba(241,245,249,0.9);
    font-size: 1.1rem;
    line-height: 1.6;
    font-weight: 400;
}
.uf-hero-actions {
    display: flex;
    align-items: center;
}
.uf-back-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    padding: 0.8rem 2rem;
    border-radius: 50px;
    background: linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(37,99,235,0.15) 100%);
    border: 2px solid rgba(59,130,246,0.4);
    color: #ffffff;
    font-weight: 600;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
    text-decoration: none !important;
    box-shadow: 0 8px 32px rgba(59,130,246,0.15), inset 0 1px 0 rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.uf-back-chip::before {
    content: '';
}
.uf-back-chip::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: left 0.5s ease;
}
.uf-back-chip:hover {
    background: linear-gradient(135deg, rgba(59,130,246,0.35) 0%, rgba(37,99,235,0.25) 100%);
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 16px 40px rgba(59,130,246,0.25), inset 0 1px 0 rgba(255,255,255,0.2);
    border-color: rgba(59,130,246,0.6);
    color: #f8fafc;
}
.uf-back-chip:hover::after {
    left: 100%;
}
.uf-back-chip:active {
    transform: translateY(-1px) scale(0.98);
}

.uf-actions-shell {
    background: var(--uf-surface);
    border: 1px solid rgba(148,163,184,.2);
    border-radius: var(--uf-radius);
    padding: 1.05rem 1.2rem;
    margin-bottom: 1.2rem;
}
.uf-actions-shell > div[data-testid="column"] {
    padding: 0 !important;
}
.uf-actions-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin-bottom: 0.6rem;
}
.uf-actions-grid > div[data-testid="column"] {
    padding: 0 !important;
}
.uf-actions-grid > div[data-testid="column"] > div {
    margin-bottom: 0 !important;
}
.uf-status-card {
    background: linear-gradient(135deg, 
        rgba(15,23,42,0.85) 0%, 
        rgba(30,41,59,0.8) 100%);
    border: 2px solid rgba(59,130,246,0.3);
    border-radius: 16px;
    padding: 1.5rem 1.25rem;
    display: grid;
    gap: 0.6rem;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(59,130,246,0.15), 
                inset 0 1px 0 rgba(59,130,246,0.1);
}
.uf-status-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59,130,246,0.4), 
        transparent);
    transition: left 0.6s ease;
}
.uf-status-card:hover {
    transform: translateY(-2px) scale(1.01);
    border-color: rgba(59,130,246,0.5);
    box-shadow: 0 16px 48px rgba(59,130,246,0.25), 
                inset 0 1px 0 rgba(59,130,246,0.2);
}
.uf-status-card:hover::before {
    left: 100%;
}
.uf-status-card__label {
    text-transform: uppercase;
    letter-spacing: 0.15em;
    font-size: 0.8rem;
    font-weight: 600;
    color: #94a3b8;
}
.uf-status-card__value {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.4rem;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -0.01em;
}
.uf-status-card__value .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}
.uf-status-card__meta {
    color: #94a3b8;
    font-size: 0.85rem;
}
.uf-card {
    padding: 1.2rem 1.5rem;
    border: 2px solid rgba(59,130,246,0.25);
    border-radius: 16px;
    background: linear-gradient(135deg, 
        rgba(15,23,42,0.85) 0%, 
        rgba(30,41,59,0.8) 100%);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px rgba(59,130,246,0.15);
    transition: all 0.3s ease;
}
.uf-card:hover {
    border-color: rgba(59,130,246,0.4);
    box-shadow: 0 12px 40px rgba(59,130,246,0.25);
}

/* Mobile Responsiveness for Dashboard */
@media (max-width: 768px) {
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .uf-hero {
        padding: 1.5rem 1.25rem;
        margin-bottom: 1.5rem;
        border-radius: 16px;
        flex-direction: column;
        align-items: flex-start;
        text-align: center;
    }
    .uf-hero-title {
        font-size: 2rem;
        line-height: 1.2;
    }
    .uf-hero-lead {
        font-size: 1rem;
    }
    .uf-actions-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    .uf-status-card {
        padding: 1.25rem 1rem;
        text-align: center;
    }
    .uf-status-card__value {
        justify-content: center;
        font-size: 1.2rem;
    }
    .uf-back-chip {
        width: 100%;
        justify-content: center;
        margin-bottom: 1rem;
        min-height: 48px;
    }
}

@media (max-width: 480px) {
    .uf-hero {
        padding: 1.25rem 1rem;
    }
    .uf-hero-title {
        font-size: 1.8rem;
    }
    .uf-hero-eyebrow {
        font-size: 0.75rem;
    }
    .uf-status-card {
        padding: 1rem;
    }
    .uf-card {
        padding: 1rem;
        margin-bottom: 1rem;
    }
}
.uf-section-title {
    font-weight: 700;
    color: #e2e8f0;
    margin: 0 0 .25rem 0;
}
.uf-subtle {
    color: #94a3b8;
    font-size: .85rem;
}
.stTabs [data-baseweb=tab-list] {
    gap: var(--uf-gap);
}
.stTabs [data-baseweb=tab] {
    padding: .65rem .85rem;
    border-radius: 9px;
}
.stPlotlyChart {
    border-radius: var(--uf-radius);
    overflow: hidden;
}
div[data-testid="stDataFrame"] {
    border-radius: var(--uf-radius);
    border: var(--uf-border);
}
div[data-testid="stMetric"] {
    padding: .6rem .85rem;
    border-radius: var(--uf-radius);
    border: var(--uf-border);
    background: rgba(148,163,184,.09);
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .uf-hero {
        flex-direction: column;
        text-align: center;
        padding: 1.2rem;
    }
    .uf-hero-title {
        font-size: 1.6rem;
    }
    .uf-hero-lead {
        font-size: 0.9rem;
    }
    .uf-hero-actions {
        margin-top: 1rem;
    }
    .uf-back-chip {
        font-size: 0.85rem;
        padding: 0.4rem 0.9rem;
    }
    .uf-actions-shell {
        padding: 0.8rem 1rem;
    }
}

@media (max-width: 480px) {
    .uf-hero {
        padding: 1rem;
    }
    .uf-hero-title {
        font-size: 1.4rem;
    }
    .uf-hero-eyebrow {
        font-size: 0.7rem;
    }
    .uf-back-chip {
        font-size: 0.8rem;
        padding: 0.35rem 0.8rem;
    }
}

/* Mobile Optimization */
@media (max-width: 768px) {
    .main .block-container {
        padding: 0.5rem 0.5rem;
        max-width: 100%;
    }
    
    [data-testid="stSidebar"] {
        width: 280px;
    }
    
    .uf-hero {
        padding: 1rem;
        margin-bottom: 1rem;
        flex-direction: column;
        text-align: center;
    }
    
    .uf-hero-content {
        margin-right: 0;
        margin-bottom: 1rem;
    }
    
    .uf-hero-title {
        font-size: 1.2rem;
        line-height: 1.3;
    }
    
    .uf-hero-lead {
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .uf-back-chip {
        padding: 0.5rem 1rem;
        font-size: 0.85rem;
        width: auto;
        display: inline-block;
    }
    
    /* Make tabs scrollable on mobile */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
    }
    
    [data-testid="stTabs"] [data-baseweb="tab"] {
        white-space: nowrap;
        min-width: 80px;
    }
    
    /* Mobile-friendly metrics */
    [data-testid="metric-container"] {
        margin-bottom: 0.5rem;
    }
    
    /* Stack columns vertically on mobile */
    [data-testid="column"] {
        width: 100% !important;
        margin-bottom: 0.5rem;
    }
    
    /* Mobile-friendly dataframes */
    [data-testid="stDataFrame"] {
        font-size: 0.8rem;
    }
    
    /* Mobile buttons */
    .stButton button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* Responsive selectbox */
    [data-testid="stSelectbox"] {
        margin-bottom: 0.5rem;
    }
}

/* Tablet adjustments */
@media (max-width: 1024px) and (min-width: 769px) {
    .main .block-container {
        padding: 1rem;
    }
    
    .uf-hero {
        padding: 1.5rem;
    }
    
    .uf-hero-title {
        font-size: 1.6rem;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )

    # Session state
    st.session_state.setdefault("prof_running", False)
    st.session_state.setdefault("prof_data_log", [])
    st.session_state.setdefault("simulation_results", pd.DataFrame())
    st.session_state.setdefault("auto_refresh", True)
    st.session_state.setdefault("refresh_seconds", 3)

    data_log = list(st.session_state.get("prof_data_log", []))
    live_record_count = len(data_log)
    running = bool(st.session_state.prof_running)
    auto_refresh_label = 'On' if st.session_state.auto_refresh else 'Off'
    status_label = 'Running' if running else 'Idle'
    status_color = '#22c55e' if running else '#f59e0b'
    last_entry = data_log[-1] if live_record_count else {}
    last_timestamp = last_entry.get("timestamp") if isinstance(last_entry, dict) else None
    if isinstance(last_timestamp, datetime):
        last_ts_display = last_timestamp.strftime('%H:%M:%S')
    else:
        last_ts_display = 'N/A'

    hero_html = f"""
        <div class='uf-hero'>
          <div class='uf-hero-content'>
            <p class='uf-hero-eyebrow'>VIN Professional Console</p>
            <h1 class='uf-hero-title'>Operational insight without leaving the map</h1>
            <p class='uf-hero-lead'>Monitor live flow, inspect analytics, and export evidence from a single workspace. Configure a city, start streaming, and stay ahead of congestion.</p>
          </div>
          <div class='uf-hero-actions'>
            <a class='uf-back-chip' href='/' style='text-decoration: none;'>← Back to Home</a>
          </div>
        </div>
    """


    st.markdown(hero_html, unsafe_allow_html=True)

    # Navigation button to Kerala Demo
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    with nav_col3:
        if st.button("🚦 Kerala Demo", key="go_kerala_demo", use_container_width=True, help="Go to Kerala Traffic Demo"):
            st.switch_page("demo/app_simple_kerala.py")
    
    st.markdown("---")

    metric_cols = st.columns(3)
    metric_cols[0].metric('Records buffered', f"{live_record_count:,}")
    metric_cols[1].metric('Collector status', status_label)
    metric_cols[2].metric('Refresh cadence', f"{auto_refresh_label} ({st.session_state.refresh_seconds}s)")

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        selected_city = st.selectbox("City", ["Bangalore", "Delhi"], index=0)
        st.subheader("Refresh")
        st.session_state.auto_refresh = st.toggle("Auto refresh", value=st.session_state.auto_refresh)
        st.session_state.refresh_seconds = st.slider("Interval (sec)", 1, 10, st.session_state.refresh_seconds)

    # Collector controls and status
    st.markdown("<div class='uf-actions-shell'>", unsafe_allow_html=True)
    action_col, status_col = st.columns([3, 1.1])
    with action_col:
        st.markdown("<div class='uf-actions-grid'>", unsafe_allow_html=True)
        start_col, stop_col, export_col = st.columns(3)
        with start_col:
            if st.button('Start', type='primary', use_container_width=True, disabled=running):
                st.session_state.prof_running = True
                st.session_state.prof_data_log = []
                st.toast('Data collection started')
                st.rerun()
        with stop_col:
            if st.button('Stop & Process', use_container_width=True, disabled=not running):
                st.session_state.prof_running = False
                if st.session_state.prof_data_log:
                    df_results = pd.DataFrame(st.session_state.prof_data_log)
                    st.session_state.simulation_results = df_results
                    st.success(f'Processed {len(df_results)} points')
                else:
                    st.info('No data collected yet')
                st.rerun()
        with export_col:
            has_data = len(st.session_state.simulation_results) > 0
            if has_data:
                csv_bytes = st.session_state.simulation_results.to_csv(index=False).encode('utf-8')
                st.download_button('Download CSV', csv_bytes, file_name=f"urbanflow360_{datetime.now():%Y%m%d_%H%M%S}.csv", mime='text/csv', use_container_width=True)
            else:
                st.button('Download CSV', disabled=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption('Adjust the interval from the sidebar.')
    with status_col:
        status_html = f"""
        <div class='uf-status-card'>
          <div class='uf-status-card__label'>Collector</div>
          <div class='uf-status-card__value'><span class='dot' style='background:{status_color}'></span>{status_label}</div>
          <div class='uf-status-card__meta'>{live_record_count:,} records buffered</div>
          <div class='uf-status-card__meta'>Auto refresh: <strong>{auto_refresh_label}</strong> ({st.session_state.refresh_seconds}s)</div>
          <div class='uf-status-card__meta'>Last update: <strong>{last_ts_display}</strong></div>
        </div>
        """
        st.markdown(status_html.strip(), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    traffic_csv_path = (
        "data/Banglore_traffic_Dataset.csv" if selected_city == "Bangalore"
        else "data/delhi/2024_week_day_congestion_city.csv"
    )

    tab_monitor, tab_analytics, tab_map, tab_data = st.tabs(["Monitor", "Analytics", "Map", "Data"])

    # Monitor tab
    with tab_monitor:
        if st.session_state.prof_running:
            samples = _collect_samples(selected_city, traffic_csv_path, n=5)
            st.session_state.prof_data_log.extend(samples)

            last = samples[-1]
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Location", f"({last.get('x', 0):.2f}, {last.get('y', 0):.2f})")
            with k2:
                st.metric("Speed", f"{last.get('speed', 0):.1f} km/h")
            with k3:
                st.metric("Status", last.get('Status', 'Unknown'))
            with k4:
                st.metric("Points collected", len(st.session_state.prof_data_log))

            df_live = pd.DataFrame(samples)
            # Keep the live table simple: hide complex 'alert' column
            show_cols = [c for c in ["timestamp", "x", "y", "speed", "Status"] if c in df_live.columns]
            # Full-width: sparkline on top, table below
            # Live sparkline for speed if available
            if "speed" in df_live.columns:
                sp = pd.to_numeric(df_live["speed"], errors="coerce").dropna()
                if len(sp) > 1:
                    fig = px.line(sp, title="Live Speed (last batch)")
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=30, b=0), height=220,
                        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#e2e8f0"),
                    )
                    fig.update_yaxes(gridcolor="#334155")
                    fig.update_xaxes(gridcolor="#334155")
                    fig.update_traces(line_color="#60a5fa")
                    st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_live[show_cols], use_container_width=True)

            if st.session_state.auto_refresh:
                time.sleep(st.session_state.refresh_seconds)
                st.rerun()
        else:
            st.info("Collector is idle. Click Start to begin streaming data.")
            # Provide quick actions when idle - center the button
            left, center, right = st.columns([1,2,1])
            with center:
                if st.button("Clear Collected Data", use_container_width=True):
                    st.session_state.prof_data_log = []
                    st.session_state.simulation_results = pd.DataFrame()
                    st.toast("Cleared previous data")
                    st.rerun()
            st.caption("Use the sidebar to tweak refresh behaviour.")

    # Analytics tab
    with tab_analytics:
        # Pick data source: live buffer vs processed
        live_df = pd.DataFrame(st.session_state.get("prof_data_log", []))
        processed_df = st.session_state.get("simulation_results") if isinstance(st.session_state.get("simulation_results"), pd.DataFrame) else pd.DataFrame()
        default_source = "Live" if (st.session_state.get("prof_running") and not live_df.empty) else "Processed"
        source = st.radio("Data source", ["Live", "Processed"], index=0 if default_source=="Live" else 1, horizontal=True, help="Analyze the live collector buffer or the processed dataset.")
        df = live_df if source == "Live" else processed_df
        if df.empty:
            st.info("No data available for analytics yet.")
        else:
            # choose a speed-like column across datasets
            def _pick_series(frame, names):
                for n in names:
                    if n in frame.columns:
                        s = pd.to_numeric(frame[n], errors='coerce')
                        if s.notna().any():
                            return s
                return None

            # Metric selector kept simple
            metric = st.radio("Metric", ["Speed", "Volume"], horizontal=True)
            speed_series = _pick_series(df, [
                'speed', 'Speed', 'Average Speed', 'AverageSpeed', 'avg_speed', 'Avg Speed'
            ]) if metric == "Speed" else None
            volume_series = _pick_series(df, [
                'Traffic Volume', 'Vehicles', 'traffic_volume', 'volume', 'Volume'
            ]) if metric == "Volume" else None

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Records", len(df))
            with m2:
                if metric == "Speed" and speed_series is not None:
                    st.metric("Avg speed", f"{speed_series.mean():.1f} km/h")
                elif metric == "Volume" and volume_series is not None:
                    st.metric("Avg volume", f"{volume_series.mean():.0f}")
                else:
                    st.metric("Average", "N/A")
            with m3:
                congested = int((df.get('Status', pd.Series([])) == 'Heavy').sum()) if 'Status' in df.columns else 0
                st.metric("Congested", congested)
            with m4:
                st.metric("Alerts", int((df.get('alert', pd.Series([])) != 'No Alert').sum()) if 'alert' in df.columns else 0)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader(f"{metric} Distribution")
                bins = st.slider("Bins", 5, 50, 12, key="hist_bins")
                if metric == "Speed" and speed_series is not None:
                    s = pd.to_numeric(speed_series, errors='coerce').dropna()
                    if len(s) > 0:
                        fig = _plot_histogram(s, "Speed (km/h)", bins)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric speed values to chart.")
                elif metric == "Volume" and volume_series is not None:
                    v = pd.to_numeric(volume_series, errors='coerce').dropna()
                    if len(v) > 0:
                        fig = _plot_histogram(v, "Volume", bins)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric volume values to chart.")
                else:
                    st.info("No suitable numeric column to chart.")
            with c2:
                st.subheader(f"{metric} Trend")
                window = st.slider("Smoothing window", 1, 50, 10, key="trend_win")
                if metric == "Speed" and speed_series is not None:
                    s = pd.to_numeric(speed_series, errors='coerce')
                    if s.notna().any():
                        ts = df["timestamp"] if "timestamp" in df.columns else None
                        fig = _plot_trend(s, "Speed (km/h)", window, timestamps=ts)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric speed values to chart.")
                elif metric == "Volume" and volume_series is not None:
                    v = pd.to_numeric(volume_series, errors='coerce')
                    if v.notna().any():
                        ts = df["timestamp"] if "timestamp" in df.columns else None
                        fig = _plot_trend(v, "Volume", window, timestamps=ts)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No numeric volume values to chart.")

    # Map tab
    with tab_map:
        _map_view(_resolve_df_for_analysis(st.session_state), selected_city)

    # Data tab
    with tab_data:
        df = _resolve_df_for_analysis(st.session_state)
        if df.empty:
            st.info("No data collected yet.")
        else:
            try:
                from streamlit import column_config as cc
                col_cfg = {}
                if 'alert' in df.columns:
                    col_cfg['alert'] = cc.TextColumn('Alert', max_chars=120, width='large')
                st.dataframe(df.tail(200), use_container_width=True, hide_index=True, column_config=col_cfg)
            except Exception:
                st.dataframe(df.tail(200), use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Export CSV", csv,
                               file_name=f"urbanflow360_export_{datetime.now():%Y%m%d_%H%M%S}.csv",
                               mime="text/csv")


if __name__ == "__main__":
    main()
