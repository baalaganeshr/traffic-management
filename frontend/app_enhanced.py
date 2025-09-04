# Enhanced UrbanFlow360 with PRIT Integration
# Main application with tabbed interface

import streamlit as st
import pandas as pd
from datetime import datetime
import pydeck as pdk
import os
import sys
import importlib.util

# Allow root-level imports
sys.path.append(os.path.abspath("."))

# Check if PRIT integration is available
try:
    from frontend.app_prit_enhanced import main as prit_main
    PRIT_AVAILABLE = True
except ImportError:
    PRIT_AVAILABLE = False

# Import gamified app
try:
    from frontend.app_gamified import main as gamified_main  
    GAMIFIED_AVAILABLE = True
except ImportError:
    GAMIFIED_AVAILABLE = False

# Local module imports
from frontend.ui_helpers import display_kpis, show_bar_chart, show_line_chart, show_table
from backend.simulate_data import simulate_traffic_stream
from backend.predictor import predict_congestion
from backend.alert_engine import generate_alert
from analysis.predictor_helpers import predict_congestion as predict_csv_congestion
from data_utils.delhi_cleaner import convert_weekday_speed_to_xy_format
import numpy as np

def run_professional_tab():
    """Original Professional Dashboard"""
    
    st.markdown("### 🏢 Professional Traffic Management Dashboard")
    
    # ---------------------- Sidebar Configuration ----------------------
    with st.sidebar:
        st.header("🏙️ City Selection")
        selected_city = st.selectbox("Choose a city", ["Bangalore", "Delhi"])

        st.markdown("### ⚠️ Simulate Traffic Event")
        event_enabled = st.toggle("Enable Event Injection", value=False)
        
        event_config = {"enabled": event_enabled}
        if event_enabled:
            event_config["event_time"] = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
            event_config["event_duration"] = st.slider("Duration (minutes)", 5, 60, 15)
            event_config["event_x"] = st.number_input("X Location", min_value=0, max_value=100, value=50)
            event_config["event_y"] = st.number_input("Y Location", min_value=0, max_value=100, value=40)
            event_config["event_radius"] = st.slider("Impact Radius", 10, 100, 30)
            st.success("✅ Event configured. Will inject during simulation.")

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

    # ---------------------- Display KPIs ----------------------
    st.subheader("📊 Key Performance Indicators")
    kpi_data = {
        "Total Vehicles": len(df),
        "Avg Speed": f"{df['speed'].mean():.1f} km/h" if 'speed' in df.columns else "N/A",
        "Active Alerts": len(alerts),
        "City": selected_city
    }
    display_kpis(kpi_data)

    # ---------------------- Charts Section ----------------------
    col1, col2 = st.columns(2)
    
    # Process data based on city
    if selected_city == "Delhi":
        try:
            df_clean = convert_weekday_speed_to_xy_format(df)
            weekday_columns = [col for col in df_clean.columns if col != "Time"]
        except Exception as e:
            st.warning(f"Delhi data processing error: {e}")
            df_clean = df
            weekday_columns = []
    else:
        df_clean = df
        weekday_columns = []

    # ---------- 📊 Column 1: Bar Chart ----------
    with col1:
        try:
            if selected_city == "Delhi" and weekday_columns:
                st.subheader("📊 Average Speed by Weekday")
                weekday_avg = df_clean[weekday_columns].mean().sort_values(ascending=False)
                st.bar_chart(weekday_avg)
            elif selected_city == "Bangalore":
                st.subheader("📊 Average Speed by Area (Top 10)")
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
                st.subheader("📈 Speed Variation by Time of Day")
                if weekday_columns:
                    df_long = df_clean.melt(id_vars=["Time"], value_vars=weekday_columns, var_name="Weekday", value_name="Speed")
                    df_long = df_long.dropna()
                    df_long = df_long.sort_values("Time")
                    st.line_chart(df_long.pivot(index="Time", columns="Weekday", values="Speed"))
            elif selected_city == "Bangalore":
                st.subheader("📈 Congestion Level Over Time")
                if 'Date' in df.columns and 'Congestion Level' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df['Congestion Level'] = pd.to_numeric(df['Congestion Level'], errors='coerce')
                    df = df.dropna(subset=['Date', 'Congestion Level'])
                    daily_congestion = df.groupby(df['Date'].dt.date)['Congestion Level'].mean()
                    st.line_chart(daily_congestion.head(30))
        except Exception as e:
            st.warning(f"{selected_city} Line Chart Error: {e}")

    # ---------------------- Alerts Section ----------------------
    if alerts:
        st.subheader("🚨 Active Alerts")
        for alert in alerts[-5:]:  # Show last 5 alerts
            st.warning(f"⚠️ {alert}")
    else:
        st.info("✅ No active alerts")

    # ---------------------- Interactive Map ----------------------
    st.subheader("🗺️ Real-Time Traffic Map")
    
    if not df.empty:
        # Create map data
        map_df = df.copy()
        
        # Ensure we have coordinates
        if 'x' not in map_df.columns or 'y' not in map_df.columns:
            map_df['x'] = np.random.uniform(77.5, 77.7, len(map_df))  # Delhi longitude range
            map_df['y'] = np.random.uniform(28.4, 28.7, len(map_df))  # Delhi latitude range
        
        # Add alert indicator
        map_df['alert'] = (map_df['speed'] < 10).astype(int) if 'speed' in map_df.columns else 0
        
        # Vehicle layer
        vehicle_layer = pdk.Layer(
            'ScatterplotLayer',
            data=map_df,
            get_position='[x, y]',
            get_color='[0, 255, 0]' if selected_city == "Delhi" else '[0, 0, 255]',
            get_radius=100,
            pickable=True,
        )

        # Alert layer
        alert_layer = pdk.Layer(
            'ScatterplotLayer',
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
            latitude=28.6139 if selected_city == "Delhi" else 12.9716,
            longitude=77.2090 if selected_city == "Delhi" else 77.5946,
            zoom=10,
            pitch=0,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[vehicle_layer, alert_layer],
            initial_view_state=view_state,
            tooltip={"text": "Vehicle: {vehicle_id}\nSpeed: {speed} km/h\nStatus: {Status}"},
        ))

    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(df.head(100))


