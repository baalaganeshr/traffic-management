# frontend/app.py

import streamlit as st
import pandas as pd
from datetime import datetime

from frontend.ui_helpers import display_kpis, show_bar_chart, show_line_chart, show_table
from backend.simulate_data import simulate_traffic_stream
from backend.predictor import predict_congestion
from backend.alert_engine import generate_alert

# ---------------------- Page Config ----------------------
st.set_page_config(
    page_title="UrbanFlow360 - Real-time Traffic Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚦 UrbanFlow360: Real-Time Traffic Dashboard")
st.markdown("##### Monitoring Bangalore Traffic with Predictive Alerts")

# ---------------------- Data Initialization ----------------------
df = pd.DataFrame()
alerts = []

# ---------------------- Simulate Stream (Fast Demo Mode) ----------------------
with st.spinner("Simulating traffic stream (limited rows)..."):
    for i, row in enumerate(simulate_traffic_stream('data/Banglore_traffic_Dataset.csv', sleep_time=0)):
        row['Status'] = predict_congestion(row)  # Predict congestion status
        alert = generate_alert(row, row["Status"])
        if alert:
            alerts.append(alert)
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

        # Limit to 1000 rows for performance
        if len(df) > 1000:
            df = df.tail(1000)

        # Limit total iterations for smoother Streamlit experience
        if i >= 200:
            break

# ---------------------- KPI Section ----------------------
alert_count = len(alerts)
heavy_count = df[df['Status'] == 'Heavy'].shape[0]

display_kpis(df, alert_count, heavy_count)

# ---------------------- Charts Section ----------------------
st.markdown("###  Traffic Trend Overview")
col1, col2 = st.columns(2)

with col1:
    show_bar_chart(df)

with col2:
    show_line_chart(df)

# ---------------------- Alert Log Table ----------------------
st.markdown("###  Real-Time Alert Log")
if alerts:
    alert_df = pd.DataFrame(alerts)
    show_table(alert_df)
else:
    st.success(" No alerts triggered yet.")
