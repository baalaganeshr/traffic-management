"""
UrbanFlow360 - Unified Dashboard
Combines Professional + Gamified + PRIT Enhanced interfaces
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath("."))

# Import original components
from frontend.ui_helpers import display_kpis, show_bar_chart, show_line_chart, show_table
from backend.simulate_data import simulate_traffic_stream
from backend.predictor import predict_congestion
from backend.alert_engine import generate_alert
from analysis.predictor_helpers import predict_congestion as predict_csv_congestion
from data_utils.delhi_cleaner import convert_weekday_speed_to_xy_format
import pydeck as pdk

# Try to import PRIT integration
PRIT_AVAILABLE = False
try:
    from backend.prit_integration.game_bridge import PritGameBridge
    PRIT_AVAILABLE = True
except ImportError:
    print("⚠️ PRIT integration not available - using fallback mode")

def initialize_session_state():
    """Initialize all session state variables"""
    if "current_interface" not in st.session_state:
        st.session_state.current_interface = "🏢 Professional"
    
    if "prit_bridge" not in st.session_state and PRIT_AVAILABLE:
        config = {
            "simulation_speed": 1.0,
            "auto_generation": True,
            "neat_enabled": True,
            "vehicle_variety": True
        }
        st.session_state.prit_bridge = PritGameBridge(config)
        st.session_state.prit_active = False
    
    if "gamified_stats" not in st.session_state:
        st.session_state.gamified_stats = {
            "xp": 0,
            "level": 1,
            "badges": [],
            "total_score": 0,
            "sessions_played": 0
        }

def render_professional_dashboard():
    """Professional Traffic Management Dashboard"""
    
    st.markdown("### 🏢 Professional Traffic Management")
    st.markdown("*Real-time traffic monitoring and analysis*")
    
    # Initialize session state for professional dashboard
    if "prof_running" not in st.session_state:
        st.session_state.prof_running = False
    if "prof_data_log" not in st.session_state:
        st.session_state.prof_data_log = []
    if "simulation_results" not in st.session_state:
        st.session_state.simulation_results = pd.DataFrame()
    
    # Sidebar for city selection
    with st.sidebar:
        st.header("🏙️ Configuration")
        selected_city = st.selectbox("Choose City", ["Bangalore", "Delhi"])
        
        st.subheader("⚠️ Event Simulation")
        event_enabled = st.toggle("Enable Event Injection", value=False)
        
        if event_enabled:
            event_duration = st.slider("Duration (minutes)", 5, 60, 15)
            event_impact = st.slider("Impact Radius", 10, 100, 30)
            st.success("✅ Event configured")

    # Control Panel
    st.markdown("### 🎛️ Data Collection Controls")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_disabled = st.session_state.prof_running
        start_button = st.button(
            "🚀 Start Data Gathering" if not start_disabled else "🔄 Gathering Data...", 
            disabled=start_disabled, 
            use_container_width=True,
            help="Start real-time traffic data collection"
        )
        if start_button:
            st.session_state.prof_running = True
            st.session_state.prof_data_log = []
            st.success("✅ Data gathering started!")
            st.rerun()
    
    with col2:
        stop_disabled = not st.session_state.prof_running
        stop_button = st.button(
            "⏹️ Stop & Process", 
            disabled=stop_disabled, 
            use_container_width=True,
            help="Stop data gathering and process results"
        )
        if stop_button:
            st.session_state.prof_running = False
            
            # Process collected data
            if st.session_state.prof_data_log:
                with st.spinner("Processing collected data..."):
                    df_results = pd.DataFrame(st.session_state.prof_data_log)
                    st.session_state.simulation_results = df_results
                    st.success(f"✅ Processed {len(df_results)} data points!")
            else:
                st.warning("⚠️ No data collected yet!")
            st.rerun()
    
    with col3:
        download_disabled = len(st.session_state.simulation_results) == 0
        if not download_disabled:
            csv_data = st.session_state.simulation_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Data",
                data=csv_data,
                file_name=f"urbanflow360_data_{selected_city}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download collected traffic data as CSV"
            )
        else:
            st.button(
                "📥 Download Data", 
                disabled=True, 
                use_container_width=True,
                help="No data available for download"
            )

    # Set file paths
    if selected_city == "Bangalore":
        traffic_csv_path = "data/Banglore_traffic_Dataset.csv"
    else:
        traffic_csv_path = "data/delhi/2024_week_day_congestion_city.csv"

    # Real-time data collection
    if st.session_state.prof_running:
        # Collect data in background
        st.markdown("### 📡 Real-Time Data Collection Active")
        
        try:
            # Generate data points
            data_sample = []
            for i, row in enumerate(simulate_traffic_stream(traffic_csv_path, sleep_time=0)):
                if selected_city == "Delhi":
                    row['Status'] = predict_congestion(row)
                    alert = generate_alert(row, row["Status"], city="Delhi")
                else:
                    alert = generate_alert(row, city="Bangalore")
                
                # Add timestamp and log
                row['timestamp'] = datetime.now()
                row['alert'] = alert if alert else "No Alert"
                st.session_state.prof_data_log.append(row)
                data_sample.append(row)
                
                if i >= 5:  # Collect 5 samples per refresh
                    break
            
            # Show current data points
            if data_sample:
                col_a, col_b, col_c, col_d = st.columns(4)
                last_row = data_sample[-1]
                with col_a:
                    st.metric("📍 Location", f"({last_row.get('x', 0):.1f}, {last_row.get('y', 0):.1f})")
                with col_b:
                    st.metric("🚗 Speed", f"{last_row.get('speed', 0):.1f} km/h")
                with col_c:
                    st.metric("📊 Status", last_row.get('Status', 'Unknown'))
                with col_d:
                    st.metric("📈 Total Points", len(st.session_state.prof_data_log))
                
                # Show latest samples
                st.subheader("📊 Latest Data Samples")
                df_samples = pd.DataFrame(data_sample)
                display_cols = ['timestamp', 'x', 'y', 'speed', 'Status', 'alert'] if 'Status' in df_samples.columns else list(df_samples.columns)
                available_cols = [col for col in display_cols if col in df_samples.columns]
                st.dataframe(df_samples[available_cols], use_container_width=True)
                
                # Auto refresh every 3 seconds when running
                time.sleep(3)
                st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Data collection error: {str(e)}")
            st.session_state.prof_running = False
    
    # Display current dataset and results
    if len(st.session_state.simulation_results) > 0:
        st.markdown("---")
        st.markdown("### 📊 Processed Results")
        
        # Show summary stats
        results_df = st.session_state.simulation_results
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚗 Total Vehicles", len(results_df))
        with col2:
            avg_speed = results_df.get('speed', [0]).mean() if 'speed' in results_df.columns else 0
            st.metric("⚡ Avg Speed", f"{avg_speed:.1f} km/h")
        with col3:
            if 'Status' in results_df.columns:
                congested = len(results_df[results_df['Status'] == 'Heavy'])
                st.metric("🚨 Congested", congested)
            else:
                st.metric("🚨 Alerts", len([a for a in results_df.get('alert', []) if a != "No Alert"]))
        with col4:
            st.metric("🏙️ City", selected_city)
        
        # Show data preview
        st.subheader("🔍 Data Preview")
        display_cols = ['timestamp', 'x', 'y', 'speed', 'Status', 'alert'] if 'Status' in results_df.columns else list(results_df.columns)
        available_cols = [col for col in display_cols if col in results_df.columns]
        st.dataframe(results_df[available_cols].tail(10), use_container_width=True)
        
        # Traffic distribution chart
        if 'Status' in results_df.columns:
            st.subheader("📊 Traffic Status Distribution")
            status_counts = results_df['Status'].value_counts()
            st.bar_chart(status_counts)
    
    # Initialize variables for KPIs if not already set
    df = pd.DataFrame()
    alerts = []
    
    # Generate initial data for KPIs when not running or no results
    if not st.session_state.prof_running and len(st.session_state.simulation_results) == 0:
        # Generate traffic data for display when not running
        with st.spinner("Loading initial traffic data..."):
            # Simulate traffic stream
            for i, row in enumerate(simulate_traffic_stream(traffic_csv_path, sleep_time=0)):
                if selected_city == "Delhi":
                    row['Status'] = predict_congestion(row)
                    alert = generate_alert(row, row["Status"], city="Delhi")
                else:
                    alert = generate_alert(row, city="Bangalore")

                if alert:
                    alerts.append(alert)
                    
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

                if len(df) > 800:  # Limit for performance
                    df = df.tail(800)
                if i >= 150:  # Quick demo mode
                    break
    
    elif len(st.session_state.simulation_results) > 0:
        # Use processed results for KPIs
        df = st.session_state.simulation_results
        alerts = [a for a in df.get('alert', []) if a != "No Alert"] if 'alert' in df.columns else []

    # KPIs section with safe variable handling
    st.subheader("📊 Key Performance Indicators")
    
    # Ensure df and alerts are defined and not empty
    if 'df' not in locals() or df is None or len(df) == 0:
        df = pd.DataFrame({'speed': [0], 'vehicle_id': [1]})  # Default data
    if 'alerts' not in locals() or alerts is None:
        alerts = []
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚗 Total Vehicles", len(df))
    
    with col2:
        avg_speed = df['speed'].mean() if 'speed' in df.columns and len(df) > 0 else 0
        st.metric("⚡ Avg Speed", f"{avg_speed:.1f} km/h")
    
    with col3:
        st.metric("🚨 Active Alerts", len(alerts))
    
    with col4:
        st.metric("🏙️ City", selected_city)

    # Charts section with safe data handling
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Traffic Distribution")
        if len(df) > 0 and selected_city == "Bangalore" and 'Area Name' in df.columns:
            try:
                df['Average Speed'] = pd.to_numeric(df['Average Speed'], errors='coerce')
                top_areas = df.groupby("Area Name")["Average Speed"].mean().sort_values(ascending=False).head(10)
                if len(top_areas) > 0:
                    st.bar_chart(top_areas)
                else:
                    st.info("No area data available")
            except Exception as e:
                st.warning(f"Chart error: {e}")
        elif len(df) > 0 and 'speed' in df.columns:
            try:
                # Generic speed distribution
                speed_bins = pd.cut(df['speed'], bins=5)
                speed_dist = speed_bins.value_counts()
                if len(speed_dist) > 0:
                    st.bar_chart(speed_dist)
                else:
                    st.info("No speed data for distribution")
            except Exception as e:
                st.info("No traffic distribution data available")
        else:
            st.info("Start data collection to see traffic distribution")

    with col2:
        st.subheader("📈 Traffic Flow Trends")
        if len(df) > 0 and 'speed' in df.columns:
            try:
                # Rolling average of speed over time
                df_sorted = df.sort_values('vehicle_id') if 'vehicle_id' in df.columns else df
                rolling_speed = df_sorted['speed'].rolling(window=min(10, len(df))).mean()
                if len(rolling_speed) > 0:
                    st.line_chart(rolling_speed.head(50))
                else:
                    st.info("No trend data available")
            except Exception as e:
                st.info("No traffic trend data available")
        else:
            st.info("Start data collection to see traffic trends")

    # Alerts section
    if alerts:
        st.subheader("🚨 Recent Alerts")
        for alert in alerts[-3:]:  # Show last 3
            st.warning(f"⚠️ {alert}")
    else:
        st.success("✅ No active alerts - traffic flowing smoothly")

    # Map visualization
    st.subheader("🗺️ Traffic Heatmap")
    
    if not df.empty:
        # Create map data
        map_df = df.copy()
        
        # Generate coordinates if not present
        if 'x' not in map_df.columns:
            if selected_city == "Delhi":
                map_df['x'] = np.random.uniform(77.1, 77.3, len(map_df))
                map_df['y'] = np.random.uniform(28.5, 28.7, len(map_df))
            else:
                map_df['x'] = np.random.uniform(77.5, 77.6, len(map_df))  
                map_df['y'] = np.random.uniform(12.9, 13.0, len(map_df))

        # Alert indicator
        if 'speed' in map_df.columns:
            map_df['alert_level'] = pd.cut(map_df['speed'], 
                                         bins=[0, 10, 25, 50, 100], 
                                         labels=[3, 2, 1, 0])  # 3=red, 0=green
        else:
            map_df['alert_level'] = 0

        # Create layers
        layers = []
        
        for alert_level in [0, 1, 2, 3]:
            level_data = map_df[map_df['alert_level'] == alert_level]
            if not level_data.empty:
                color_map = {0: [0, 255, 0], 1: [255, 255, 0], 2: [255, 165, 0], 3: [255, 0, 0]}
                
                layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=level_data,
                    get_position='[x, y]',
                    get_color=color_map[alert_level],
                    get_radius=150,
                    pickable=True,
                )
                layers.append(layer)

        # Map center
        center_lat = 28.6 if selected_city == "Delhi" else 12.97
        center_lon = 77.2 if selected_city == "Delhi" else 77.59

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=11,
            pitch=0,
        )

        st.pydeck_chart(pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip={"text": "Vehicle: {vehicle_id}\nSpeed: {speed} km/h"},
        ))

    # Data export
    with st.expander("📋 Data Export & Details"):
        st.subheader("📊 Raw Data Sample")
        st.dataframe(df.head(20))
        
        # Export button
        if st.button("📁 Export Data"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"professional_traffic_data_{timestamp}.csv"
            df.to_csv(filename, index=False)
            st.success(f"✅ Data exported to {filename}")

def render_gamified_dashboard():
    """Gamified Traffic Management Experience"""
    
    st.markdown("### 🎮 Gamified Traffic Control")
    st.markdown("*Earn XP, unlock badges, and level up your traffic management skills!*")
    
    # Player stats display
    stats = st.session_state.gamified_stats
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎮 Level", stats["level"])
    with col2:
        st.metric("⭐ XP", stats["xp"])
    with col3:
        st.metric("🏅 Badges", len(stats["badges"]))
    with col4:
        st.metric("🏆 Total Score", stats["total_score"])

    # XP Progress bar
    xp_needed = stats["level"] * 100
    xp_progress = (stats["xp"] % 100) / 100
    st.markdown("**📈 Progress to Next Level**")
    st.progress(xp_progress)
    st.write(f"Need {100 - (stats['xp'] % 100)} XP for Level {stats['level'] + 1}")

    # Game controls
    st.subheader("🎯 Traffic Control Challenge")
    
    col1, col2 = st.columns(2)
    
    with col1:
        difficulty = st.selectbox("🎚️ Difficulty Level", 
                                ["Easy", "Medium", "Hard", "Expert"])
        
        scenario = st.selectbox("🌆 Scenario",
                              ["Morning Rush", "Evening Rush", "Weekend", "Night Time", "Event Traffic"])
    
    with col2:
        duration = st.slider("⏱️ Session Duration (minutes)", 1, 30, 10)
        
        if st.button("🚀 Start Gamified Session", type="primary"):
            st.session_state.gamified_active = True
            st.success("🎮 Gamified session started!")
            st.rerun()

    # Active session
    if st.session_state.get("gamified_active", False):
        
        # Simulation placeholder
        st.subheader("🎪 Live Traffic Management")
        
        # Create realistic simulation data
        simulation_data = generate_gamified_simulation_data(scenario, difficulty)
        
        # Performance metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            efficiency = simulation_data["efficiency"]
            st.metric("⚡ Efficiency", f"{efficiency:.1f}%", 
                     delta=f"+{np.random.uniform(0.5, 2.0):.1f}%")
        
        with col2:
            throughput = simulation_data["throughput"]  
            st.metric("🚀 Throughput", f"{throughput:.0f} veh/hr",
                     delta=f"+{np.random.uniform(10, 50):.0f}")
        
        with col3:
            score = simulation_data["score"]
            st.metric("🎯 Current Score", score,
                     delta=f"+{np.random.randint(5, 25)}")

        # Live charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Traffic Flow")
            
            # Generate time series data
            times = np.arange(0, 10, 0.5)
            flows = np.sin(times) * 20 + 50 + np.random.normal(0, 5, len(times))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=times, y=flows, mode='lines+markers',
                                   name='Traffic Flow', line=dict(color='#2E8B57')))
            fig.update_layout(title="Real-time Traffic Flow", height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Performance Score")
            
            # Score progression
            score_history = [score - i*5 + np.random.uniform(-2, 5) for i in range(10, 0, -1)]
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=list(range(len(score_history))), y=score_history,
                                    mode='lines+markers', name='Score',
                                    line=dict(color='#4169E1')))
            fig2.update_layout(title="Score Progression", height=300)
            st.plotly_chart(fig2, use_container_width=True)

        # Action buttons
        st.subheader("🎮 Traffic Controls")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚦 Switch Lights"):
                xp_gain = np.random.randint(5, 15)
                st.session_state.gamified_stats["xp"] += xp_gain
                st.success(f"⚡ +{xp_gain} XP - Good timing!")
        
        with col2:
            if st.button("🚌 Priority Bus"):
                xp_gain = np.random.randint(8, 20)
                st.session_state.gamified_stats["xp"] += xp_gain
                st.success(f"🚌 +{xp_gain} XP - Bus priority activated!")
        
        with col3:
            if st.button("🚨 Emergency Mode"):
                xp_gain = np.random.randint(15, 25)
                st.session_state.gamified_stats["xp"] += xp_gain
                st.success(f"🚨 +{xp_gain} XP - Emergency handled!")
        
        with col4:
            if st.button("⏹️ End Session"):
                st.session_state.gamified_active = False
                st.session_state.gamified_stats["sessions_played"] += 1
                
                # Calculate final score and XP
                final_xp = np.random.randint(50, 150)
                st.session_state.gamified_stats["xp"] += final_xp
                st.session_state.gamified_stats["total_score"] += score
                
                # Check for level up
                new_level = min(50, 1 + st.session_state.gamified_stats["xp"] // 100)
                if new_level > st.session_state.gamified_stats["level"]:
                    st.session_state.gamified_stats["level"] = new_level
                    st.balloons()
                    st.success(f"🎉 LEVEL UP! You're now Level {new_level}!")
                
                # Check for badges
                check_badge_achievements(efficiency, throughput, score)
                
                st.success(f"🎮 Session completed! +{final_xp} XP")
                st.rerun()

    # Badge showcase
    st.subheader("🏅 Badge Collection")
    
    available_badges = {
        "efficiency_master": {"name": "🎯 Efficiency Master", "desc": "Achieve 90%+ efficiency", "unlocked": False},
        "speed_demon": {"name": "🚀 Speed Demon", "desc": "Handle 2000+ vehicles/hour", "unlocked": False},
        "emergency_hero": {"name": "🚨 Emergency Hero", "desc": "Handle 5 emergency situations", "unlocked": False},
        "night_owl": {"name": "🌙 Night Owl", "desc": "Complete 10 night scenarios", "unlocked": False},
        "master_controller": {"name": "👑 Master Controller", "desc": "Reach Level 25", "unlocked": False}
    }
    
    # Update badge status
    for badge_id in st.session_state.gamified_stats["badges"]:
        if badge_id in available_badges:
            available_badges[badge_id]["unlocked"] = True

    # Display badges
    cols = st.columns(5)
    for i, (badge_id, badge_info) in enumerate(available_badges.items()):
        with cols[i % 5]:
            if badge_info["unlocked"]:
                st.success(f"✅ {badge_info['name']}")
                st.caption(badge_info['desc'])
            else:
                st.info(f"🔒 {badge_info['name']}")
                st.caption(badge_info['desc'])

def render_prit_enhanced_dashboard():
    """PRIT Enhanced Automatic I/O Dashboard"""
    
    if not PRIT_AVAILABLE:
        st.error("❌ PRIT Integration not available")
        st.info("Please install pygame and neat-python dependencies")
        return
    
    st.markdown("### 🤖 PRIT Enhanced - Automatic I/O Generation")
    st.markdown("*Neural networks meet realistic traffic simulation*")
    
    # Initialize PRIT bridge
    prit_bridge = st.session_state.prit_bridge
    
    # Control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Start Auto-Generation", type="primary"):
            result = prit_bridge.start_automatic_simulation(30)
            st.session_state.prit_active = True
            st.success("✅ Auto-generation started!")
    
    with col2:
        if st.button("⏹️ Stop Generation"):
            prit_bridge.is_running = False
            st.session_state.prit_active = False
            st.warning("⏸️ Auto-generation stopped")
    
    with col3:
        if st.button("💾 Export Data"):
            if hasattr(prit_bridge, 'real_time_data') and prit_bridge.real_time_data:
                file_path = prit_bridge.export_session_data()
                st.success(f"✅ Exported to {file_path}")

    # Status indicator
    if st.session_state.get("prit_active", False):
        st.success("🟢 **Auto-Generation ACTIVE** - Real-time data flowing!")
        
        # Live data display
        if hasattr(prit_bridge, 'get_automatic_input_output'):
            try:
                live_data = prit_bridge.get_automatic_input_output()
                
                # Input/Output display
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📥 Automatic INPUT")
                    
                    input_data = live_data.get("automatic_input", {})
                    
                    # Traffic demand
                    if "traffic_demand" in input_data:
                        st.write("**🚗 Traffic Demand**")
                        demand_df = pd.DataFrame([input_data["traffic_demand"]])
                        st.dataframe(demand_df, use_container_width=True)
                    
                    # Vehicle composition
                    if "vehicle_composition" in input_data:
                        st.write("**🚙 Vehicle Mix**")
                        comp_data = input_data["vehicle_composition"]
                        
                        # Create a pie chart
                        fig = px.pie(values=list(comp_data.values()), 
                                   names=list(comp_data.keys()),
                                   title="Vehicle Type Distribution")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("📤 Automatic OUTPUT")
                    
                    output_data = live_data.get("automatic_output", {})
                    
                    # Performance metrics
                    if "traffic_flow_metrics" in output_data:
                        flow_metrics = output_data["traffic_flow_metrics"]
                        
                        metric_col1, metric_col2, metric_col3 = st.columns(3)
                        
                        with metric_col1:
                            st.metric("Throughput", f"{flow_metrics.get('throughput', 0):.0f} veh/hr")
                        
                        with metric_col2:
                            st.metric("Efficiency", f"{flow_metrics.get('efficiency_score', 0):.1f}%")
                        
                        with metric_col3:
                            st.metric("Avg Wait", f"{flow_metrics.get('average_wait_time', 0):.1f}s")
                    
                    # AI Performance
                    if "ai_performance" in output_data:
                        ai_data = output_data["ai_performance"]
                        st.write("**🤖 AI Performance**")
                        
                        ai_col1, ai_col2 = st.columns(2)
                        with ai_col1:
                            st.metric("NEAT Fitness", f"{ai_data.get('neat_fitness', 0):.1f}")
                        with ai_col2:
                            st.metric("Decision Accuracy", f"{ai_data.get('decision_accuracy', 0):.1f}%")
                
                # Performance trends
                if hasattr(prit_bridge, 'real_time_data') and len(prit_bridge.real_time_data) > 1:
                    st.subheader("📈 Performance Trends")
                    
                    # Extract data for plotting
                    recent_data = prit_bridge.real_time_data[-20:]  # Last 20 points
                    
                    times = [d["timestamp"] for d in recent_data]
                    efficiencies = [d.get("output", {}).get("traffic_flow_metrics", {}).get("efficiency_score", 50) 
                                  for d in recent_data]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=times, y=efficiencies, mode='lines+markers',
                                           name='Efficiency %', line=dict(color='#2E8B57')))
                    fig.update_layout(title="Real-time Efficiency Trend", height=300)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Auto-refresh
                st.write(f"🔄 Last updated: {datetime.now().strftime('%H:%M:%S')}")
                time.sleep(2)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error in PRIT data generation: {e}")
                st.info("Falling back to mock data mode")
                render_mock_prit_data()
    else:
        st.info("⚪ Auto-generation ready to start")

def render_mock_prit_data():
    """Render mock PRIT data when real integration isn't available"""
    
    st.subheader("🎪 Demo Mode - Simulated PRIT Data")
    
    # Generate mock data
    mock_input = {
        "traffic_demand": {"north_bound": np.random.randint(5, 20), 
                          "south_bound": np.random.randint(5, 20),
                          "east_bound": np.random.randint(5, 20), 
                          "west_bound": np.random.randint(5, 20)},
        "vehicle_composition": {"car": np.random.randint(10, 30),
                              "bike": np.random.randint(5, 20),
                              "bus": np.random.randint(1, 5),
                              "truck": np.random.randint(2, 8),
                              "rickshaw": np.random.randint(3, 12)}
    }
    
    mock_output = {
        "traffic_flow_metrics": {
            "throughput": np.random.uniform(1500, 2000),
            "efficiency_score": np.random.uniform(75, 95),
            "average_wait_time": np.random.uniform(5, 15)
        },
        "ai_performance": {
            "neat_fitness": np.random.uniform(80, 95),
            "decision_accuracy": np.random.uniform(85, 98)
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**📥 Mock INPUT**")
        st.json(mock_input)
    
    with col2:
        st.write("**📤 Mock OUTPUT**")
        
        metrics = mock_output["traffic_flow_metrics"]
        ai_metrics = mock_output["ai_performance"]
        
        mcol1, mcol2 = st.columns(2)
        with mcol1:
            st.metric("Throughput", f"{metrics['throughput']:.0f} veh/hr")
            st.metric("NEAT Fitness", f"{ai_metrics['neat_fitness']:.1f}")
        with mcol2:
            st.metric("Efficiency", f"{metrics['efficiency_score']:.1f}%")
            st.metric("Decision Accuracy", f"{ai_metrics['decision_accuracy']:.1f}%")

def generate_gamified_simulation_data(scenario, difficulty):
    """Generate realistic simulation data for gamified mode"""
    
    # Base values adjusted by scenario and difficulty
    base_efficiency = {
        "Easy": 85, "Medium": 75, "Hard": 65, "Expert": 55
    }[difficulty]
    
    scenario_modifiers = {
        "Morning Rush": {"efficiency": -10, "throughput": +300, "score": 1.2},
        "Evening Rush": {"efficiency": -15, "throughput": +400, "score": 1.3},
        "Weekend": {"efficiency": +5, "throughput": -100, "score": 0.9},
        "Night Time": {"efficiency": +10, "throughput": -200, "score": 0.8},
        "Event Traffic": {"efficiency": -20, "throughput": +500, "score": 1.5}
    }
    
    modifier = scenario_modifiers.get(scenario, {"efficiency": 0, "throughput": 0, "score": 1.0})
    
    efficiency = max(30, min(100, base_efficiency + modifier["efficiency"] + np.random.uniform(-5, 10)))
    throughput = max(800, 1600 + modifier["throughput"] + np.random.uniform(-100, 200))
    score = int((efficiency + throughput/20) * modifier["score"] + np.random.uniform(-10, 20))
    
    return {
        "efficiency": efficiency,
        "throughput": throughput,
        "score": max(0, score)
    }

def check_badge_achievements(efficiency, throughput, score):
    """Check and award badges based on performance"""
    
    new_badges = []
    
    if efficiency > 90 and "efficiency_master" not in st.session_state.gamified_stats["badges"]:
        st.session_state.gamified_stats["badges"].append("efficiency_master")
        new_badges.append("🎯 Efficiency Master")
    
    if throughput > 2000 and "speed_demon" not in st.session_state.gamified_stats["badges"]:
        st.session_state.gamified_stats["badges"].append("speed_demon") 
        new_badges.append("🚀 Speed Demon")
    
    if st.session_state.gamified_stats["level"] >= 25 and "master_controller" not in st.session_state.gamified_stats["badges"]:
        st.session_state.gamified_stats["badges"].append("master_controller")
        new_badges.append("👑 Master Controller")
    
    if new_badges:
        for badge in new_badges:
            st.success(f"🏅 **NEW BADGE UNLOCKED:** {badge}!")

def main():
    """Main unified dashboard application"""
    
    st.set_page_config(
        page_title="UrbanFlow360 - Unified Traffic Management",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; text-align: center;'>
        <h1 style='color: white; margin: 0; font-size: 3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
            🚦 UrbanFlow360
        </h1>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 1.4rem; opacity: 0.9;'>
            Unified Traffic Management Platform
        </p>
        <div style='margin-top: 1rem;'>
            <span style='background: rgba(255,255,255,0.2); padding: 0.3rem 1rem; border-radius: 20px; margin: 0 0.5rem;'>
                Professional
            </span>
            <span style='background: rgba(255,255,255,0.2); padding: 0.3rem 1rem; border-radius: 20px; margin: 0 0.5rem;'>
                Gamified
            </span>
            <span style='background: rgba(255,255,255,0.2); padding: 0.3rem 1rem; border-radius: 20px; margin: 0 0.5rem;'>
                PRIT Enhanced
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Interface selector
    interface_options = [
        "🏢 Professional Dashboard",
        "🎮 Gamified Experience", 
        "🤖 PRIT Enhanced Auto-I/O"
    ]
    
    selected_interface = st.selectbox(
        "Choose Interface Mode:", 
        interface_options,
        index=0,
        label_visibility="collapsed"
    )
    
    st.session_state.current_interface = selected_interface
    
    # Render selected interface
    if selected_interface == "🏢 Professional Dashboard":
        render_professional_dashboard()
    
    elif selected_interface == "🎮 Gamified Experience":
        render_gamified_dashboard()
        
    elif selected_interface == "🤖 PRIT Enhanced Auto-I/O":
        render_prit_enhanced_dashboard()
    
    # Footer with system status
    st.markdown("---")
    
    footer_cols = st.columns(4)
    
    with footer_cols[0]:
        st.metric("🏢 Professional", "✅ Ready")
    
    with footer_cols[1]:
        st.metric("🎮 Gamified", "✅ Ready")
    
    with footer_cols[2]:
        if PRIT_AVAILABLE:
            st.metric("🤖 PRIT Enhanced", "✅ Ready")
        else:
            st.metric("🤖 PRIT Enhanced", "⚠️ Demo Mode")
    
    with footer_cols[3]:
        st.metric("🔧 System Status", "🟢 Operational")
    
    # Quick stats in sidebar
    with st.sidebar:
        st.markdown("---")
        st.header("📊 Quick Stats")
        
        if "gamified_stats" in st.session_state:
            stats = st.session_state.gamified_stats
            st.write(f"🎮 Player Level: **{stats['level']}**")
            st.write(f"⭐ Total XP: **{stats['xp']}**") 
            st.write(f"🏅 Badges: **{len(stats['badges'])}**")
            st.write(f"🎯 Sessions: **{stats.get('sessions_played', 0)}**")
        
        st.markdown("---")
        st.markdown("**🚦 UrbanFlow360**")
        st.markdown("*Unified Traffic Management*")
        st.markdown("Built with ❤️ using Streamlit")

if __name__ == "__main__":
    main()
