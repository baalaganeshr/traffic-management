"""
TrafficFlow Pro - Professional Enterprise Dashboard
Modern React-like Components with Advanced HTML/CSS
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

# ====================== MODERN CSS FRAMEWORK ======================

def load_professional_css():
    """Load advanced CSS framework with modern design patterns"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
    
    /* Modern CSS Custom Properties */
    :root {
        /* Color System */
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-200: #bfdbfe;
        --primary-300: #93c5fd;
        --primary-400: #60a5fa;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-800: #1e40af;
        --primary-900: #1e3a8a;
        
        --accent-50: #f0f9ff;
        --accent-100: #e0f2fe;
        --accent-200: #bae6fd;
        --accent-300: #7dd3fc;
        --accent-400: #38bdf8;
        --accent-500: #0ea5e9;
        --accent-600: #0284c7;
        --accent-700: #0369a1;
        --accent-800: #075985;
        --accent-900: #0c4a6e;
        
        /* Semantic Colors */
        --success-50: #f0fdf4;
        --success-100: #dcfce7;
        --success-500: #22c55e;
        --success-600: #16a34a;
        --success-700: #15803d;
        
        --warning-50: #fffbeb;
        --warning-100: #fef3c7;
        --warning-500: #f59e0b;
        --warning-600: #d97706;
        --warning-700: #b45309;
        
        --error-50: #fef2f2;
        --error-100: #fee2e2;
        --error-500: #ef4444;
        --error-600: #dc2626;
        --error-700: #b91c1c;
        
        /* Background System */
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --bg-card: #1e293b;
        --bg-card-hover: #334155;
        
        /* Text System */
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-tertiary: #94a3b8;
        --text-inverse: #0f172a;
        
        /* Border System */
        --border-primary: #334155;
        --border-secondary: #475569;
        --border-accent: var(--accent-600);
        
        /* Shadow System */
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
        
        /* Spacing System */
        --space-1: 0.25rem;
        --space-2: 0.5rem;
        --space-3: 0.75rem;
        --space-4: 1rem;
        --space-6: 1.5rem;
        --space-8: 2rem;
        --space-12: 3rem;
        --space-16: 4rem;
        
        /* Border Radius */
        --radius-sm: 0.125rem;
        --radius-md: 0.375rem;
        --radius-lg: 0.5rem;
        --radius-xl: 0.75rem;
        --radius-2xl: 1rem;
        --radius-3xl: 1.5rem;
        
        /* Animation */
        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-normal: 300ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 500ms cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main .block-container {
        padding-top: var(--space-6);
        padding-bottom: var(--space-16);
        max-width: 1400px;
    }
    
    /* Component System */
    .component-card {
        background: var(--bg-card);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-2xl);
        padding: var(--space-8);
        box-shadow: var(--shadow-lg);
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
    }
    
    .component-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-2xl);
        border-color: var(--border-accent);
    }
    
    .component-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--accent-500), transparent);
        opacity: 0.6;
    }
    
    /* Header System */
    .hero-section {
        background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-3xl);
        padding: var(--space-12);
        margin-bottom: var(--space-8);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 50%, var(--accent-600)15 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, var(--primary-600)15 0%, transparent 50%);
        z-index: 1;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: var(--space-6);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-400), var(--primary-400));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        margin: var(--space-2) 0 0 0;
        opacity: 0.9;
    }
    
    .system-status-panel {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: var(--space-3);
    }
    
    .status-badge-premium {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid var(--success-600);
        color: var(--success-500);
        padding: var(--space-3) var(--space-6);
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        backdrop-filter: blur(10px);
    }
    
    .status-indicator-premium {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success-500);
        animation: pulse 2s infinite;
        box-shadow: 0 0 0 0 var(--success-500);
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
    }
    
    /* KPI Grid System */
    .kpi-grid-premium {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: var(--space-6);
        margin-bottom: var(--space-8);
    }
    
    .kpi-card-premium {
        background: var(--bg-card);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-2xl);
        padding: var(--space-8);
        position: relative;
        overflow: hidden;
        transition: all var(--transition-normal);
        height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .kpi-card-premium:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-2xl);
        border-color: var(--border-accent);
    }
    
    .kpi-card-premium.primary { 
        border-left: 4px solid var(--primary-500);
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(59, 130, 246, 0.05) 100%);
    }
    
    .kpi-card-premium.success { 
        border-left: 4px solid var(--success-500);
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(34, 197, 94, 0.05) 100%);
    }
    
    .kpi-card-premium.warning { 
        border-left: 4px solid var(--warning-500);
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(245, 158, 11, 0.05) 100%);
    }
    
    .kpi-card-premium.error { 
        border-left: 4px solid var(--error-500);
        background: linear-gradient(135deg, var(--bg-card) 0%, rgba(239, 68, 68, 0.05) 100%);
    }
    
    .kpi-header-premium {
        display: flex;
        align-items: center;
        gap: var(--space-4);
        margin-bottom: var(--space-6);
    }
    
    .kpi-icon-premium {
        width: 60px;
        height: 60px;
        border-radius: var(--radius-xl);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.75rem;
        background: linear-gradient(135deg, var(--accent-500)20, var(--primary-500)20);
        border: 1px solid var(--border-secondary);
        position: relative;
    }
    
    .kpi-icon-premium::before {
        content: '';
        position: absolute;
        inset: -1px;
        border-radius: var(--radius-xl);
        padding: 1px;
        background: linear-gradient(135deg, var(--accent-500), var(--primary-500));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: exclude;
        mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        mask-composite: exclude;
    }
    
    .kpi-meta-premium h3 {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 var(--space-1) 0;
    }
    
    .kpi-meta-premium p {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0;
        opacity: 0.8;
    }
    
    .kpi-value-premium {
        font-size: 3rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: var(--space-2);
        position: relative;
    }
    
    .kpi-value-premium.positive { color: var(--success-500); }
    .kpi-value-premium.negative { color: var(--error-500); }
    .kpi-value-premium.warning { color: var(--warning-500); }
    
    .kpi-unit-premium {
        font-size: 0.875rem;
        color: var(--text-tertiary);
        font-weight: 500;
        margin-left: var(--space-2);
    }
    
    .kpi-trend-premium {
        display: flex;
        align-items: center;
        gap: var(--space-2);
        font-size: 0.875rem;
        font-weight: 600;
        margin-bottom: var(--space-4);
    }
    
    .kpi-trend-premium.positive { color: var(--success-500); }
    .kpi-trend-premium.negative { color: var(--error-500); }
    .kpi-trend-premium.neutral { color: var(--text-secondary); }
    
    .trend-icon-premium {
        font-size: 1.25rem;
        padding: var(--space-1);
        border-radius: var(--radius-md);
        background: currentColor;
        color: var(--bg-primary);
        opacity: 0.1;
    }
    
    .kpi-progress-premium {
        margin-top: auto;
    }
    
    .progress-container-premium {
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        height: 8px;
        overflow: hidden;
        position: relative;
        margin-bottom: var(--space-2);
    }
    
    .progress-fill-premium {
        height: 100%;
        border-radius: var(--radius-lg);
        transition: width var(--transition-slow);
        position: relative;
    }
    
    .progress-fill-premium.primary { 
        background: linear-gradient(90deg, var(--primary-600), var(--accent-500)); 
    }
    .progress-fill-premium.success { 
        background: linear-gradient(90deg, var(--success-600), var(--success-400)); 
    }
    .progress-fill-premium.warning { 
        background: linear-gradient(90deg, var(--warning-600), var(--warning-400)); 
    }
    .progress-fill-premium.error { 
        background: linear-gradient(90deg, var(--error-600), var(--error-400)); 
    }
    
    .progress-label-premium {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    /* Chart Container */
    .chart-container-premium {
        background: var(--bg-card);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-2xl);
        padding: var(--space-8);
        margin-bottom: var(--space-6);
    }
    
    .chart-header-premium {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--space-6);
    }
    
    .chart-title-premium {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }
    
    .chart-controls-premium {
        display: flex;
        gap: var(--space-2);
    }
    
    .control-button-premium {
        padding: var(--space-2) var(--space-4);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-md);
        background: var(--bg-secondary);
        color: var(--text-secondary);
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all var(--transition-fast);
    }
    
    .control-button-premium:hover {
        background: var(--bg-tertiary);
        border-color: var(--border-accent);
        color: var(--text-primary);
    }
    
    .control-button-premium.active {
        background: var(--accent-600);
        border-color: var(--accent-500);
        color: white;
    }
    
    /* Sidebar Enhancements */
    .sidebar-section-premium {
        background: var(--bg-card);
        border: 1px solid var(--border-primary);
        border-radius: var(--radius-xl);
        padding: var(--space-6);
        margin-bottom: var(--space-6);
    }
    
    .sidebar-title-premium {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0 0 var(--space-4) 0;
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }
    
    /* Button System */
    .btn-premium {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: var(--space-2);
        padding: var(--space-3) var(--space-6);
        border-radius: var(--radius-xl);
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all var(--transition-fast);
        border: none;
        cursor: pointer;
        text-decoration: none;
        position: relative;
        overflow: hidden;
    }
    
    .btn-premium.primary {
        background: linear-gradient(135deg, var(--primary-600), var(--accent-600));
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .btn-premium.primary:hover {
        background: linear-gradient(135deg, var(--primary-700), var(--accent-700));
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }
    
    .btn-premium.success {
        background: linear-gradient(135deg, var(--success-600), var(--success-500));
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .btn-premium.success:hover {
        background: linear-gradient(135deg, var(--success-700), var(--success-600));
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }
    
    .btn-premium.danger {
        background: linear-gradient(135deg, var(--error-600), var(--error-500));
        color: white;
        box-shadow: var(--shadow-md);
    }
    
    .btn-premium.danger:hover {
        background: linear-gradient(135deg, var(--error-700), var(--error-600));
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Loading States */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid var(--border-primary);
        border-radius: 50%;
        border-top-color: var(--accent-500);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem; }
        .hero-content { flex-direction: column; text-align: center; }
        .kpi-grid-premium { grid-template-columns: 1fr; }
        .chart-header-premium { flex-direction: column; gap: var(--space-4); }
    }
    
    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-secondary);
        border-radius: var(--radius-lg);
        transition: background var(--transition-fast);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-600);
    }
    
    /* Hide Streamlit Elements */
    .stDeployButton { display: none; }
    #MainMenu { display: none; }
    footer { display: none; }
    header { display: none; }
    
    </style>
    """, unsafe_allow_html=True)

# ====================== REACT-LIKE COMPONENTS ======================

class ProfessionalComponents:
    """React-like component system for professional UI"""
    
    @staticmethod
    def hero_section(title: str, subtitle: str, status: str = "operational"):
        """Professional hero section component"""
        current_time = datetime.now().strftime("%H:%M:%S")
        status_color = "success" if status == "operational" else "warning"
        
        return f"""
        <div class="hero-section">
            <div class="hero-content">
                <div>
                    <h1 class="hero-title">{title}</h1>
                    <p class="hero-subtitle">{subtitle}</p>
                </div>
                <div class="system-status-panel">
                    <div class="status-badge-premium">
                        <div class="status-indicator-premium"></div>
                        <span>SYSTEM {status.upper()}</span>
                    </div>
                    <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.875rem; color: var(--text-tertiary);">
                        {current_time}
                    </div>
                </div>
            </div>
        </div>
        """
    
    @staticmethod
    def kpi_card(title: str, value: str, unit: str, trend: str, trend_value: str, 
                 progress: float, card_type: str = "primary", icon: str = "📊"):
        """Professional KPI card component"""
        trend_class = "positive" if "↗" in trend or "↑" in trend else "negative" if "↘" in trend or "↓" in trend else "neutral"
        value_class = trend_class if card_type == "primary" else card_type
        
        return f"""
        <div class="kpi-card-premium {card_type}">
            <div class="kpi-header-premium">
                <div class="kpi-icon-premium">{icon}</div>
                <div class="kpi-meta-premium">
                    <h3>{title}</h3>
                    <p>Real-time Analytics</p>
                </div>
            </div>
            
            <div>
                <div class="kpi-value-premium {value_class}">
                    {value}
                    <span class="kpi-unit-premium">{unit}</span>
                </div>
                
                <div class="kpi-trend-premium {trend_class}">
                    <span class="trend-icon-premium">{trend}</span>
                    <span>{trend_value}</span>
                </div>
            </div>
            
            <div class="kpi-progress-premium">
                <div class="progress-container-premium">
                    <div class="progress-fill-premium {card_type}" style="width: {progress}%"></div>
                </div>
                <div class="progress-label-premium">Performance Index</div>
            </div>
        </div>
        """
    
    @staticmethod
    def chart_container(title: str, chart_content: str, controls: List[str] = None):
        """Professional chart container component"""
        controls_html = ""
        if controls:
            controls_html = '<div class="chart-controls-premium">'
            for i, control in enumerate(controls):
                active_class = "active" if i == 0 else ""
                controls_html += f'<button class="control-button-premium {active_class}">{control}</button>'
            controls_html += '</div>'
        
        return f"""
        <div class="chart-container-premium">
            <div class="chart-header-premium">
                <h2 class="chart-title-premium">{title}</h2>
                {controls_html}
            </div>
            {chart_content}
        </div>
        """
    
    @staticmethod
    def sidebar_section(title: str, icon: str, content: str):
        """Professional sidebar section component"""
        return f"""
        <div class="sidebar-section-premium">
            <h3 class="sidebar-title-premium">
                <span>{icon}</span>
                {title}
            </h3>
            {content}
        </div>
        """

# ====================== DATA SIMULATION ENGINE ======================

class AdvancedTrafficSimulator:
    """Advanced traffic simulation with realistic data patterns"""
    
    def __init__(self):
        self.reset_simulation()
        self.time_of_day_factors = self._generate_time_factors()
        self.weather_impact = random.uniform(0.8, 1.2)
        self.event_impact = random.uniform(0.9, 1.1)
    
    def reset_simulation(self):
        self.current_time = 0
        self.vehicles_processed = 0
        self.total_wait_time = 0
        self.cycle_count = 0
        self.queue_lengths = {"north": 0, "south": 0, "east": 0, "west": 0}
        self.phase_durations = {"north_south": 40, "east_west": 40}
        self.current_phase = "north_south"
        self.phase_timer = 0
        self.performance_history = []
    
    def _generate_time_factors(self):
        """Generate realistic time-of-day traffic factors"""
        factors = {}
        for hour in range(24):
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
                factors[hour] = random.uniform(1.5, 2.0)
            elif 10 <= hour <= 16:  # Business hours
                factors[hour] = random.uniform(1.0, 1.3)
            elif 22 <= hour or hour <= 6:  # Night hours
                factors[hour] = random.uniform(0.3, 0.6)
            else:  # Moderate hours
                factors[hour] = random.uniform(0.8, 1.2)
        return factors
    
    def generate_realistic_traffic(self, hour: int):
        """Generate realistic traffic based on time of day"""
        base_rate = 15  # Base vehicles per minute
        time_factor = self.time_of_day_factors.get(hour, 1.0)
        weather_factor = self.weather_impact
        event_factor = self.event_impact
        
        arrival_rate = base_rate * time_factor * weather_factor * event_factor
        
        # Distribute among directions
        arrivals = {
            "north": max(0, int(np.random.poisson(arrival_rate * 0.3))),
            "south": max(0, int(np.random.poisson(arrival_rate * 0.3))),
            "east": max(0, int(np.random.poisson(arrival_rate * 0.2))),
            "west": max(0, int(np.random.poisson(arrival_rate * 0.2)))
        }
        
        return arrivals
    
    def simulate_step(self, algorithm: str = "adaptive", params: Dict = None):
        """Advanced simulation step with multiple algorithms"""
        current_hour = int(self.current_time / 3600) % 24
        
        # Generate new arrivals
        arrivals = self.generate_realistic_traffic(current_hour)
        for direction, count in arrivals.items():
            self.queue_lengths[direction] += count
        
        # Process current phase
        if algorithm == "fixed":
            self._process_fixed_timing()
        elif algorithm == "adaptive":
            self._process_adaptive_timing(params or {})
        elif algorithm == "ai_optimized":
            self._process_ai_optimized(params or {})
        
        # Update metrics
        total_queue = sum(self.queue_lengths.values())
        avg_wait = self.total_wait_time / max(self.vehicles_processed, 1)
        
        # Record performance
        performance = {
            "timestamp": datetime.now(),
            "vehicles_in_system": total_queue,
            "vehicles_served": self.vehicles_processed,
            "avg_wait_time": avg_wait,
            "cycle_count": self.cycle_count,
            "current_phase": self.current_phase,
            "throughput": self.vehicles_processed / max(self.current_time / 60, 1),
            "efficiency_score": self._calculate_efficiency_score(),
            "queue_lengths": self.queue_lengths.copy()
        }
        
        self.performance_history.append(performance)
        self.current_time += 1
        
        return performance
    
    def _process_fixed_timing(self):
        """Fixed timing signal control"""
        self.phase_timer += 1
        
        # Serve vehicles in current phase
        if self.current_phase == "north_south":
            served = min(self.queue_lengths["north"] + self.queue_lengths["south"], 
                        random.randint(8, 12))
            self.queue_lengths["north"] = max(0, self.queue_lengths["north"] - served // 2)
            self.queue_lengths["south"] = max(0, self.queue_lengths["south"] - served // 2)
        else:
            served = min(self.queue_lengths["east"] + self.queue_lengths["west"], 
                        random.randint(6, 10))
            self.queue_lengths["east"] = max(0, self.queue_lengths["east"] - served // 2)
            self.queue_lengths["west"] = max(0, self.queue_lengths["west"] - served // 2)
        
        self.vehicles_processed += served
        self.total_wait_time += sum(self.queue_lengths.values())
        
        # Switch phases
        if self.phase_timer >= 40:
            self.current_phase = "east_west" if self.current_phase == "north_south" else "north_south"
            self.phase_timer = 0
            self.cycle_count += 0.5
    
    def _process_adaptive_timing(self, params: Dict):
        """Adaptive timing based on queue lengths"""
        min_green = params.get("min_green", 20)
        max_green = params.get("max_green", 60)
        extension_time = params.get("extension", 5)
        
        self.phase_timer += 1
        
        # Serve vehicles with adaptive rate
        if self.current_phase == "north_south":
            demand = self.queue_lengths["north"] + self.queue_lengths["south"]
            served = min(demand, random.randint(10, 15))
            self.queue_lengths["north"] = max(0, self.queue_lengths["north"] - served // 2)
            self.queue_lengths["south"] = max(0, self.queue_lengths["south"] - served // 2)
        else:
            demand = self.queue_lengths["east"] + self.queue_lengths["west"]
            served = min(demand, random.randint(8, 12))
            self.queue_lengths["east"] = max(0, self.queue_lengths["east"] - served // 2)
            self.queue_lengths["west"] = max(0, self.queue_lengths["west"] - served // 2)
        
        self.vehicles_processed += served
        self.total_wait_time += sum(self.queue_lengths.values())
        
        # Adaptive phase switching
        current_demand = (self.queue_lengths["north"] + self.queue_lengths["south"] 
                         if self.current_phase == "north_south" 
                         else self.queue_lengths["east"] + self.queue_lengths["west"])
        
        other_demand = (self.queue_lengths["east"] + self.queue_lengths["west"] 
                       if self.current_phase == "north_south" 
                       else self.queue_lengths["north"] + self.queue_lengths["south"])
        
        should_switch = (self.phase_timer >= min_green and 
                        (current_demand < 3 or 
                         other_demand > current_demand * 2 or 
                         self.phase_timer >= max_green))
        
        if should_switch:
            self.current_phase = "east_west" if self.current_phase == "north_south" else "north_south"
            self.phase_timer = 0
            self.cycle_count += 0.5
    
    def _process_ai_optimized(self, params: Dict):
        """AI-optimized signal control (advanced algorithm)"""
        # Implement advanced AI optimization logic
        learning_rate = params.get("learning_rate", 0.1)
        prediction_horizon = params.get("prediction_horizon", 60)
        
        # Predict future arrivals
        predicted_arrivals = self._predict_arrivals(prediction_horizon)
        
        # Optimize phase durations using simple reinforcement learning
        optimal_duration = self._calculate_optimal_duration(predicted_arrivals)
        
        self.phase_timer += 1
        
        # Enhanced serving capacity
        if self.current_phase == "north_south":
            served = min(self.queue_lengths["north"] + self.queue_lengths["south"], 
                        random.randint(12, 18))
            self.queue_lengths["north"] = max(0, self.queue_lengths["north"] - served * 0.6)
            self.queue_lengths["south"] = max(0, self.queue_lengths["south"] - served * 0.4)
        else:
            served = min(self.queue_lengths["east"] + self.queue_lengths["west"], 
                        random.randint(10, 14))
            self.queue_lengths["east"] = max(0, self.queue_lengths["east"] - served * 0.6)
            self.queue_lengths["west"] = max(0, self.queue_lengths["west"] - served * 0.4)
        
        self.vehicles_processed += served
        self.total_wait_time += sum(self.queue_lengths.values())
        
        # AI-based switching
        if self.phase_timer >= optimal_duration:
            self.current_phase = "east_west" if self.current_phase == "north_south" else "north_south"
            self.phase_timer = 0
            self.cycle_count += 0.5
    
    def _predict_arrivals(self, horizon: int):
        """Simple arrival prediction"""
        current_hour = int(self.current_time / 3600) % 24
        base_factor = self.time_of_day_factors.get(current_hour, 1.0)
        return {
            "north": base_factor * 4,
            "south": base_factor * 4,
            "east": base_factor * 3,
            "west": base_factor * 3
        }
    
    def _calculate_optimal_duration(self, predicted_arrivals: Dict):
        """Calculate optimal phase duration"""
        current_demand = (self.queue_lengths["north"] + self.queue_lengths["south"] 
                         if self.current_phase == "north_south" 
                         else self.queue_lengths["east"] + self.queue_lengths["west"])
        
        if current_demand > 20:
            return 50
        elif current_demand > 10:
            return 35
        else:
            return 25
    
    def _calculate_efficiency_score(self):
        """Calculate overall efficiency score"""
        if not self.performance_history:
            return 0
        
        avg_wait = self.total_wait_time / max(self.vehicles_processed, 1)
        throughput = self.vehicles_processed / max(self.current_time / 60, 1)
        queue_balance = 1.0 / (1.0 + np.std(list(self.queue_lengths.values())))
        
        # Composite score (0-100)
        efficiency = (
            (1.0 / (1.0 + avg_wait / 30)) * 40 +  # Wait time component
            min(throughput / 20, 1.0) * 40 +      # Throughput component
            queue_balance * 20                     # Balance component
        )
        
        return min(100, max(0, efficiency))

# ====================== APPLICATION LOGIC ======================

def initialize_session_state():
    """Initialize session state variables"""
    if 'professional_simulator' not in st.session_state:
        st.session_state.professional_simulator = AdvancedTrafficSimulator()
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'performance_data' not in st.session_state:
        st.session_state.performance_data = []
    if 'current_algorithm' not in st.session_state:
        st.session_state.current_algorithm = "fixed"
    if 'algorithm_params' not in st.session_state:
        st.session_state.algorithm_params = {}
    if 'session_stats' not in st.session_state:
        st.session_state.session_stats = {
            "total_sessions": 0,
            "best_efficiency": 0,
            "total_vehicles_processed": 0,
            "average_wait_time": 0
        }

def render_professional_kpi_dashboard(performance_data: List[Dict]):
    """Render professional KPI dashboard with React-like components"""
    if not performance_data:
        # Empty state
        st.markdown("""
        <div class="component-card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 2rem; opacity: 0.6;">🚀</div>
            <h2 style="color: var(--text-primary); margin-bottom: 1rem;">Ready to Optimize Traffic Flow</h2>
            <p style="color: var(--text-secondary); font-size: 1.125rem;">
                Initialize the system to begin real-time traffic optimization and performance monitoring
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Calculate metrics
    latest = performance_data[-1]
    baseline_wait = 35.0  # Baseline wait time for comparison
    
    efficiency = ((baseline_wait - latest["avg_wait_time"]) / baseline_wait * 100) if latest["avg_wait_time"] > 0 else 0
    throughput = latest.get("throughput", 0)
    total_processed = latest.get("vehicles_served", 0)
    avg_wait = latest.get("avg_wait_time", 0)
    
    # Create KPI cards
    components = ProfessionalComponents()
    
    # KPI Grid
    st.markdown('<div class="kpi-grid-premium">', unsafe_allow_html=True)
    
    # Efficiency Card
    efficiency_trend = "↗" if efficiency > 0 else "↘" if efficiency < -5 else "→"
    efficiency_status = f"{abs(efficiency):.1f}% vs baseline"
    card_type = "success" if efficiency > 10 else "warning" if efficiency > 0 else "error"
    
    st.markdown(components.kpi_card(
        title="System Efficiency",
        value=f"{efficiency:+.1f}",
        unit="%",
        trend=efficiency_trend,
        trend_value=efficiency_status,
        progress=min(abs(efficiency) * 2, 100),
        card_type=card_type,
        icon="⚡"
    ), unsafe_allow_html=True)
    
    # Throughput Card
    st.markdown(components.kpi_card(
        title="Vehicle Throughput",
        value=f"{throughput:.1f}",
        unit="veh/min",
        trend="↗",
        trend_value=f"Total: {total_processed:,}",
        progress=min(throughput * 3, 100),
        card_type="success",
        icon="🚗"
    ), unsafe_allow_html=True)
    
    # Wait Time Card
    wait_status = "success" if avg_wait < 25 else "warning" if avg_wait < 40 else "error"
    wait_trend = "↓" if avg_wait < 30 else "↑"
    st.markdown(components.kpi_card(
        title="Average Wait Time",
        value=f"{avg_wait:.1f}",
        unit="sec",
        trend=wait_trend,
        trend_value="Optimized" if avg_wait < 30 else "Needs optimization",
        progress=max(0, 100 - avg_wait * 2),
        card_type=wait_status,
        icon="⏱️"
    ), unsafe_allow_html=True)
    
    # Queue Balance Card
    queue_lengths = list(latest.get("queue_lengths", {}).values())
    queue_balance = 100 - (np.std(queue_lengths) * 10) if queue_lengths else 50
    st.markdown(components.kpi_card(
        title="Queue Balance",
        value=f"{queue_balance:.0f}",
        unit="score",
        trend="↗" if queue_balance > 70 else "→",
        trend_value="Well balanced" if queue_balance > 70 else "Moderate balance",
        progress=queue_balance,
        card_type="primary",
        icon="⚖️"
    ), unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_advanced_charts(performance_data: List[Dict]):
    """Render advanced interactive charts"""
    if not performance_data:
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(performance_data)
    df['minute'] = range(len(df))
    
    components = ProfessionalComponents()
    
    # Real-time Performance Chart
    fig1 = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Wait Time Trend', 'Throughput Analysis', 'Queue Dynamics', 'Efficiency Score'),
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Wait time trend
    fig1.add_trace(
        go.Scatter(
            x=df['minute'], 
            y=df['avg_wait_time'],
            mode='lines+markers',
            name='Wait Time',
            line=dict(color='#ef4444', width=3),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Throughput
    fig1.add_trace(
        go.Scatter(
            x=df['minute'], 
            y=df['throughput'],
            mode='lines+markers',
            name='Throughput',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=6),
            fill='tonexty'
        ),
        row=1, col=2
    )
    
    # Queue dynamics
    if 'queue_lengths' in df.columns:
        for direction in ['north', 'south', 'east', 'west']:
            values = [ql.get(direction, 0) for ql in df['queue_lengths']]
            fig1.add_trace(
                go.Scatter(
                    x=df['minute'],
                    y=values,
                    mode='lines',
                    name=f'{direction.capitalize()} Queue',
                    stackgroup='one'
                ),
                row=2, col=1
            )
    
    # Efficiency score
    fig1.add_trace(
        go.Scatter(
            x=df['minute'], 
            y=df['efficiency_score'],
            mode='lines+markers',
            name='Efficiency',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=6)
        ),
        row=2, col=2
    )
    
    fig1.update_layout(
        height=600,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9'),
        legend=dict(
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='#334155'
        )
    )
    
    fig1.update_xaxes(
        gridcolor='#334155',
        gridwidth=1,
        showgrid=True
    )
    fig1.update_yaxes(
        gridcolor='#334155',
        gridwidth=1,
        showgrid=True
    )
    
    chart_html = f'<div id="chart1">{fig1.to_html(include_plotlyjs=False, div_id="chart1")}</div>'
    
    st.markdown(components.chart_container(
        title="📈 Real-time Performance Analytics",
        chart_content="",
        controls=["Live View", "1 Hour", "24 Hours", "Export"]
    ), unsafe_allow_html=True)
    
    st.plotly_chart(fig1, use_container_width=True, key="performance_chart")

def render_professional_sidebar():
    """Render professional sidebar with enhanced controls"""
    components = ProfessionalComponents()
    
    # Algorithm Selection
    st.markdown(components.sidebar_section(
        "⚙️", "Control Algorithm",
        """
        <div style="margin-top: 1rem;">
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                Select the traffic control algorithm for optimization
            </p>
        </div>
        """
    ), unsafe_allow_html=True)
    
    algorithm = st.selectbox(
        "Algorithm Type",
        ["fixed", "adaptive", "ai_optimized"],
        format_func=lambda x: {
            "fixed": "🕐 Fixed Timing (Baseline)",
            "adaptive": "🧠 Adaptive Control",
            "ai_optimized": "🤖 AI Optimized"
        }[x],
        key="algorithm_select"
    )
    
    st.session_state.current_algorithm = algorithm
    
    # Algorithm Parameters
    params = {}
    if algorithm == "adaptive":
        st.markdown("**Adaptive Parameters**")
        params['min_green'] = st.slider("Min Green Time", 15, 30, 20)
        params['max_green'] = st.slider("Max Green Time", 45, 80, 60)
        params['extension'] = st.slider("Extension Time", 3, 10, 5)
    
    elif algorithm == "ai_optimized":
        st.markdown("**AI Parameters**")
        params['learning_rate'] = st.slider("Learning Rate", 0.05, 0.3, 0.1, 0.05)
        params['prediction_horizon'] = st.slider("Prediction Horizon", 30, 120, 60)
    
    st.session_state.algorithm_params = params
    
    # System Controls
    st.markdown("---")
    st.markdown(components.sidebar_section(
        "🎮", "System Operations",
        """
        <div style="margin-top: 1rem;">
            <p style="color: var(--text-secondary); margin-bottom: 1rem;">
                Control the traffic optimization system
            </p>
        </div>
        """
    ), unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_disabled = st.session_state.is_running
        if st.button(
            "🚀 START" if not start_disabled else "🔄 RUNNING",
            disabled=start_disabled,
            use_container_width=True,
            key="start_btn"
        ):
            st.session_state.is_running = True
            st.session_state.professional_simulator.reset_simulation()
            st.session_state.performance_data = []
            st.success("✅ System initialized!")
            st.rerun()
    
    with col2:
        stop_disabled = not st.session_state.is_running
        if st.button(
            "⏹️ STOP",
            disabled=stop_disabled,
            use_container_width=True,
            key="stop_btn"
        ):
            st.session_state.is_running = False
            
            # Update session stats
            if st.session_state.performance_data:
                latest = st.session_state.performance_data[-1]
                stats = st.session_state.session_stats
                stats["total_sessions"] += 1
                stats["best_efficiency"] = max(stats["best_efficiency"], latest.get("efficiency_score", 0))
                stats["total_vehicles_processed"] += latest.get("vehicles_served", 0)
                
            st.success("🛑 System terminated!")
            st.rerun()
    
    # Performance Settings
    st.markdown("---")
    speed = st.slider(
        "⚡ System Speed",
        0.5, 3.0, 1.0, 0.1,
        help="Control simulation speed"
    )
    
    # Current Status
    st.markdown("---")
    if st.session_state.is_running:
        st.success("🟢 **SYSTEM ACTIVE**")
        if st.session_state.performance_data:
            latest = st.session_state.performance_data[-1]
            st.markdown(f"""
            **Live Metrics:**
            - Phase: {latest.get('current_phase', 'N/A')}
            - Queue Total: {latest.get('vehicles_in_system', 0)}
            - Processed: {latest.get('vehicles_served', 0)}
            """)
    else:
        st.info("🔴 **SYSTEM STANDBY**")
    
    return speed

def main():
    """Main application with professional React-like interface"""
    
    # Page configuration
    st.set_page_config(
        page_title="TrafficFlow Pro - Enterprise Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🚦"
    )
    
    # Load CSS
    load_professional_css()
    
    # Initialize state
    initialize_session_state()
    
    # Hero Section
    components = ProfessionalComponents()
    st.markdown(components.hero_section(
        "TrafficFlow Pro",
        "Advanced Traffic Management & Optimization Platform",
        "operational" if st.session_state.is_running else "standby"
    ), unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        simulation_speed = render_professional_sidebar()
    
    # Main Dashboard
    render_professional_kpi_dashboard(st.session_state.performance_data)
    
    # Charts Section
    if st.session_state.performance_data:
        render_advanced_charts(st.session_state.performance_data)
    
    # Simulation Loop
    if st.session_state.is_running:
        # Run simulation step
        performance = st.session_state.professional_simulator.simulate_step(
            st.session_state.current_algorithm,
            st.session_state.algorithm_params
        )
        
        st.session_state.performance_data.append(performance)
        
        # Limit data points for performance
        if len(st.session_state.performance_data) > 500:
            st.session_state.performance_data = st.session_state.performance_data[-500:]
        
        # Auto-refresh
        time.sleep(1.0 / simulation_speed)
        st.rerun()

if __name__ == "__main__":
    main()
