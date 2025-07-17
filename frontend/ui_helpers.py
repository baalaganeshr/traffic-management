# frontend/ui_helpers.py

import streamlit as st
import pandas as pd
import altair as alt

# KPI Display
def display_kpis(df, alert_count, heavy_count):
    col1, col2, col3 = st.columns(3)
    col1.metric(" Total Records", f"{len(df):,}")
    col2.metric(" Heavy Traffic Records", heavy_count)
    col3.metric(" Total Alerts", alert_count)

# Bar Chart - Vehicles per Junction
def show_bar_chart(df):
    st.subheader(" Average Vehicles per Junction")
    bar_data = df.groupby("Junction")["Vehicles"].mean().reset_index()
    bar_chart = alt.Chart(bar_data).mark_bar().encode(
        x="Junction:O",
        y="Vehicles:Q",
        color="Junction:N"
    ).properties(height=300)
    st.altair_chart(bar_chart, use_container_width=True)

# Line Chart - Vehicle Trend Over Time
def show_line_chart(df):
    st.subheader(" Vehicle Trend Over Time")
    line_data = df.groupby("DateTime")["Vehicles"].mean().reset_index()
    line_chart = alt.Chart(line_data).mark_line().encode(
        x="DateTime:T",
        y="Vehicles:Q"
    ).properties(height=300)
    st.altair_chart(line_chart, use_container_width=True)

# Table Renderer
def show_table(data):
    st.dataframe(data, use_container_width=True)

# Summary Section
def show_summary(df):
    st.markdown("###  Daily Summary")
    df['Date'] = df['DateTime'].dt.date
    summary = df.groupby("Date").agg({
        "Vehicles": "mean",
        "Status": lambda x: (x == "Heavy").sum(),
        "DateTime": lambda x: x.dt.hour.mode()[0] if not x.empty else None
    }).reset_index()
    summary.columns = ["Date", "Avg Vehicles", "Heavy Alerts", "Peak Hour"]
    st.dataframe(summary, use_container_width=True)

# Download Button
def download_button(data, label="⬇ Download CSV"):
    csv = data.to_csv(index=False).encode("utf-8")
    st.download_button(label=label, data=csv, file_name="export.csv", mime="text/csv")