def main():
    """Main application with tabbed interface"""
    
    st.set_page_config(
        page_title="UrbanFlow360 - Enhanced Traffic Management",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; text-align: center; margin: 0; font-size: 2.5rem;'>
            🚦 UrbanFlow360
        </h1>
        <p style='color: white; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;'>
            Advanced Traffic Management with AI Integration
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab configuration
    tabs = ["🏢 Professional", "🎮 Gamified"]
    if PRIT_AVAILABLE:
        tabs.append("🤖 PRIT Enhanced")
    
    selected_tab = st.selectbox("Choose Interface Mode", tabs, label_visibility="collapsed")
    
    # Route to appropriate interface
    if selected_tab == "🏢 Professional":
        run_professional_tab()
    
    elif selected_tab == "🎮 Gamified":
        if GAMIFIED_AVAILABLE:
            try:
                # Call the gamified main function
                gamified_main()
            except Exception as e:
                st.error(f"❌ Error loading Gamified interface: {e}")
                st.info("💡 Falling back to Professional interface")
                run_professional_tab()
        else:
            st.error("❌ Gamified interface not available")
            run_professional_tab()
    
    elif selected_tab == "🤖 PRIT Enhanced" and PRIT_AVAILABLE:
        try:
            # Call the PRIT-enhanced main function
            prit_main()
        except Exception as e:
            st.error(f"❌ Error loading PRIT Enhanced interface: {e}")
            st.info("💡 Install pygame and neat-python for PRIT integration")
            
            # Show installation instructions
            with st.expander("📋 Installation Instructions"):
                st.code("""
# Install PRIT dependencies
pip install pygame neat-python

# Or using conda
conda install -c conda-forge pygame
pip install neat-python
                """)
            
            run_professional_tab()
    
    # Status bar
    st.markdown("---")
    status_cols = st.columns(4)
    
    with status_cols[0]:
        st.metric("🏢 Professional", "✅ Available")
    
    with status_cols[1]:
        if GAMIFIED_AVAILABLE:
            st.metric("🎮 Gamified", "✅ Available") 
        else:
            st.metric("🎮 Gamified", "❌ Error")
    
    with status_cols[2]:
        if PRIT_AVAILABLE:
            st.metric("🤖 PRIT Enhanced", "✅ Available")
        else:
            st.metric("🤖 PRIT Enhanced", "⚠️ Dependencies Missing")
    
    with status_cols[3]:
        st.metric("📊 Total Modes", f"{len(tabs)}/3")


if __name__ == "__main__":
    main()
