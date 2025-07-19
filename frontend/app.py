# frontend/app.py

import streamlit as st
import pandas as pd
from datetime import datetime
import pydeck as pdk
import os
import sys
from data_utils.delhi_cleaner import convert_weekday_speed_to_xy_format
import numpy as np


# Allow root-level imports
sys.path.append(os.path.abspath("."))

# Local module imports
from frontend.ui_helpers import display_kpis, show_bar_chart, show_line_chart, show_table
from backend.simulate_data import simulate_traffic_stream
from backend.predictor import predict_congestion
from backend.alert_engine import generate_alert
from analysis.predictor_helpers import predict_congestion as predict_csv_congestion

# ---------------------- Page Config ----------------------
st.set_page_config(
    page_title="UrbanFlow360 - Real-time Traffic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚦 UrbanFlow360: Real-Time Traffic Dashboard")
st.markdown("##### Monitoring Traffic with Predictive Alerts")

# ---------------------- City Selection ----------------------
st.sidebar.title(" City Selection")
selected_city = st.sidebar.selectbox("Choose a city", ["Bangalore", "Delhi"])

# ---------------------- Event Injection Form ----------------------
st.sidebar.markdown("###  Simulate Traffic Event")
event_enabled = st.sidebar.toggle("Enable Event Injection", value=False)

event_config = {}
if event_enabled:
    event_config["event_city"] = selected_city  # No need to ask again
    event_config["event_time"] = st.sidebar.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
    event_config["event_duration"] = st.sidebar.slider("Duration (minutes)", 5, 60, 15)
    event_config["event_x"] = st.sidebar.number_input("X Location", min_value=0, max_value=100, value=50)
    event_config["event_y"] = st.sidebar.number_input("Y Location", min_value=0, max_value=100, value=40)
    event_config["event_radius"] = st.sidebar.slider("Impact Radius", 10, 100, 30)
    st.sidebar.success(" Event configured. Will inject during simulation.")

# ---------------------- Set File Paths Based on City ----------------------
if selected_city == "Bangalore":
    traffic_csv_path = "data/Banglore_traffic_Dataset.csv"
    sim_csv_path = "simulation/simulated_data.csv"
    st.session_state['city_code'] = "BLR"
else:
    traffic_csv_path = "data/delhi/2024_week_day_congestion_city.csv"
    sim_csv_path = "data/delhi/2024_week_day_congestion_city.csv"
    st.session_state['city_code'] = "DEL"

# ---------------------- Data Initialization ----------------------
df = pd.DataFrame()
alerts = []

# ---------------------- Simulate Stream (Fast Demo Mode) ----------------------
with st.spinner("Simulating traffic stream (limited rows)..."):
    for i, row in enumerate(simulate_traffic_stream(traffic_csv_path, sleep_time=0)):
        if selected_city == "Delhi":
            row['Status'] = predict_congestion(row)
            alert = generate_alert(row, row["Status"], city="Delhi")
        else:
            alert = generate_alert(row, city="Bangalore")

        if alert:
            alerts.append(alert)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

        if len(df) > 1000:
            df = df.tail(1000)
        if i >= 200:
            break

alert_count = len(alerts)

if selected_city == "Delhi" and 'Status' in df.columns:
    heavy_count = df[df['Status'] == 'Heavy'].shape[0]
else:
    # For Bangalore: use congestion level > 70%
    if 'Congestion Level' in df.columns:
        try:
            df["Congestion Level"] = pd.to_numeric(df["Congestion Level"], errors="coerce")
            heavy_count = df[df["Congestion Level"] > 70].shape[0]
        except:
            heavy_count = 0
    else:
        heavy_count = 0

display_kpis(df, alert_count, heavy_count)

# ---------------------- Traffic Trend Overview ----------------------
st.markdown("### ⚡ Traffic Trend Overview")
col1, col2 = st.columns(2)

# ---------- 📊 Column 1: Bar Chart ----------
with col1:
    try:
        if selected_city == "Delhi":
            st.subheader(" Average Speed by Weekday")

            weekday_columns = [col for col in df.columns if col in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
            df_clean = df.copy()

            for col in weekday_columns:
                df_clean[col] = df_clean[col].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)

            weekday_avg = df_clean[weekday_columns].mean().reset_index()
            weekday_avg.columns = ["Weekday", "Avg Speed (km/h)"]

            st.bar_chart(weekday_avg.set_index("Weekday"))

        elif selected_city == "Bangalore":
            st.subheader(" Average Speed by Area (Top 10)")
            if 'Area Name' in df.columns and 'Average Speed' in df.columns:
                df['Average Speed'] = pd.to_numeric(df['Average Speed'], errors='coerce')
                top_areas = df.groupby("Area Name")["Average Speed"].mean().sort_values(ascending=False).head(10)
                st.bar_chart(top_areas)
            else:
                st.warning("Missing 'Area Name' or 'Average Speed' in Bangalore dataset.")

    except Exception as e:
        st.warning(f"{selected_city} Bar Chart Error: {e}")

