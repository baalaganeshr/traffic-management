"""
Modern Smart Traffic Management System Demo
Clean implementation with card-based UI matching mobile screenshots
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import random

def init_session_state():
    """Initialize all session state variables to prevent conflicts"""
    # Core app state
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
    if 'current_cycle' not in st.session_state:
        st.session_state.current_cycle = 0
    if 'incident_count' not in st.session_state:
        st.session_state.incident_count = 0
    if 'auto_refresh_enabled' not in st.session_state:
        st.session_state.auto_refresh_enabled = True
    
    # AI control state (unique names to avoid widget conflicts)
    if 'ai_mode_active' not in st.session_state:
        st.session_state.ai_mode_active = True
    if 'manual_override_status' not in st.session_state:
        st.session_state.manual_override_status = False

# Page configuration
st.set_page_config(
    page_title="Smart Traffic Management System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Styling (keep the traffic light CSS)
st.markdown("""
<style>
/* Main theme */
.stApp {
    background: linear-gradient(180deg, #0e1425, #1a202c);
}

/* Traffic Light CSS - CRITICAL */
.traffic-intersection {
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    width: 300px;
    height: 300px;
    margin: 2rem auto;
    background: #1e293b;
    border-radius: 15px;
    padding: 20px;
    border: 2px solid #334155;
}

.traffic-light {
    position: absolute;
    display: flex;
    flex-direction: column;
    background: linear-gradient(145deg, #4a5568, #2d3748);
    border-radius: 18px;
    padding: 10px;
    border: 3px solid #1a202c;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
}

.traffic-light.vertical {
    width: 40px;
    height: 120px;
}

.traffic-light.horizontal {
    width: 120px;
    height: 40px;
    flex-direction: row;
}

.light {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    margin: 4px;
    border: 2px solid rgba(255,255,255,0.3);
    transition: all 0.3s ease;
}

.light.red {
    background: radial-gradient(circle at 30% 30%, #ff6b6b, #dc2626, #991b1b) !important;
    box-shadow: 0 0 20px rgba(220, 38, 38, 0.9), inset 0 1px 3px rgba(255,255,255,0.3) !important;
    border: 2px solid #7f1d1d !important;
}

.light.red.off {
    background: radial-gradient(circle at 30% 30%, #450a0a, #7f1d1d, #450a0a) !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5) !important;
    border: 2px solid #450a0a !important;
}

.light.yellow {
    background: radial-gradient(circle at 30% 30%, #fde047, #f59e0b, #d97706) !important;
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.9), inset 0 1px 3px rgba(255,255,255,0.3) !important;
    border: 2px solid #92400e !important;
}

.light.yellow.off {
    background: radial-gradient(circle at 30% 30%, #451a03, #78350f, #451a03) !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5) !important;
    border: 2px solid #451a03 !important;
}

.light.green {
    background: radial-gradient(circle at 30% 30%, #4ade80, #16a34a, #15803d) !important;
    box-shadow: 0 0 20px rgba(22, 163, 74, 0.9), inset 0 1px 3px rgba(255,255,255,0.3) !important;
    border: 2px solid #14532d !important;
}

.light.green.off {
    background: radial-gradient(circle at 30% 30%, #052e16, #14532d, #052e16) !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5) !important;
    border: 2px solid #052e16 !important;
}

.traffic-north {
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
}

.traffic-south {
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
}

.traffic-east {
    right: -10px;
    top: 50%;
    transform: translateY(-50%);
}

.traffic-west {
    left: -10px;
    top: 50%;
    transform: translateY(-50%);
}

.intersection-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90px;
    height: 90px;
    background: linear-gradient(45deg, #6b7280, #4b5563, #374151);
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    border: 3px solid #1f2937;
    box-shadow: 0 6px 16px rgba(0,0,0,0.4), inset 0 2px 4px rgba(255,255,255,0.1);
}

/* Back button */
.back-button {
    background: linear-gradient(135deg, #3b82f6 0%, #4f46e5 100%);
    color: white !important;
    padding: 12px 24px;
    border-radius: 50px;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 14px;
    border: none;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.back-button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #3b36ef 100%);
    color: white !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    text-decoration: none !important;
}

.back-arrow {
    font-size: 16px;
    font-weight: 700;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

def get_live_traffic_data():
    """Generate realistic live traffic data with cycling states"""
    # Cycle through traffic states realistically
    cycle_time = int(time.time() / 5) % 60  # 60 second cycles, update every 5 seconds
    
    if cycle_time < 25:  # NS Green (25 seconds)
        ns_state = "green"
        ew_state = "red"
        ns_timer = f"{25 - cycle_time}s"
        ew_timer = "STOP"
    elif cycle_time < 28:  # NS Yellow (3 seconds)
        ns_state = "yellow"
        ew_state = "red"
        ns_timer = f"{28 - cycle_time}s"
        ew_timer = "STOP"
    elif cycle_time < 53:  # EW Green (25 seconds)
        ns_state = "red"
        ew_state = "green"
        ns_timer = "STOP"
        ew_timer = f"{53 - cycle_time}s"
    else:  # EW Yellow (3 seconds)
        ns_state = "red"
        ew_state = "yellow"
        ns_timer = "STOP"
        ew_timer = f"{60 - cycle_time}s"
    
    # Generate realistic vehicle counts based on time and state
    base_ns = random.randint(120, 180)
    base_ew = random.randint(80, 120)
    
    # Adjust based on signal state (waiting vehicles decrease during green)
    ns_vehicles = base_ns if ns_state == "red" else max(20, base_ns - random.randint(30, 50))
    ew_vehicles = base_ew if ew_state == "red" else max(15, base_ew - random.randint(20, 40))
    
    return ns_vehicles, ew_vehicles, ns_state, ew_state, ns_timer, ew_timer

def create_traffic_light_display(state):
    """Create a compact traffic light display"""
    red_class = "light red" if state == "red" else "light red off"
    yellow_class = "light yellow" if state == "yellow" else "light yellow off"
    green_class = "light green" if state == "green" else "light green off"
    
    return f"""
    <div style="display: flex; flex-direction: column; align-items: center; background: linear-gradient(145deg, #4a5568, #2d3748); border-radius: 12px; padding: 8px; width: 35px; margin: 0 auto;">
        <div class="{red_class}" style="width: 20px; height: 20px; border-radius: 50%; margin: 2px;"></div>
        <div class="{yellow_class}" style="width: 20px; height: 20px; border-radius: 50%; margin: 2px;"></div>
        <div class="{green_class}" style="width: 20px; height: 20px; border-radius: 50%; margin: 2px;"></div>
    </div>
    """


def render_vehicle_analytics():
    """Render vehicle type analytics chart like mobile screenshot"""
    
    # Generate realistic vehicle data based on time and traffic cycle
    current_cycle = st.session_state.get('current_cycle', 0)
    time_factor = (current_cycle % 12) / 12  # Create variation over 12 cycles
    
    # Base vehicle counts with realistic traffic patterns
    base_cars = 40 + int(15 * time_factor)
    base_buses = 10 + int(5 * (1 - time_factor))  # Fewer buses during peak
    base_bikes = 20 + int(10 * time_factor)
    base_trucks = 15 + int(8 * (0.5 - abs(time_factor - 0.5)))  # Moderate variation
    
    # Add some randomness but keep it realistic
    vehicle_data = {
        "Car": base_cars + random.randint(-5, 5),
        "Bus": base_buses + random.randint(-2, 3), 
        "Bike": base_bikes + random.randint(-3, 3),
        "Truck": base_trucks + random.randint(-3, 3)
    }
    
    # Ensure no negative values
    vehicle_data = {k: max(1, v) for k, v in vehicle_data.items()}
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(vehicle_data.keys()),
            y=list(vehicle_data.values()),
            marker_color=['#3b82f6', '#06b6d4', '#10b981', '#f59e0b'],
            text=list(vehicle_data.values()),
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text=f"count: {sum(vehicle_data.values())}",
            x=0.5,
            font=dict(size=16, color='white')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=40),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', range=[0, max(vehicle_data.values()) + 10])
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_ai_control_panel(ns_state, ew_state, ns_vehicles, ew_vehicles, ns_timer, ew_timer):
    """Render AI control panel matching mobile screenshot"""
    
    # Ensure session state is initialized
    # Use consistent session state variables (managed by init_session_state)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Mode**")
        if st.session_state.ai_mode_active:
            st.success("🤖 AI Adaptive")
        else:
            st.warning("👤 Manual")
    
    with col2:
        if st.button("Toggle Mode", use_container_width=True, key="toggle_ai_mode"):
            st.session_state.ai_mode_active = not st.session_state.ai_mode_active
            st.rerun()
    
    st.markdown("**Current AI Timings**")
    
    # Enhanced timing displays with real data
    col1, col2 = st.columns([3, 1])
    with col1:
        # Calculate progress based on actual state
        if ns_state == "green":
            progress_val = max(0.1, int(ns_timer.replace('s', '')) / 25) if 's' in ns_timer else 0.5
        elif ns_state == "yellow":
            progress_val = max(0.1, int(ns_timer.replace('s', '')) / 3) if 's' in ns_timer else 0.3
        else:
            progress_val = 0.1
            
        st.progress(progress_val, text=f"Lane N/S ({ns_vehicles} vehicles)")
        
    with col2:
        timer_color = '#4ade80' if ns_state == 'green' else '#ef4444' if ns_state == 'red' else '#fbbf24'
        st.markdown(f"""
        <div style="text-align: center; padding: 0.75rem; background: rgba(30, 41, 59, 0.6); border-radius: 8px; border: 1px solid #475569;">
            <div style="color: {timer_color}; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.25rem;">
                {ns_timer if ns_timer != 'STOP' else '⏹️'}
            </div>
            <div style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;">
                {ns_state.title()}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # EW Lane timing with real data 
    col1, col2 = st.columns([3, 1])
    with col1:
        # Calculate progress based on actual state
        if ew_state == "green":
            progress_val = max(0.1, int(ew_timer.replace('s', '')) / 25) if 's' in ew_timer else 0.5
        elif ew_state == "yellow":
            progress_val = max(0.1, int(ew_timer.replace('s', '')) / 3) if 's' in ew_timer else 0.3
        else:
            progress_val = 0.1
            
        st.progress(progress_val, text=f"Lane E/W ({ew_vehicles} vehicles)")
        
    with col2:
        timer_color = '#4ade80' if ew_state == 'green' else '#ef4444' if ew_state == 'red' else '#fbbf24'
        st.markdown(f"""
        <div style="text-align: center; padding: 0.75rem; background: rgba(30, 41, 59, 0.6); border-radius: 8px; border: 1px solid #475569;">
            <div style="color: {timer_color}; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.25rem;">
                {ew_timer if ew_timer != 'STOP' else '⏹️'}
            </div>
            <div style="color: #94a3b8; font-size: 0.8rem; text-transform: uppercase;">
                {ew_state.title()}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Action buttons with enhanced styling
    st.markdown("**Controls**")
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        if st.button("🎯 View Live Signal", use_container_width=True, type="primary", key="view_signal_ai"):
            show_live_signal_modal(ns_state, ew_state, ns_vehicles, ew_vehicles, ns_timer, ew_timer)
    with col2:
        if st.button("🔧 Manual Override", use_container_width=True, type="secondary", key="manual_override_btn"):
            st.session_state.manual_override_status = True
            st.warning("Manual override activated!")
    
    # Enhanced manual override status display
    if st.session_state.get('manual_override_status', False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #fbbf24, #f59e0b); padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 4px solid #d97706;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">🔧</span>
                <span style="color: #1f2937; font-weight: 600;">Manual Override Active</span>
            </div>
            <p style="color: #374151; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                System is under manual control. Automatic optimization is paused.
            </p>
        </div>
        """, unsafe_allow_html=True)

def show_live_signal_modal(ns_state, ew_state, ns_vehicles, ew_vehicles, ns_timer, ew_timer):
    """Show the live signal modal like in mobile screenshot"""
    
    # Simple display without expander to avoid HTML issues
    st.markdown("### 🚦 Live Signal: Oak & Main")
    
    # Create a simple traffic intersection display
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**North-South Direction**")
        if ns_state == "green":
            st.success(f"🟢 GREEN - {ns_timer}")
        elif ns_state == "yellow":
            st.warning(f"🟡 YELLOW - {ns_timer}")
        else:
            st.error(f"🔴 RED - {ns_timer}")
        st.metric("Vehicles Waiting", f"{ns_vehicles}")
    
    with col2:
        st.markdown("**East-West Direction**")
        if ew_state == "green":
            st.success(f"🟢 GREEN - {ew_timer}")
        elif ew_state == "yellow":
            st.warning(f"🟡 YELLOW - {ew_timer}")
        else:
            st.error(f"🔴 RED - {ew_timer}")
        st.metric("Vehicles Waiting", f"{ew_vehicles}")
    
    # Simple intersection diagram using text
    ns_color = '#4ade80' if ns_state == 'green' else '#ef4444' if ns_state == 'red' else '#fbbf24'
    ew_color = '#4ade80' if ew_state == 'green' else '#ef4444' if ew_state == 'red' else '#fbbf24'
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: rgba(30, 41, 59, 0.5); border-radius: 12px; margin: 1rem 0;">
        <div style="font-size: 3rem; line-height: 1;">
            🚦<br/>
            ⬆️ N/S: <span style="color: {ns_color}">{ns_state.upper()}</span><br/>
            ↔️ E/W: <span style="color: {ew_color}">{ew_state.upper()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_emergency_feed():
    """Render emergency incident feed matching mobile screenshot"""
    
    # Generate realistic incidents
    incidents = [
        {
            "type": "🚨",
            "title": "AI Detection: Sudden Stop & Congestion", 
            "location": "Oak & Main",
            "time": "19:25:54",
            "severity": "high"
        },
        {
            "type": "⚠️", 
            "title": "AI Detection: Heavy Traffic Buildup",
            "location": "Oak & Main", 
            "time": "19:25:39",
            "severity": "medium"
        },
        {
            "type": "ℹ️",
            "title": "Signal Optimization Applied",
            "location": "Oak & Main",
            "time": "19:24:12", 
            "severity": "low"
        }
    ]
    
    for incident in incidents:
        color = "#ef4444" if incident["severity"] == "high" else "#f59e0b" if incident["severity"] == "medium" else "#06b6d4"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; padding: 1rem; background: rgba(30, 41, 59, 0.5); border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {color};">
            <div style="font-size: 1.5rem; margin-right: 1rem;">{incident["type"]}</div>
            <div style="flex: 1;">
                <div style="color: white; font-weight: 600; margin-bottom: 0.25rem;">{incident["title"]}</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">{incident["location"]} - {incident["time"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_modern_dashboard():
    """Render the modern card-based dashboard matching mobile screenshots"""
    
    # Live Signal Status Card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #334155); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #475569;">
        <h3 style="color: white; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            🚦 Live Signal: Oak & Main
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current traffic data
    ns_vehicles, ew_vehicles, ns_state, ew_state, ns_timer, ew_timer = get_live_traffic_data()
    
    # Signal Status Display with improved alignment
    col1, col2 = st.columns(2, gap="medium")
    
    with col1:
        # Create traffic light HTML with enhanced styling
        red_class = "light red" if ns_state == "red" else "light red off"
        yellow_class = "light yellow" if ns_state == "yellow" else "light yellow off"
        green_class = "light green" if ns_state == "green" else "light green off"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: rgba(30, 41, 59, 0.8); border-radius: 12px; margin-bottom: 1rem; border: 1px solid #475569; height: 280px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; box-sizing: border-box;">
            <div style="flex-shrink: 0;">
                <h4 style="color: white; margin: 0 0 0.5rem 0; font-size: 1.1rem;">Lane N/S</h4>
                <p style="color: #94a3b8; margin: 0 0 1rem 0; font-size: 0.9rem;">{ns_vehicles} vehicles waiting</p>
            </div>
            <div style="flex: 1; display: flex; align-items: center; justify-content: center;">
                <div style="display: flex; flex-direction: column; align-items: center; background: linear-gradient(145deg, #4a5568, #2d3748); border-radius: 15px; padding: 12px; width: 45px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                    <div class="{red_class}" style="width: 24px; height: 24px; border-radius: 50%; margin: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                    <div class="{yellow_class}" style="width: 24px; height: 24px; border-radius: 50%; margin: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                    <div class="{green_class}" style="width: 24px; height: 24px; border-radius: 50%; margin: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                </div>
            </div>
            <div style="flex-shrink: 0; padding: 0.5rem 0;">
                <p style="color: {'#4ade80' if ns_state == 'green' else '#ef4444' if ns_state == 'red' else '#fbbf24'}; font-size: 1.4rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); line-height: 1.2;">
                    {ns_timer if ns_state != 'red' else 'STOP'}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Create traffic light HTML with enhanced styling
        red_class = "light red" if ew_state == "red" else "light red off"
        yellow_class = "light yellow" if ew_state == "yellow" else "light yellow off"
        green_class = "light green" if ew_state == "green" else "light green off"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1.5rem; background: rgba(30, 41, 59, 0.8); border-radius: 12px; margin-bottom: 1rem; border: 1px solid #475569; height: 280px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden; box-sizing: border-box;">
            <div style="flex-shrink: 0;">
                <h4 style="color: white; margin: 0 0 0.5rem 0; font-size: 1.1rem;">Lane E/W</h4>
                <p style="color: #94a3b8; margin: 0 0 1rem 0; font-size: 0.9rem;">{ew_vehicles} vehicles waiting</p>
            </div>
            <div style="flex: 1; display: flex; align-items: center; justify-content: center;">
                <div style="display: flex; flex-direction: column; align-items: center; background: linear-gradient(145deg, #4a5568, #2d3748); border-radius: 15px; padding: 12px; width: 45px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                    <div class="{red_class}" style="width: 24px; height: 24px; border-radius: 50%; margin: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                    <div class="{yellow_class}" style="width: 24px; height: 24px; border-radius: 50%; margin: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                    <div class="{green_class}" style="width: 24px; height: 24px; border-radius: 50%; margin: 3px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>
                </div>
            </div>
            <div style="flex-shrink: 0; padding: 0.5rem 0;">
                <p style="color: {'#4ade80' if ew_state == 'green' else '#ef4444' if ew_state == 'red' else '#fbbf24'}; font-size: 1.4rem; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.3); line-height: 1.2;">
                    {ew_timer if ew_state != 'red' else 'STOP'}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Live Signal Button
    if st.button("🎯 View Live Signal", use_container_width=True, type="primary", key="view_signal_main"):
        show_live_signal_modal(ns_state, ew_state, ns_vehicles, ew_vehicles, ns_timer, ew_timer)
    
    st.markdown("---")
    
    # Vehicle Analytics Card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #334155); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #475569;">
        <h3 style="color: white; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            📊 Live Traffic Map
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Vehicle count chart
    render_vehicle_analytics()
    
    st.markdown("---")
    
    # AI Control Card  
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #334155); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #475569;">
        <h3 style="color: white; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            🤖 Autonomous Signal Control
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    render_ai_control_panel(ns_state, ew_state, ns_vehicles, ew_vehicles, ns_timer, ew_timer)
    
    st.markdown("---")
    
    # Emergency Feed Card
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e293b, #334155); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; border: 1px solid #475569;">
        <h3 style="color: white; margin: 0 0 1rem 0; display: flex; align-items: center; gap: 0.5rem;">
            🚨 Incident & Emergency Feed
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    render_emergency_feed()

def main():
    """Smart Traffic Management System - Modern Demo Interface"""
    
    # Initialize session state to prevent conflicts
    init_session_state()
    
    # Initialize session state for auto-refresh and data
    if 'last_update' not in st.session_state:
        st.session_state.last_update = time.time()
        st.session_state.current_cycle = 0
        st.session_state.ai_mode = True
        st.session_state.manual_override_active = False
        st.session_state.incident_count = 0
    
    # Auto-refresh every 30 seconds (only if enabled)
    current_time = time.time()
    auto_refresh_enabled = st.session_state.get('auto_refresh_enabled', True)
    if auto_refresh_enabled and current_time - st.session_state.last_update > 30:
        st.session_state.last_update = current_time
        st.session_state.current_cycle += 1
        st.rerun()
    
    # Navigation header
    st.markdown("""
    <div style="text-align: right; margin: 1rem 0;">
        <a class='back-button' href='/' style='text-decoration: none !important;'>
            <span class='back-arrow'>←</span> Back to Home
        </a>
    </div>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e40af, #3b82f6); border-radius: 12px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 2.2rem;">🚦 Smart Traffic Management System</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">Real-time Traffic Signal Optimization Based on Vehicle Density</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-refresh control panel
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        auto_refresh_enabled = st.session_state.get('auto_refresh_enabled', True)
        
        col_a, col_b, col_c = st.columns([1, 1, 1])
        with col_a:
            if st.button("▶️ Enable Auto-Refresh" if not auto_refresh_enabled else "⏸️ Pause Auto-Refresh", 
                        key="toggle_auto_refresh", use_container_width=True):
                st.session_state.auto_refresh_enabled = not auto_refresh_enabled
                st.rerun()
        
        with col_b:
            if st.button("🔄 Refresh Now", key="manual_refresh", use_container_width=True):
                st.session_state.last_update = time.time() - 31  # Force refresh
                st.rerun()
        
        with col_c:
            refresh_status = "🟢 LIVE" if auto_refresh_enabled else "🔴 PAUSED"
            st.markdown(f"<div style='text-align: center; padding: 0.5rem; color: white;'>{refresh_status}</div>", 
                       unsafe_allow_html=True)

    # Demo Information Panel
    with st.expander("ℹ️ About This Demo - Traffic Management System Features", expanded=False):
        st.markdown("""
        ### 🎯 **What This Demo Shows**
        
        **Real-Time Traffic Optimization:**
        - Live traffic signal timing based on vehicle density
        - Adaptive AI algorithms that adjust signal patterns
        - Emergency vehicle priority override system
        
        **Key Features Demonstrated:**
        
        🚦 **Live Signal Management**
        - Click "View Live Signal" to see real-time intersection status
        - Traffic lights cycle automatically every 60 seconds
        - Red/Yellow/Green states with countdown timers
        
        📊 **Vehicle Analytics**
        - Real-time vehicle type detection and counting
        - Dynamic charts showing Cars, Buses, Bikes, and Trucks
        - Data updates automatically with traffic patterns
        
        🤖 **AI Control System**
        - Toggle between AI Adaptive and Manual control modes
        - Manual override for emergency situations
        - Smart timing adjustments based on traffic flow
        
        🚨 **Emergency Response**
        - Incident detection and alerts
        - Emergency vehicle priority system
        - Traffic congestion management
        
        ### 🎮 **Interactive Controls**
        - **Auto-Refresh**: Control live data updates (top controls)
        - **AI Mode Toggle**: Switch between automated and manual control
        - **Manual Override**: Emergency control activation
        - **Live Signal View**: Real-time intersection visualization
        
        ### 📈 **How It Works**
        This system simulates a modern smart traffic management solution that uses:
        - Computer vision for vehicle detection
        - Machine learning for traffic pattern optimization
        - IoT sensors for real-time data collection
        - Cloud-based processing for instant decision making
        """)

    # Main Dashboard Cards Layout
    render_modern_dashboard()

    # Auto-refresh indicator with more detailed status
    auto_refresh_enabled = st.session_state.get('auto_refresh_enabled', True)
    current_time = time.time()
    last_update = st.session_state.get('last_update', current_time)
    seconds_since_update = int(current_time - last_update)
    next_refresh_in = max(0, 30 - seconds_since_update)
    
    status_text = f"🟢 LIVE - Next refresh in {next_refresh_in}s" if auto_refresh_enabled else "🔴 PAUSED - Auto-refresh disabled"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem; margin-top: 2rem; background: rgba(30, 41, 59, 0.3); border-radius: 8px; border: 1px solid #475569;">
        <div style="color: {'#4ade80' if auto_refresh_enabled else '#ef4444'}; font-weight: 600; margin-bottom: 0.5rem;">
            {status_text}
        </div>
        <div style="color: #64748b; font-size: 0.9rem;">
            Last update: {datetime.now().strftime("%H:%M:%S")} | Cycle: {st.session_state.current_cycle} | Mode: {'AI' if not st.session_state.get('manual_override_status', False) else 'Manual'}
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()