"""
UrbanFlow360 – Improved Professional Dashboard

This Streamlit app focuses on a clean, responsive Professional dashboard
with tabs for Monitor, Analytics, Map and Data. It reuses the project’s
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

# Local imports from the project
from backend.simulate_data import simulate_traffic_stream
from backend.predictor import predict_congestion
from backend.alert_engine import generate_alert


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


def main():
    st.set_page_config(page_title="UrbanFlow360 – Professional (Improved)",
                       layout="wide", initial_sidebar_state="expanded")

    # Layout + control alignment styles
    st.markdown(
        """
        <style>
        .main .block-container { max-width: 1200px; margin: 0 auto; padding-top: 1.25rem; }
        .stButton > button { width: 100%; height: 42px; border-radius: 10px; }
        .uf-status { height: 42px; display: flex; align-items: center; justify-content: center;
                     border-radius: 10px; border: 1px solid rgba(255,255,255,0.12);
                     background: rgba(255,255,255,0.06); color: #e5e7eb; font-weight: 600; }
        .uf-caption { margin-bottom: 0.25rem; color: #94a3b8; font-size: 0.85rem; }
        .uf-status .dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;'>
            <h1 style='color: white; margin: 0; font-size: 3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                UrbanFlow360 – Professional
            </h1>
            <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;'>
                Real-time monitoring, analytics, map and exports
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Session state
    st.session_state.setdefault("prof_running", False)
    st.session_state.setdefault("prof_data_log", [])
    st.session_state.setdefault("simulation_results", pd.DataFrame())
    st.session_state.setdefault("auto_refresh", True)
    st.session_state.setdefault("refresh_seconds", 3)

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        selected_city = st.selectbox("City", ["Bangalore", "Delhi"], index=0)
        st.subheader("Refresh")
        st.session_state.auto_refresh = st.toggle("Auto refresh", value=st.session_state.auto_refresh)
        st.session_state.refresh_seconds = st.slider("Interval (sec)", 1, 10, st.session_state.refresh_seconds)

    # Controls (equal columns for perfect alignment)
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1:
        if st.button("Start", type="primary", use_container_width=True, disabled=st.session_state.prof_running):
            st.session_state.prof_running = True
            st.session_state.prof_data_log = []
            st.toast("Data collection started", icon="✅")
            st.rerun()
    with c2:
        if st.button("Stop & Process", use_container_width=True, disabled=not st.session_state.prof_running):
            st.session_state.prof_running = False
            if st.session_state.prof_data_log:
                df_results = pd.DataFrame(st.session_state.prof_data_log)
                st.session_state.simulation_results = df_results
                st.success(f"Processed {len(df_results)} points")
            else:
                st.info("No data collected yet")
            st.rerun()
    with c3:
        has_data = len(st.session_state.simulation_results) > 0
        if has_data:
            csv_bytes = st.session_state.simulation_results.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv_bytes,
                               file_name=f"urbanflow360_{datetime.now():%Y%m%d_%H%M%S}.csv",
                               mime="text/csv", use_container_width=True)
        else:
            st.button("Download CSV", disabled=True, use_container_width=True)
    with c4:
        st.markdown("<div class='uf-caption'>Collector</div>", unsafe_allow_html=True)
        _running = bool(st.session_state.prof_running)
        _color = "#22c55e" if _running else "#f59e0b"
        _status = "Running" if _running else "Idle"
        st.markdown(f"<div class='uf-status'><span class='dot' style='background:{_color}'></span>{_status}</div>", unsafe_allow_html=True)

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
            show_cols = [c for c in ["timestamp", "x", "y", "speed", "Status", "alert"] if c in df_live.columns]
            st.dataframe(df_live[show_cols], use_container_width=True)

            if st.session_state.auto_refresh:
                time.sleep(st.session_state.refresh_seconds)
                st.rerun()
        else:
            st.info("Collector is idle. Click Start to begin streaming data.")

    # Analytics tab
    with tab_analytics:
        df = _resolve_df_for_analysis(st.session_state)
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

            speed_series = _pick_series(df, [
                'speed', 'Speed', 'Average Speed', 'AverageSpeed', 'avg_speed', 'Avg Speed'
            ])

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Records", len(df))
            with m2:
                st.metric("Avg speed", f"{speed_series.mean():.1f} km/h" if speed_series is not None else "N/A")
            with m3:
                congested = int((df.get('Status', pd.Series([])) == 'Heavy').sum()) if 'Status' in df.columns else 0
                st.metric("Congested", congested)
            with m4:
                st.metric("Alerts", int((df.get('alert', pd.Series([])) != 'No Alert').sum()) if 'alert' in df.columns else 0)

            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Speed Distribution" if speed_series is not None else "Volume Distribution")
                if speed_series is not None:
                    st.bar_chart(pd.cut(speed_series.dropna(), bins=10).value_counts().sort_index())
                else:
                    vol = _pick_series(df, ['Traffic Volume', 'Vehicles', 'traffic_volume'])
                    if vol is not None:
                        st.bar_chart(pd.cut(vol.dropna(), bins=10).value_counts().sort_index())
                    else:
                        st.info("No suitable numeric column to chart.")
            with c2:
                st.subheader("Speed Trend" if speed_series is not None else "Volume Trend")
                if speed_series is not None:
                    st.line_chart(speed_series.rolling(window=min(25, len(speed_series))).mean())
                else:
                    vol = _pick_series(df, ['Traffic Volume', 'Vehicles', 'traffic_volume'])
                    if vol is not None:
                        st.line_chart(vol.rolling(window=min(25, len(vol))).mean())
                    else:
                        st.info("No suitable numeric column to chart.")

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