# ---------- 📈 Column 2: Line Chart ----------
with col2:
    try:
        if selected_city == "Delhi":
            st.subheader(" Speed Variation by Time of Day")
            df_long = df_clean.melt(id_vars=["Time"], value_vars=weekday_columns, var_name="Weekday", value_name="Speed")
            df_long = df_long.dropna()
            df_long = df_long.sort_values("Time")

            st.line_chart(df_long.pivot(index="Time", columns="Weekday", values="Speed"))

        elif selected_city == "Bangalore":
            st.subheader(" Congestion Level Over Time")
            if 'Date' in df.columns and 'Congestion Level' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df['Congestion Level'] = pd.to_numeric(df['Congestion Level'], errors='coerce')
                df = df.dropna(subset=['Date', 'Congestion Level'])

                line_data = df.groupby(df['Date'].dt.date)["Congestion Level"].mean()
                st.line_chart(line_data)
            else:
                st.warning("Missing 'Date' or 'Congestion Level' in Bangalore dataset.")

    except Exception as e:
        st.warning(f"{selected_city} Line Chart Error: {e}")

# ---------------------- Alert Log Table ----------------------
st.markdown("###  Real-Time Alert Log")
if alerts:
    alert_df = pd.DataFrame(alerts)
    st.dataframe(alert_df)
else:
    st.success(" No alerts triggered yet.")



# ---------------------- ML Model-Based Congestion Prediction ----------------------
st.markdown("---")
st.markdown("###  ML-Based Congestion Prediction from Simulated Data")

if selected_city == "Delhi":
    # 🔍 Debug: Show raw structure first
    raw_df = pd.read_csv("data/delhi/2024_week_day_speed_city.csv")
    st.success(f" Delhi raw data loaded: {len(raw_df)} rows")
    

    # 🛠️ Convert Delhi data to model-ready format
    sim_df = convert_weekday_speed_to_xy_format("data/delhi/2024_week_day_speed_city.csv")
    result_df = predict_csv_congestion(sim_df)

else:
    csv_path = "simulation/simulated_data.csv"
    if os.path.exists(csv_path):
        sim_df = pd.read_csv(csv_path)
        st.success(f" Simulation data loaded: {len(sim_df)} rows")
    else:
        sim_df = pd.DataFrame()

# ✅ Continue only if sim_df has valid data
if not sim_df.empty:
    st.write("Final sim_df columns:", sim_df.columns.tolist())

    if 'step' in sim_df.columns:
        st.write("⏱ Simulation Time Range:", sim_df['step'].min(), "to", sim_df['step'].max())

    # 🔍 ML Prediction
    result_df = predict_csv_congestion(sim_df)

    # 🔎 Display Output
    st.subheader("🔍 Prediction Preview")
    st.dataframe(result_df[['step', 'vehicle_id', 'speed', 'prediction']].head(10))

    st.subheader("📊 Congestion Count (0 = Smooth, 1 = Heavy)")
    st.bar_chart(result_df["prediction"].value_counts())

    st.download_button(
        label="⬇ Download Prediction CSV",
        data=result_df.to_csv(index=False).encode("utf-8"),
        file_name="congestion_predictions.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ Simulation DataFrame is empty. Please check your selected city/data source.")

    # ---------------------- 🗺️ Real-Time Congestion Map ----------------------
    st.markdown("---")
    st.subheader(" Real-Time Congestion Map")

    map_df = result_df[['x', 'y', 'Status', 'speed', 'step', 'vehicle_id']].dropna()
    map_df['alert'] = map_df['Status'].apply(lambda s: 1 if s == 'Heavy' else 0)

    def get_color(row):
        if row["Status"] == "Smooth":
            return [0, int(min(row["speed"] * 20, 255)), 0]  # Green
        else:
            return [255, int(max(255 - row["speed"] * 20, 0)), 0]  # Red

    map_df['color'] = map_df.apply(get_color, axis=1)
    map_df = map_df.sort_values(by="step", ascending=False).head(100)

    if st.toggle(" Animate by Step"):
        unique_steps = sorted(map_df["step"].unique())
        selected_step = st.slider("Select Time Step", int(min(unique_steps)), int(max(unique_steps)))
        map_df = map_df[map_df["step"] == selected_step]

    vehicle_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[x, y]',
        get_color='color',
        get_radius=100,
        pickable=True,
        opacity=0.8,
    )

    alert_layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df[map_df['alert'] == 1],
        get_position='[x, y]',
        get_color='[255, 0, 0]',
        get_radius=200,
        pickable=True,
        line_width_min_pixels=3,
        stroked=True,
        filled=True,
    )

    view_state = pdk.ViewState(
        latitude=21.1458,    # Central India
        longitude=79.0882,
        zoom=4.8,
        pitch=0,
    )

    st.pydeck_chart(pdk.Deck(
        layers=[vehicle_layer, alert_layer],
        initial_view_state=view_state,
        tooltip={"text": "Vehicle: {vehicle_id}\nSpeed: {speed} km/h\nStatus: {Status}"},
    ))

   