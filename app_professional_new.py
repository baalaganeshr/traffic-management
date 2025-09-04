"""
UrbanFlow360 - Professional Traffic Management Dashboard
Enterprise-Grade UI/UX with Intuitive Navigation and Export Features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
import hashlib

# Page Configuration
st.set_page_config(
    page_title="UrbanFlow360 - Traffic Management",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/KishanBouri/urbanflow360',
        'Report a bug': "https://github.com/KishanBouri/urbanflow360/issues",
        'About': "UrbanFlow360 - Professional Traffic Management System"
    }
)

# Professional UI/UX Framework
def load_professional_styles():
    """Load modern professional CSS with better UX"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Roboto+Mono:wght@300;400;500;600&display=swap');
    
    :root {
        --primary: #1e40af;
        --primary-light: #3b82f6;
        --secondary: #10b981;
        --secondary-light: #34d399;
        --danger: #ef4444;
        --warning: #f59e0b;
        --success: #10b981;
        --info: #06b6d4;
        
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --bg-surface: #475569;
        
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        
        --border-color: #334155;
        --border-light: #475569;
        
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #0f172a 100%);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        padding: var(--space-6) var(--space-8);
        margin: -1rem -1rem var(--space-8) -1rem;
        border-radius: 0 0 var(--radius-xl) var(--radius-xl);
        box-shadow: var(--shadow-xl);
        text-align: center;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0 0 var(--space-2) 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-weight: 400;
    }
    
    .stSidebar > div {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-color);
    }
    
    .sidebar-section {
        background: var(--bg-tertiary);
        border-radius: var(--radius-lg);
        padding: var(--space-4);
        margin: var(--space-4) 0;
        border: 1px solid var(--border-color);
    }
    
    .sidebar-title {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: var(--space-3);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }
    
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--space-6);
        margin: var(--space-6) 0;
    }
    
    .kpi-card {
        background: linear-gradient(145deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary-light);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
    }
    
    .kpi-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--space-4);
    }
    
    .kpi-icon {
        width: 56px;
        height: 56px;
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .kpi-meta h3 {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 var(--space-1) 0;
    }
    
    .kpi-meta p {
        font-size: 0.875rem;
        color: var(--text-muted);
        margin: 0;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        font-family: 'Roboto Mono', monospace;
        margin: var(--space-2) 0;
        display: flex;
        align-items: baseline;
        gap: var(--space-2);
    }
    
    .kpi-unit {
        font-size: 1rem;
        color: var(--text-muted);
        font-weight: 500;
    }
    
    .kpi-trend {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: var(--space-4);
    }
    
    .trend-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    
    .status-success { color: var(--success); }
    .status-warning { color: var(--warning); }
    .status-danger { color: var(--danger); }
    .status-info { color: var(--info); }
    
    .bg-success { background: var(--success); }
    .bg-warning { background: var(--warning); }
    .bg-danger { background: var(--danger); }
    .bg-info { background: var(--info); }
    
    .progress-container {
        background: var(--bg-primary);
        height: 8px;
        border-radius: var(--radius-sm);
        overflow: hidden;
        position: relative;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: var(--radius-sm);
        transition: width 0.8s ease;
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
    }
    
    .progress-label {
        font-size: 0.75rem;
        color: var(--text-muted);
        margin-top: var(--space-1);
        text-align: center;
    }
    
    .control-panel {
        background: var(--bg-secondary);
        border-radius: var(--radius-lg);
        padding: var(--space-6);
        margin: var(--space-6) 0;
        border: 1px solid var(--border-color);
    }
    
    .btn-group {
        display: flex;
        gap: var(--space-3);
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .btn {
        padding: var(--space-3) var(--space-6);
        border-radius: var(--radius-md);
        font-weight: 500;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        cursor: pointer;
        border: 1px solid var(--border-color);
        background: var(--bg-tertiary);
        color: var(--text-primary);
        text-decoration: none;
    }
    
    .btn:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-light);
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        border-color: var(--primary);
    }
    
    .btn-success {
        background: linear-gradient(135deg, var(--success) 0%, var(--secondary-light) 100%);
        color: white;
        border-color: var(--success);
    }
    
    .chart-container {
        background: var(--bg-secondary);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-6) 0;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-lg);
    }
    
    .chart-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--space-6);
        padding-bottom: var(--space-4);
        border-bottom: 1px solid var(--border-color);
    }
    
    .chart-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .export-section {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin: var(--space-6) 0;
        border: 1px solid var(--border-color);
        text-align: center;
    }
    
    .export-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: var(--space-3);
    }
    
    .export-description {
        color: var(--text-muted);
        margin-bottom: var(--space-6);
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: var(--space-2);
        padding: var(--space-1) var(--space-3);
        border-radius: var(--radius-lg);
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-online {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .status-offline {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger);
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
    
    @media (max-width: 768px) {
        .kpi-grid {
            grid-template-columns: 1fr;
        }
        .main-title {
            font-size: 2rem;
        }
    }
    
    .fadeIn {
        animation: fadeIn 0.6s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """, unsafe_allow_html=True)

# Utility Functions
def generate_unique_key(prefix: str = "component") -> str:
    """Generate unique keys to prevent Streamlit conflicts"""
    timestamp = str(int(time.time() * 1000))
    random_str = str(random.randint(10000, 99999))
    unique_id = hashlib.md5(f"{prefix}_{timestamp}_{random_str}".encode()).hexdigest()[:8]
    return f"{prefix}_{unique_id}"

def create_professional_kpi_card(title: str, value: str, unit: str, 
                                trend_direction: str, trend_text: str, 
                                progress: float, status: str, icon_bg: str):
    """Create professional KPI cards with proper Streamlit components"""
    
    # Determine colors based on status
    if status == "success":
        value_color = "var(--success)"
        trend_color = "var(--success)"
        trend_dot_bg = "#10b981"
    elif status == "warning":
        value_color = "var(--warning)"
        trend_color = "var(--warning)"
        trend_dot_bg = "#f59e0b"
    elif status == "danger":
        value_color = "var(--danger)"
        trend_color = "var(--danger)"
        trend_dot_bg = "#ef4444"
    else:
        value_color = "var(--info)"
        trend_color = "var(--info)"
        trend_dot_bg = "#06b6d4"
    
    kpi_html = f"""
    <div class="kpi-card fadeIn">
        <div class="kpi-header">
            <div class="kpi-icon" style="background: {icon_bg};">
                {title[:2].upper()}
            </div>
            <div class="kpi-meta">
                <h3>{title}</h3>
                <p>Real-time Analytics</p>
            </div>
        </div>
        
        <div class="kpi-value" style="color: {value_color};">
            {value}
            <span class="kpi-unit">{unit}</span>
        </div>
        
        <div class="kpi-trend" style="color: {trend_color};">
            <span class="trend-dot" style="background: {trend_dot_bg};"></span>
            <span>{trend_text}</span>
        </div>
        
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%;"></div>
        </div>
        <div class="progress-label">Performance Index</div>
    </div>
    """
    
    return kpi_html

def create_download_section(data_dict: Dict[str, pd.DataFrame]):
    """Create professional download section with multiple export options"""
    st.markdown("""
    <div class="export-section">
        <h3 class="export-title">📊 Data Export Center</h3>
        <p class="export-description">Download your traffic analytics and simulation data in various formats</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if "simulation_data" in data_dict:
            csv_data = data_dict["simulation_data"].to_csv(index=False)
            st.download_button(
                label="📈 Simulation CSV",
                data=csv_data,
                file_name=f"traffic_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key=generate_unique_key("csv_download"),
                help="Download simulation data as CSV"
            )
    
    with col2:
        if "performance_metrics" in data_dict:
            json_data = json.dumps(data_dict["performance_metrics"], indent=2, default=str)
            st.download_button(
                label="📊 Metrics JSON",
                data=json_data,
                file_name=f"traffic_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key=generate_unique_key("json_download"),
                help="Download performance metrics as JSON"
            )
    
    with col3:
        # Create summary report
        summary_data = create_summary_report(data_dict)
        st.download_button(
            label="📋 Summary Report",
            data=summary_data,
            file_name=f"traffic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            key=generate_unique_key("report_download"),
            help="Download comprehensive traffic report"
        )
    
    with col4:
        # Excel download with multiple sheets
        excel_buffer = create_excel_export(data_dict)
        st.download_button(
            label="📊 Complete Excel",
            data=excel_buffer,
            file_name=f"urbanflow360_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key=generate_unique_key("excel_download"),
            help="Download all data as Excel workbook"
        )

def create_summary_report(data_dict: Dict) -> str:
    """Generate comprehensive text report"""
    report = f"""
URBANFLOW360 - TRAFFIC MANAGEMENT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===========================================

EXECUTIVE SUMMARY
-----------------
This report contains traffic simulation and performance analytics data
from the UrbanFlow360 professional traffic management system.

SIMULATION OVERVIEW
------------------
"""
    
    if "simulation_data" in data_dict:
        df = data_dict["simulation_data"]
        report += f"""
Total Simulation Points: {len(df)}
Time Period Analyzed: {len(df)} minutes
Average System Efficiency: {df['efficiency'].mean():.2f}%
Peak Throughput: {df['throughput'].max():.0f} vehicles/hr
Minimum Wait Time: {df['wait_time'].min():.1f} seconds
Maximum Wait Time: {df['wait_time'].max():.1f} seconds
"""
    
    report += f"""

PERFORMANCE METRICS
------------------
System Status: Operational
Analysis Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Data Export Tool: UrbanFlow360 Professional Dashboard

For technical support: https://github.com/KishanBouri/urbanflow360
Report generated by UrbanFlow360 v2.0
"""
    
    return report

def create_excel_export(data_dict: Dict) -> bytes:
    """Create comprehensive Excel export with multiple sheets"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Simulation data sheet
        if "simulation_data" in data_dict:
            data_dict["simulation_data"].to_excel(writer, sheet_name='Simulation_Data', index=False)
        
        # Performance summary sheet
        if "performance_metrics" in data_dict:
            metrics_df = pd.DataFrame([data_dict["performance_metrics"]])
            metrics_df.to_excel(writer, sheet_name='Performance_Metrics', index=False)
        
        # Create summary statistics sheet
        if "simulation_data" in data_dict:
            df = data_dict["simulation_data"]
            summary_stats = pd.DataFrame({
                'Metric': ['Mean Efficiency', 'Mean Throughput', 'Mean Wait Time', 'Total Data Points'],
                'Value': [
                    f"{df['efficiency'].mean():.2f}%",
                    f"{df['throughput'].mean():.0f} veh/hr",
                    f"{df['wait_time'].mean():.1f} sec",
                    len(df)
                ]
            })
            summary_stats.to_excel(writer, sheet_name='Summary_Statistics', index=False)
    
    output.seek(0)
    return output.getvalue()

# Professional Traffic Simulation Engine
class ProfessionalTrafficSimulator:
    """Advanced traffic simulation with realistic modeling"""
    
    def __init__(self):
        self.reset_simulation()
        self.algorithms = {
            "Fixed Timing": "fixed",
            "Adaptive Control": "adaptive", 
            "AI-Optimized": "ai_optimized"
        }
    
    def reset_simulation(self):
        """Reset simulation state"""
        self.current_time = 0
        self.total_vehicles = 0
        self.vehicles_processed = 0
        self.total_wait_time = 0
        self.queue_lengths = {"North": 0, "South": 0, "East": 0, "West": 0}
        self.phase = "NS"  # NS or EW
        self.phase_time = 0
        self.green_time = {"NS": 30, "EW": 25}
        self.performance_history = []
        
    def get_time_factor(self) -> float:
        """Get traffic intensity based on time of day"""
        hour = (self.current_time // 3600) % 24
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            return 1.8
        elif 10 <= hour <= 16:  # Business hours
            return 1.2
        elif 22 <= hour or hour <= 6:  # Night
            return 0.4
        else:
            return 1.0
    
    def simulate_arrivals(self) -> Dict[str, int]:
        """Simulate realistic vehicle arrivals"""
        base_rate = 12  # vehicles per minute per direction
        time_factor = self.get_time_factor()
        
        arrivals = {}
        for direction in self.queue_lengths.keys():
            rate = base_rate * time_factor * random.uniform(0.8, 1.2)
            arrivals[direction] = max(0, np.random.poisson(rate / 4))  # 15-second intervals
        
        return arrivals
    
    def process_traffic(self, algorithm: str = "adaptive"):
        """Process traffic based on selected algorithm"""
        # Add new arrivals
        arrivals = self.simulate_arrivals()
        for direction, count in arrivals.items():
            self.queue_lengths[direction] += count
            self.total_vehicles += count
        
        # Process current phase
        if algorithm == "fixed":
            self._process_fixed_timing()
        elif algorithm == "adaptive":
            self._process_adaptive_timing()
        else:  # AI optimized
            self._process_ai_timing()
        
        # Update metrics
        self._update_metrics()
        
    def _process_fixed_timing(self):
        """Fixed timing algorithm"""
        active_directions = ["North", "South"] if self.phase == "NS" else ["East", "West"]
        
        # Process vehicles in active directions
        for direction in active_directions:
            if self.queue_lengths[direction] > 0:
                processed = min(self.queue_lengths[direction], 8)  # 8 vehicles per cycle
                self.queue_lengths[direction] -= processed
                self.vehicles_processed += processed
                self.total_wait_time += processed * (self.queue_lengths[direction] * 2 + 10)
        
        # Switch phase
        self.phase_time += 15  # 15 seconds
        if self.phase_time >= self.green_time[self.phase]:
            self.phase = "EW" if self.phase == "NS" else "NS"
            self.phase_time = 0
    
    def _process_adaptive_timing(self):
        """Adaptive timing based on queue lengths"""
        active_directions = ["North", "South"] if self.phase == "NS" else ["East", "West"]
        inactive_directions = ["East", "West"] if self.phase == "NS" else ["North", "South"]
        
        # Adjust timing based on demand
        active_demand = sum(self.queue_lengths[d] for d in active_directions)
        inactive_demand = sum(self.queue_lengths[d] for d in inactive_directions)
        
        if active_demand > 0:
            processed_per_direction = min(active_demand // 2, 10)
            for direction in active_directions:
                if self.queue_lengths[direction] > 0:
                    processed = min(self.queue_lengths[direction], processed_per_direction)
                    self.queue_lengths[direction] -= processed
                    self.vehicles_processed += processed
                    self.total_wait_time += processed * (self.queue_lengths[direction] + 8)
        
        # Smart phase switching
        self.phase_time += 15
        min_green = 20
        max_green = 60
        
        if self.phase_time >= min_green:
            if inactive_demand > active_demand * 1.5 or self.phase_time >= max_green:
                self.phase = "EW" if self.phase == "NS" else "NS"
                self.phase_time = 0
    
    def _process_ai_timing(self):
        """AI-optimized timing with predictive capabilities"""
        all_queues = list(self.queue_lengths.values())
        total_demand = sum(all_queues)
        
        if total_demand == 0:
            return
        
        # AI prediction considers future arrivals and optimal processing
        time_factor = self.get_time_factor()
        predicted_arrivals = 12 * time_factor * 4  # Next minute prediction
        
        # Dynamic phase allocation
        ns_demand = self.queue_lengths["North"] + self.queue_lengths["South"]
        ew_demand = self.queue_lengths["East"] + self.queue_lengths["West"]
        
        if self.phase == "NS":
            if ns_demand > 0:
                throughput_rate = min(15, ns_demand // 2 + 5)  # Higher throughput
                for direction in ["North", "South"]:
                    if self.queue_lengths[direction] > 0:
                        processed = min(self.queue_lengths[direction], throughput_rate // 2)
                        self.queue_lengths[direction] -= processed
                        self.vehicles_processed += processed
                        self.total_wait_time += processed * (self.queue_lengths[direction] * 1.5 + 5)
        else:
            if ew_demand > 0:
                throughput_rate = min(15, ew_demand // 2 + 5)
                for direction in ["East", "West"]:
                    if self.queue_lengths[direction] > 0:
                        processed = min(self.queue_lengths[direction], throughput_rate // 2)
                        self.queue_lengths[direction] -= processed
                        self.vehicles_processed += processed
                        self.total_wait_time += processed * (self.queue_lengths[direction] * 1.5 + 5)
        
        # Predictive phase switching
        self.phase_time += 15
        optimal_switch_time = 25 + (predicted_arrivals / total_demand) * 10
        
        if self.phase_time >= optimal_switch_time:
            self.phase = "EW" if self.phase == "NS" else "NS"
            self.phase_time = 0
    
    def _update_metrics(self):
        """Update performance metrics"""
        self.current_time += 15  # 15-second intervals
        
        efficiency = max(0, 100 - (sum(self.queue_lengths.values()) * 2))
        throughput = (self.vehicles_processed * 240) if self.current_time > 0 else 0  # vehicles/hour
        avg_wait = self.total_wait_time / max(self.vehicles_processed, 1)
        
        metrics = {
            'timestamp': self.current_time,
            'efficiency': efficiency,
            'throughput': throughput,
            'wait_time': avg_wait,
            'queue_lengths': self.queue_lengths.copy(),
            'total_vehicles': self.total_vehicles,
            'processed_vehicles': self.vehicles_processed
        }
        
        self.performance_history.append(metrics)
        
        # Keep last 100 data points for memory efficiency
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)

def render_professional_dashboard():
    """Main dashboard rendering function"""
    load_professional_styles()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 class="main-title">🚦 UrbanFlow360</h1>
        <p class="main-subtitle">Professional Traffic Management & Analytics Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize simulator in session state
    if 'simulator' not in st.session_state:
        st.session_state.simulator = ProfessionalTrafficSimulator()
        st.session_state.is_running = False
    
    # Professional sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h3 class="sidebar-title">⚙️ Control Center</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Algorithm selection
        algorithm_name = st.selectbox(
            "Traffic Control Algorithm",
            options=list(st.session_state.simulator.algorithms.keys()),
            key="algorithm_selector",
            help="Select the traffic optimization algorithm"
        )
        
        algorithm = st.session_state.simulator.algorithms[algorithm_name]
        
        st.markdown("""
        <div class="sidebar-section">
            <h3 class="sidebar-title">🎮 System Operations</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Control buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ START", type="primary", use_container_width=True):
                st.session_state.is_running = True
                st.rerun()
        
        with col2:
            if st.button("⏹️ STOP", use_container_width=True):
                st.session_state.is_running = False
                st.rerun()
        
        if st.button("🔄 RESET", use_container_width=True):
            st.session_state.simulator.reset_simulation()
            st.session_state.is_running = False
            st.rerun()
        
        # System status
        st.markdown("""
        <div class="sidebar-section">
            <h3 class="sidebar-title">📊 System Status</h3>
        </div>
        """, unsafe_allow_html=True)
        
        status_class = "status-online" if st.session_state.is_running else "status-offline"
        status_text = "RUNNING" if st.session_state.is_running else "STOPPED"
        
        st.markdown(f"""
        <div class="status-indicator {status_class}">
            <span class="trend-dot"></span>
            {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        # Performance info
        if st.session_state.simulator.performance_history:
            latest = st.session_state.simulator.performance_history[-1]
            st.metric("Runtime", f"{latest['timestamp']//60:.0f} min")
            st.metric("Total Vehicles", f"{latest['total_vehicles']:,}")
    
    # Auto-run simulation
    if st.session_state.is_running:
        st.session_state.simulator.process_traffic(algorithm)
        time.sleep(0.1)  # Control speed
        st.rerun()
    
    # Main dashboard content
    if st.session_state.simulator.performance_history:
        latest_metrics = st.session_state.simulator.performance_history[-1]
        
        # KPI Cards
        st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            efficiency = latest_metrics['efficiency']
            status = "success" if efficiency > 80 else "warning" if efficiency > 60 else "danger"
            st.markdown(create_professional_kpi_card(
                title="System Efficiency",
                value=f"{efficiency:.0f}",
                unit="%",
                trend_direction="up" if efficiency > 70 else "down",
                trend_text="Optimal" if efficiency > 80 else "Moderate" if efficiency > 60 else "Critical",
                progress=efficiency,
                status=status,
                icon_bg="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            ), unsafe_allow_html=True)
        
        with col2:
            throughput = latest_metrics['throughput']
            status = "success" if throughput > 800 else "info"
            st.markdown(create_professional_kpi_card(
                title="Vehicle Throughput",
                value=f"{throughput:.0f}",
                unit="veh/hr",
                trend_direction="up",
                trend_text="Processing",
                progress=min(100, throughput / 10),
                status=status,
                icon_bg="linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            ), unsafe_allow_html=True)
        
        with col3:
            wait_time = latest_metrics['wait_time']
            status = "success" if wait_time < 20 else "warning" if wait_time < 40 else "danger"
            st.markdown(create_professional_kpi_card(
                title="Average Wait Time",
                value=f"{wait_time:.1f}",
                unit="sec",
                trend_direction="down" if wait_time < 30 else "up",
                trend_text="Optimized" if wait_time < 20 else "Normal" if wait_time < 40 else "High",
                progress=max(0, 100 - wait_time * 2),
                status=status,
                icon_bg="linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            ), unsafe_allow_html=True)
        
        with col4:
            queue_balance = 100 - np.std(list(latest_metrics['queue_lengths'].values())) * 5
            status = "success" if queue_balance > 70 else "info"
            st.markdown(create_professional_kpi_card(
                title="Queue Balance",
                value=f"{queue_balance:.0f}",
                unit="score",
                trend_direction="up" if queue_balance > 70 else "neutral",
                trend_text="Balanced" if queue_balance > 70 else "Moderate",
                progress=queue_balance,
                status=status,
                icon_bg="linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
            ), unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Charts section
        render_professional_charts(st.session_state.simulator.performance_history)
        
        # Data export section
        export_data = {
            "simulation_data": pd.DataFrame(st.session_state.simulator.performance_history),
            "performance_metrics": latest_metrics
        }
        create_download_section(export_data)
        
    else:
        # Welcome screen
        st.markdown("""
        <div class="control-panel">
            <h2 style="text-align: center; color: var(--text-primary);">🚀 Ready to Start Traffic Simulation</h2>
            <p style="text-align: center; color: var(--text-muted); margin-bottom: 2rem;">
                Select an algorithm from the sidebar and click START to begin real-time traffic analysis
            </p>
            <div class="btn-group">
                <div class="btn btn-primary">Professional Analytics</div>
                <div class="btn btn-success">Real-time Optimization</div>
                <div class="btn">Advanced Reporting</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_professional_charts(performance_data: List[Dict]):
    """Render professional interactive charts"""
    if len(performance_data) < 2:
        return
    
    df = pd.DataFrame(performance_data)
    df['minute'] = range(len(df))
    
    st.markdown("""
    <div class="chart-container">
        <div class="chart-header">
            <h3 class="chart-title">📈 Real-time Performance Analytics</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Performance overview chart
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('System Efficiency (%)', 'Vehicle Throughput (veh/hr)', 
                       'Wait Time Trend (sec)', 'Queue Distribution'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1,
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"type": "bar"}]]
    )
    
    # Efficiency trend
    fig.add_trace(
        go.Scatter(x=df['minute'], y=df['efficiency'], 
                  mode='lines+markers', name='Efficiency',
                  line=dict(color='#10b981', width=3),
                  marker=dict(size=6, color='#10b981')),
        row=1, col=1
    )
    
    # Throughput trend
    fig.add_trace(
        go.Scatter(x=df['minute'], y=df['throughput'],
                  mode='lines+markers', name='Throughput',
                  line=dict(color='#3b82f6', width=3),
                  marker=dict(size=6, color='#3b82f6')),
        row=1, col=2
    )
    
    # Wait time trend
    fig.add_trace(
        go.Scatter(x=df['minute'], y=df['wait_time'],
                  mode='lines+markers', name='Wait Time',
                  line=dict(color='#ef4444', width=3),
                  marker=dict(size=6, color='#ef4444')),
        row=2, col=1
    )
    
    # Queue distribution (latest)
    latest_queues = df.iloc[-1]['queue_lengths']
    if isinstance(latest_queues, dict):
        directions = list(latest_queues.keys())
        queue_values = list(latest_queues.values())
        
        fig.add_trace(
            go.Bar(x=directions, y=queue_values, name='Current Queues',
                  marker_color=['#667eea', '#764ba2', '#f093fb', '#f5576c']),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        height=600,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f8fafc', family='Inter'),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#cbd5e1')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)', color='#cbd5e1')
    
    st.plotly_chart(fig, use_container_width=True)

# Main Application
if __name__ == "__main__":
    render_professional_dashboard()
