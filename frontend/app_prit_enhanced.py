"""
UrbanFlow360 - PRIT Enhanced Gamified Traffic Management
Automatic Input/Output Generation with AI-Powered Simulation
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import asyncio

# Import our integration bridge
try:
    from backend.prit_integration.game_bridge import PritGameBridge
    PRIT_AVAILABLE = True
except ImportError:
    PRIT_AVAILABLE = False
    st.error("⚠️ PRIT Integration not available. Please install pygame and neat-python.")

def initialize_prit_session():
    """Initialize PRIT integration session"""
    
    if "prit_bridge" not in st.session_state:
        config = {
            "simulation_speed": 1.0,
            "auto_generation": True,
            "neat_enabled": True,
            "vehicle_variety": True
        }
        st.session_state.prit_bridge = PritGameBridge(config)
        st.session_state.prit_active = False
    
    return st.session_state.prit_bridge

def main():
    st.set_page_config(
        page_title="UrbanFlow360 - PRIT Enhanced",
        page_icon="🚦",
        layout="wide"
    )
    
    # Header
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; text-align: center; margin: 0;'>
            🚦 UrbanFlow360 - PRIT Enhanced 🤖
        </h1>
        <p style='color: white; text-align: center; margin: 0.5rem 0 0 0;'>
            Automatic Input/Output Traffic Data Generation with AI
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not PRIT_AVAILABLE:
        st.error("❌ PRIT Integration unavailable. Please install dependencies.")
        return
    
    # Initialize PRIT bridge
    prit_bridge = initialize_prit_session()
    
    # Sidebar controls
    with st.sidebar:
        st.header("🎮 PRIT Control Panel")
        
        # Auto-generation controls
        st.subheader("🔄 Automatic Generation")
        
        if st.button("🚀 Start Auto-Simulation", type="primary"):
            duration = st.slider("Duration (minutes)", 5, 120, 30)
            result = prit_bridge.start_automatic_simulation(duration)
            st.session_state.prit_active = True
            st.success(f"✅ {result['status'].title()}!")
            st.json(result)
        
        if st.button("⏹️ Stop Simulation"):
            prit_bridge.is_running = False
            st.session_state.prit_active = False
            st.warning("⏸️ Simulation stopped")
        
        # Export controls
        st.subheader("📁 Data Export")
        if st.button("💾 Export Session Data"):
            if hasattr(prit_bridge, 'real_time_data') and prit_bridge.real_time_data:
                file_path = prit_bridge.export_session_data()
                st.success(f"✅ Exported to: {file_path}")
                
                # Download link
                with open(file_path, 'rb') as file:
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=file,
                        file_name=file_path.split('\\')[-1],
                        mime='text/csv'
                    )
            else:
                st.warning("⚠️ No data to export yet")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔄 Live Auto-Generation", 
        "📊 Performance Dashboard", 
        "🎯 AI Analytics", 
        "🏆 Player Progress"
    ])
    
    with tab1:
        st.header("🔄 Automatic Input → Output Generation")
        
        # Status indicator
        if st.session_state.get("prit_active", False):
            st.success("🟢 **Auto-Generation ACTIVE** - Real-time data flowing!")
        else:
            st.info("⚪ Auto-Generation ready to start")
        
        # Live data generation
        if st.session_state.get("prit_active", False):
            
            # Auto-refresh every 2 seconds
            placeholder = st.empty()
            
            with placeholder.container():
                # Generate new input/output data
                live_data = prit_bridge.get_automatic_input_output()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📥 **Automatic INPUT**")
                    
                    input_data = live_data["automatic_input"]
                    
                    # Traffic Demand
                    st.write("**🚗 Traffic Demand**")
                    demand_df = pd.DataFrame([input_data["traffic_demand"]])
                    st.dataframe(demand_df, use_container_width=True)
                    
                    # Vehicle Composition
                    st.write("**🚙 Vehicle Mix**")
                    comp_df = pd.DataFrame([input_data["vehicle_composition"]])
                    st.dataframe(comp_df, use_container_width=True)
                    
                    # Signal Status
                    st.write("**🚦 Signal Timing**")
                    signal_data = input_data["signal_timing"]
                    st.write(f"Current Phase: **{signal_data['current_phase']}**")
                    st.write(f"Time in Phase: **{signal_data['time_in_phase']:.1f}s**")
                    
                    # Environmental
                    st.write("**🌤️ Environmental**")
                    env_df = pd.DataFrame([input_data["environmental_factors"]])
                    st.dataframe(env_df, use_container_width=True)
                
                with col2:
                    st.subheader("📤 **Automatic OUTPUT**")
                    
                    output_data = live_data["automatic_output"]
                    
                    # Performance Metrics
                    st.write("**📈 Traffic Flow Metrics**")
                    flow_metrics = output_data["traffic_flow_metrics"]
                    
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Throughput", f"{flow_metrics['throughput']:.0f} veh/hr")
                    col_b.metric("Efficiency", f"{flow_metrics['efficiency_score']:.1f}%")
                    col_c.metric("Avg Wait", f"{flow_metrics['average_wait_time']:.1f}s")
                    
                    # AI Performance
                    st.write("**🤖 AI Performance**")
                    ai_metrics = output_data["ai_performance"]
                    
                    col_d, col_e = st.columns(2)
                    col_d.metric("NEAT Fitness", f"{ai_metrics['neat_fitness']:.1f}")
                    col_e.metric("Decision Accuracy", f"{ai_metrics['decision_accuracy']:.1f}%")
                    
                    # Environmental Impact
                    st.write("**🌱 Environmental Impact**")
                    env_impact = output_data["environmental_impact"]
                    st.write(f"Fuel Saved: **{env_impact['fuel_consumption']}**")
                    st.write(f"Emissions: **{env_impact['emissions_reduction']}**")
                    
                    # Real-time Status
                    st.write("**⚡ Real-time Status**")
                    status = output_data["real_time_status"]
                    st.write(f"Active Vehicles: **{status['vehicles_in_system']}**")
                    st.write(f"Completed: **{status['completed_journeys']}**")
                
                # Live charts
                st.subheader("📊 Live Performance Charts")
                
                if len(prit_bridge.real_time_data) > 1:
                    # Prepare time series data
                    times = [d["timestamp"] for d in prit_bridge.real_time_data[-20:]]  # Last 20 points
                    efficiencies = [d["output"]["traffic_flow_metrics"]["efficiency_score"] 
                                  for d in prit_bridge.real_time_data[-20:]]
                    throughputs = [d["output"]["traffic_flow_metrics"]["throughput"] 
                                 for d in prit_bridge.real_time_data[-20:]]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig1 = go.Figure()
                        fig1.add_trace(go.Scatter(x=times, y=efficiencies, mode='lines+markers', 
                                                name='Efficiency %', line=dict(color='#2E8B57')))
                        fig1.update_layout(title="Real-time Efficiency", height=300)
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        fig2 = go.Figure()
                        fig2.add_trace(go.Scatter(x=times, y=throughputs, mode='lines+markers',
                                                name='Throughput', line=dict(color='#4169E1')))
                        fig2.update_layout(title="Real-time Throughput", height=300)
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Auto-refresh indicator
                st.write(f"🔄 Last updated: {datetime.now().strftime('%H:%M:%S')}")
                
            # Auto-refresh every 2 seconds
            time.sleep(2)
            st.rerun()
    
    with tab2:
        st.header("📊 PRIT Performance Dashboard")
        
        # Get dashboard summary
        dashboard_summary = prit_bridge.get_dashboard_summary()
        
        if "status" in dashboard_summary and "No data" in dashboard_summary["status"]:
            st.info("⚪ Start auto-generation to see performance data")
        else:
            # Key metrics
            st.subheader("🎯 Key Performance Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            current_perf = dashboard_summary["current_performance"]
            col1.metric("🏆 Efficiency", f"{current_perf['efficiency']:.1f}%")
            col2.metric("🚀 Throughput", f"{current_perf['throughput']:.0f} veh/hr")
            col3.metric("🤖 AI Fitness", f"{current_perf['ai_fitness']:.1f}")
            col4.metric("📊 Data Points", dashboard_summary["data_points_generated"])
            
            # Session overview
            st.subheader("📈 Session Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🎮 Session Stats**")
                st.write(f"Status: {dashboard_summary['status']}")
                st.write(f"Mode: {dashboard_summary['mode']}")
                st.write(f"Duration: {dashboard_summary['session_duration']}")
                st.write(f"Vehicles Managed: {dashboard_summary['vehicles_simulated']}")
            
            with col2:
                st.write("**🏅 Player Progress**")
                player = dashboard_summary['player_progress']
                st.write(f"Level: **{player['level']}**")
                st.write(f"XP: **{player['xp']}**")
                st.write(f"Badges: **{len(player['badges'])}**")
                st.write(f"Best Efficiency: **{player['best_efficiency']:.1f}%**")
            
            # Performance trends
            if len(prit_bridge.real_time_data) > 5:
                st.subheader("📈 Performance Trends")
                
                # Create performance DataFrame
                df_data = []
                for point in prit_bridge.real_time_data:
                    df_data.append({
                        "Time": point["timestamp"],
                        "Efficiency": point["output"]["traffic_flow_metrics"]["efficiency_score"],
                        "Throughput": point["output"]["traffic_flow_metrics"]["throughput"],
                        "AI_Fitness": point["output"]["ai_performance"]["neat_fitness"],
                        "Vehicles": point["output"]["real_time_status"]["vehicles_in_system"]
                    })
                
                trend_df = pd.DataFrame(df_data)
                
                # Multi-line chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=trend_df["Time"], y=trend_df["Efficiency"], 
                                       name="Efficiency %", line=dict(color='green')))
                fig.add_trace(go.Scatter(x=trend_df["Time"], y=trend_df["AI_Fitness"], 
                                       name="AI Fitness", line=dict(color='blue')))
                fig.update_layout(title="Performance Trends Over Time", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("🤖 PRIT + NEAT AI Analytics")
        
        st.write("**🧠 Neural Evolution & Traffic Optimization**")
        
        if len(prit_bridge.real_time_data) > 0:
            latest_data = prit_bridge.real_time_data[-1]
            ai_data = latest_data["output"]["ai_performance"]
            
            col1, col2, col3 = st.columns(3)
            
            col1.metric("🎯 NEAT Fitness Score", f"{ai_data['neat_fitness']:.1f}/100")
            col2.metric("📈 Learning Progress", f"{ai_data['learning_progress']:.1f}%")
            col3.metric("🎪 Decision Accuracy", f"{ai_data['decision_accuracy']:.1f}%")
            
            # AI Decision Analysis
            st.subheader("🧩 AI Decision Analysis")
            
            # Create sample AI decision data
            if len(prit_bridge.real_time_data) > 10:
                recent_decisions = prit_bridge.real_time_data[-10:]
                
                decision_data = []
                for i, point in enumerate(recent_decisions):
                    decision_data.append({
                        "Decision": f"D{i+1}",
                        "Input_Complexity": np.random.uniform(0.3, 1.0),
                        "Output_Quality": point["output"]["ai_performance"]["neat_fitness"] / 100,
                        "Efficiency_Impact": point["output"]["traffic_flow_metrics"]["efficiency_score"] / 100
                    })
                
                decision_df = pd.DataFrame(decision_data)
                
                fig = px.scatter(decision_df, x="Input_Complexity", y="Output_Quality", 
                               size="Efficiency_Impact", title="AI Decision Quality vs Input Complexity",
                               color="Efficiency_Impact", color_continuous_scale="viridis")
                st.plotly_chart(fig, use_container_width=True)
            
            # Vehicle Type Analysis
            st.subheader("🚗 Vehicle Type Performance")
            
            latest_input = latest_data["input"]["vehicle_composition"]
            
            vehicle_df = pd.DataFrame([latest_input])
            fig = px.bar(x=list(latest_input.keys()), y=list(latest_input.values()),
                        title="Current Vehicle Type Distribution",
                        color=list(latest_input.values()), color_continuous_scale="plasma")
            st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("🤖 Start simulation to see AI analytics")
    
    with tab4:
        st.header("🏆 Player Progress & Gamification")
        
        if hasattr(prit_bridge, 'player_stats'):
            player = prit_bridge.player_stats
            
            # Player overview
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("🎮 Level", player["level"])
            col2.metric("⭐ XP", player["xp"])
            col3.metric("🏅 Badges", len(player["badges"]))
            col4.metric("🏆 Total Score", player["total_score"])
            
            # XP Progress bar
            xp_for_next = (player["level"] * 100) - player["xp"]
            progress = (player["xp"] % 100) / 100
            
            st.write("**📈 XP Progress to Next Level**")
            st.progress(progress)
            st.write(f"Need {xp_for_next} XP for Level {player['level'] + 1}")
            
            # Badges earned
            st.subheader("🏅 Badges Earned")
            
            if player["badges"]:
                badge_descriptions = {
                    "efficiency_master": "🎯 Efficiency Master - Achieved 90%+ efficiency",
                    "traffic_guru": "🚀 Traffic Guru - Handled 1800+ vehicles/hour",
                    "ai_optimizer": "🤖 AI Optimizer - NEAT fitness score 85+",
                    "eco_warrior": "🌱 Eco Warrior - Maximum emissions reduction",
                    "flow_master": "⚡ Flow Master - Managed 20+ concurrent vehicles"
                }
                
                for badge in player["badges"]:
                    if badge in badge_descriptions:
                        st.success(badge_descriptions[badge])
            else:
                st.info("🎯 No badges earned yet - keep playing to unlock achievements!")
            
            # Performance records
            st.subheader("📊 Personal Records")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**🏆 Best Achievements**")
                st.write(f"Best Efficiency: **{player['best_efficiency']:.1f}%**")
                st.write(f"Total Vehicles Managed: **{player['vehicles_managed']}**")
                st.write(f"Highest Score: **{player['total_score']}**")
            
            with col2:
                st.write("**📈 Session Statistics**")
                if len(prit_bridge.real_time_data) > 0:
                    session_efficiency = [d["output"]["traffic_flow_metrics"]["efficiency_score"] 
                                        for d in prit_bridge.real_time_data]
                    st.write(f"Average Efficiency: **{np.mean(session_efficiency):.1f}%**")
                    st.write(f"Peak Performance: **{np.max(session_efficiency):.1f}%**")
                    st.write(f"Data Points Generated: **{len(prit_bridge.real_time_data)}**")
        
        else:
            st.info("🎮 Start playing to track your progress!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 1rem;'>
        🚦 <b>UrbanFlow360 - PRIT Enhanced</b> | 
        Automatic Input/Output Generation | 
        AI-Powered Traffic Management | 
        Built with Streamlit + pygame + NEAT
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
