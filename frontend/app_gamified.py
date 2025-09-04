# frontend/app_gamified.py
"""
UrbanFlow360 Gamified Dashboard (engine-wired)

Adds a typed, testable implementation that wires the Streamlit page to
SimulationEngine backends and the HybridController. Provides per-second
logging, KPI cards, charts, and session CSV export with XP/badges.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random
from typing import Optional, Any

# Engine/controller + session store
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.sim_api import SimulationEngine
from backend.sim_engines.sumo_toy import SumoToy
try:
    from backend.sim_engines.neat_adapter import NeatAdapter
except ImportError:
    NeatAdapter = None
from backend.controller_hybrid import HybridController, HybridParams
from analysis.session_store import SessionStore


# -------------------- Minimal engine orchestration (typed) --------------------

def _make_engine(engine_name: str, demand: str, seed: int) -> SimulationEngine:
    if engine_name == "NEAT":
        return NeatAdapter()  # type: ignore[return-value]
    # default toy engine
    return SumoToy(demand=demand, seed=seed)


def _ns_ew_queues(state: dict) -> tuple[int, int]:
    ns = int(state["approaches"]["North"]["q"]) + int(state["approaches"]["South"]["q"]) if "North" in state["approaches"] else 0
    ew = int(state["approaches"]["East"]["q"]) + int(state["approaches"]["West"]["q"]) if "East" in state["approaches"] else 0
    return ns, ew


def _since_last_arrival_for_phase(state: dict, cur_phase: int) -> float:
    # min last_arrival across active approaches as a simple proxy
    active = state["phases"][cur_phase]
    vals = [float(state["approaches"][a]["last_arrival"]) for a in active]
    return float(min(vals) if vals else 0.0)


def run_episode(
    engine: SimulationEngine,
    controller_mode: str,
    params: HybridParams,
    sim_duration_sec: int,
) -> tuple[list[dict], dict, dict]:
    """Run a single episode and return (rows, kpis, extras).

    rows: per-second log rows
    kpis: aggregated KPIs (avg_wait, throughput, total_queue)
    extras: extra counters like gap_outs
    """
    controller = HybridController(params)
    state = engine.reset()
    gap_outs = 0
    rows: list[dict] = []

    fixed_phase = 0
    t_in_phase = 0

    for _ in range(sim_duration_sec):
        if controller_mode == "Fixed 40s":
            # switch every 40s
            if t_in_phase >= 40:
                t_in_phase = 0
                if hasattr(engine, "switch_phase"):
                    try:
                        getattr(engine, "switch_phase")()
                    except Exception:
                        pass
                fixed_phase = 1 - fixed_phase
        else:
            # Adaptive: decide based on current state
            cur_phase = int(state["cur_phase"]) if "cur_phase" in state else 0
            t_in_phase = float(state.get("t_in_phase", 0.0))
            last_gap = _since_last_arrival_for_phase(state, cur_phase)
            dec_state = {
                "phases": state["phases"],
                "approaches": state["approaches"],
                "approaches_since_last_arrival": last_gap,
            }
            action, target = controller.decide(dec_state, cur_phase, t_in_phase)
            if action == "HOLD" and t_in_phase >= params.min_green and last_gap < params.gap:
                gap_outs += 1
            if action == "SWITCH" and target != cur_phase and hasattr(engine, "switch_phase"):
                try:
                    getattr(engine, "switch_phase")()
                except Exception:
                    pass

        # step 1s
        state = engine.step()
        t_in_phase = float(state.get("t_in_phase", t_in_phase + 1))
        ns_q, ew_q = _ns_ew_queues(state)
        served = state.get("served", {"North": 0, "South": 0, "East": 0, "West": 0})
        row = {
            "time": int(state.get("time", 0)),
            "phase": int(state.get("cur_phase", 0)),
            "ns_queue": ns_q,
            "ew_queue": ew_q,
            "ns_served": int(served.get("North", 0) + served.get("South", 0)),
            "ew_served": int(served.get("East", 0) + served.get("West", 0)),
        }
        rows.append(row)

    kpis = engine.metrics()
    extras = {"gap_outs": gap_outs}
    return rows, kpis, extras


def compute_improvement(curr: dict, baseline: Optional[dict]) -> float:
    if not baseline:
        return 0.0
    base_wait = float(baseline.get("avg_wait", 0.0))
    curr_wait = float(curr.get("avg_wait", 0.0))
    if base_wait <= 0:
        return 0.0
    return 100.0 * (base_wait - curr_wait) / base_wait


def award_badges(extras: dict, kpis: dict, params: HybridParams, improvement_pct: float) -> list[str]:
    badges: list[str] = []
    if extras.get("gap_outs", 0) >= 3:
        badges.append("Gap Master")
    # Fairness keeper: approximate by no approach max_wait over limit at episode end
    # This relies on engine state; if not available, skip
    try:
        # conservative: treat as keeper if avg_wait below threshold implied by max_wait
        if float(kpis.get("avg_wait", 0.0)) <= float(params.max_wait):
            badges.append("Fairness Keeper")
    except Exception:
        pass
    if improvement_pct >= 15.0:
        badges.append("Flow Guru")
    return badges

# ====================== ADVANCED STYLING & THEME ======================

def load_custom_css():
    """Load advanced custom CSS for professional enterprise-grade interface"""
    st.markdown("""
    <style>
    /* Import Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Roboto+Condensed:wght@400;500;700&display=swap');
    
    /* Advanced CSS Variables */
    :root {
        --primary-bg: linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 50%, #2a2f3e 100%);
        --card-bg: linear-gradient(135deg, rgba(26, 31, 46, 0.95) 0%, rgba(42, 47, 62, 0.85) 100%);
        --accent-primary: #00d4ff;
        --accent-secondary: #ff6b35;
        --accent-success: #00ff88;
        --accent-warning: #ffaa00;
        --accent-error: #ff4444;
        --accent-purple: #8b5cf6;
        --text-primary: #ffffff;
        --text-secondary: #b8bcc8;
        --text-tertiary: #8b8fa3;
        --border-color: rgba(255, 255, 255, 0.1);
        --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 20px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 8px 30px rgba(0, 0, 0, 0.2);
        --shadow-glow: 0 0 30px rgba(0, 212, 255, 0.2);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Global Styles */
    .stApp {
        background: var(--primary-bg);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-primary);
    }
    
    .main > div {
        padding: 1rem 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Professional Header */
    .enterprise-header {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .enterprise-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary), var(--accent-purple));
    }
    
    .header-title {
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 50%, var(--accent-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        line-height: 1.1;
    }
    
    .header-subtitle {
        font-size: 1.25rem;
        color: var(--text-secondary);
        text-align: center;
        font-weight: 400;
        max-width: 800px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    .status-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-active {
        background: linear-gradient(135deg, var(--accent-success), #00cc70);
        color: white;
        box-shadow: var(--shadow-glow);
    }
    
    .status-standby {
        background: linear-gradient(135deg, var(--text-tertiary), #6b7280);
        color: white;
    }
    
    /* Professional Cards */
    .pro-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 2rem;
        backdrop-filter: blur(15px);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    
    .pro-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-primary), transparent);
        opacity: 0;
        transition: var(--transition);
    }
    
    .pro-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--accent-primary);
    }
    
    .pro-card:hover::before {
        opacity: 1;
    }
    
    /* Advanced Metrics Cards */
    .metric-pro-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        text-align: center;
        position: relative;
        transition: var(--transition);
        backdrop-filter: blur(10px);
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-pro-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        opacity: 0.8;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--accent-primary);
        margin-bottom: 0.25rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    .metric-trend {
        font-size: 0.75rem;
        margin-top: 0.5rem;
        padding: 0.25rem 0.5rem;
        border-radius: var(--radius-sm);
        font-weight: 500;
    }
    
    .trend-positive {
        background: rgba(0, 255, 136, 0.1);
        color: var(--accent-success);
    }
    
    .trend-negative {
        background: rgba(255, 68, 68, 0.1);
        color: var(--accent-error);
    }
    
    /* Enhanced Gamification */
    .gamification-container {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(0, 212, 255, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: var(--radius-lg);
        padding: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .gamification-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.02)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.02)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.01)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
    }
    
    .level-badge-pro {
        background: linear-gradient(135deg, var(--accent-secondary), #ff8a50);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-md);
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
    }
    
    .xp-progress-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: var(--radius-md);
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .achievement-badge {
        background: linear-gradient(135deg, rgba(139, 92, 246, 0.8), rgba(0, 212, 255, 0.8));
        color: white;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        font-weight: 500;
        margin: 0.25rem;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(5px);
    }
    
    /* Professional Controls */
    .control-section {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-lg);
        padding: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .control-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .control-icon {
        width: 3rem;
        height: 3rem;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        border-radius: var(--radius-sm);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-primary), #0099cc);
        color: white;
        border: none;
        padding: 0.875rem 2rem;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 1rem;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, #00b8e6, #00a3cc);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:disabled {
        background: linear-gradient(135deg, #4a5568, #2d3748);
        color: var(--text-tertiary);
        cursor: not-allowed;
        transform: none;
    }
    
    /* Professional Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, rgba(10, 14, 26, 0.95) 0%, rgba(26, 31, 46, 0.95) 100%);
        border-right: 2px solid var(--border-color);
        backdrop-filter: blur(20px);
    }
    
    /* Advanced Data Tables */
    .stDataFrame {
        border: 1px solid var(--border-color);
        border-radius: var(--radius-md);
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    
    .stDataFrame [data-testid="stDataFrameContainer"] {
        background: var(--card-bg);
    }
    
    /* Traffic Light Animation */
    .traffic-light {
        width: 80px;
        height: 80px;
        background: var(--card-bg);
        border-radius: 50%;
        border: 3px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin: 1rem auto;
        position: relative;
        overflow: hidden;
    }
    
    .traffic-light.active {
        box-shadow: 0 0 30px var(--accent-success), 0 0 60px var(--accent-success);
        border-color: var(--accent-success);
        animation: pulse-green 2s infinite;
    }
    
    @keyframes pulse-green {
        0%, 100% { box-shadow: 0 0 20px var(--accent-success); }
        50% { box-shadow: 0 0 40px var(--accent-success), 0 0 60px var(--accent-success); }
    }
    
    /* Queue Direction Styling */
    .queue-direction-pro {
        background: var(--card-bg);
        border: 2px solid var(--border-color);
        border-radius: var(--radius-md);
        padding: 1rem;
        text-align: center;
        min-width: 100px;
        transition: var(--transition);
        position: relative;
    }
    
    .queue-direction-pro:hover {
        border-color: var(--accent-primary);
        transform: scale(1.05);
    }
    
    .queue-count-pro {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--accent-primary);
        font-family: 'JetBrains Mono', monospace;
    }
    
    .queue-label-pro {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.5rem;
    }
    
    /* Phase Indicator Enhancement */
    .phase-indicator-pro {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1.5rem;
        border-radius: var(--radius-md);
        font-weight: 600;
        font-size: 1rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        backdrop-filter: blur(5px);
    }
    
    .phase-ns-pro {
        background: linear-gradient(135deg, var(--accent-success), #00cc70);
        color: white;
    }
    
    .phase-ew-pro {
        background: linear-gradient(135deg, var(--accent-warning), #e69500);
        color: white;
    }
    
    /* Loading and Status Indicators */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .status-online {
        background: var(--accent-success);
        box-shadow: 0 0 10px var(--accent-success);
        animation: pulse-online 2s infinite;
    }
    
    .status-offline {
        background: var(--text-tertiary);
    }
    
    @keyframes pulse-online {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main > div {
            padding: 1rem;
        }
        
        .header-title {
            font-size: 2.5rem;
        }
        
        .pro-card {
            padding: 1.5rem;
        }
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-primary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-secondary);
    }
    
    /* Professional KPI Dashboard Styles */
    .kpi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .kpi-title-section h2.kpi-title {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .kpi-title-section .kpi-subtitle {
        font-size: 1.125rem;
        color: var(--text-secondary);
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    .status-badge {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: var(--success-bg);
        color: var(--success-text);
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: 2px solid var(--success-border);
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success-text);
        animation: pulse 2s infinite;
    }
    
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        border-color: var(--accent-primary);
    }
    
    .kpi-card.primary { border-left: 4px solid var(--accent-primary); }
    .kpi-card.success { border-left: 4px solid var(--success-border); }
    .kpi-card.warning { border-left: 4px solid var(--warning-border); }
    .kpi-card.info { border-left: 4px solid var(--info-border); }
    
    .kpi-card-header {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .kpi-icon {
        font-size: 2rem;
        width: 3rem;
        height: 3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--accent-primary)20, var(--accent-secondary)20);
        border: 1px solid var(--border-color);
    }
    
    .kpi-meta h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 0.25rem 0;
    }
    
    .kpi-meta p {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0;
        opacity: 0.8;
    }
    
    .kpi-value-section {
        margin-bottom: 1.5rem;
    }
    
    .kpi-main-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .kpi-main-value.positive { color: var(--success-text); }
    .kpi-main-value.negative { color: var(--error-text); }
    .kpi-main-value.neutral { color: var(--text-primary); }
    
    .kpi-unit {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .kpi-trend {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .kpi-trend.positive { color: var(--success-text); }
    .kpi-trend.negative { color: var(--error-text); }
    .kpi-trend.neutral { color: var(--text-secondary); }
    
    .kpi-progress {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .progress-bar {
        height: 6px;
        background: var(--bg-primary);
        border-radius: 3px;
        overflow: hidden;
        position: relative;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .progress-fill.primary { background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary)); }
    .progress-fill.success { background: linear-gradient(90deg, var(--success-border), #4ade80); }
    .progress-fill.warning { background: linear-gradient(90deg, var(--warning-border), #fbbf24); }
    .progress-fill.info { background: linear-gradient(90deg, var(--info-border), #60a5fa); }
    .progress-fill.positive { background: linear-gradient(90deg, var(--success-border), #4ade80); }
    .progress-fill.negative { background: linear-gradient(90deg, var(--error-border), #f87171); }
    .progress-fill.neutral { background: linear-gradient(90deg, var(--text-secondary), var(--text-tertiary)); }
    
    .progress-label {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.6;
    }
    
    .metrics-preview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .metric-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: var(--bg-primary);
        border: 1px dashed var(--border-color);
        border-radius: 12px;
        opacity: 0.6;
    }
    
    .metric-icon {
        font-size: 1.5rem;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .stat-item:last-child {
        border-bottom: none;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    .stat-value {
        font-size: 1rem;
        color: var(--text-primary);
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# ====================== GAME LOGIC & SIMULATION ======================

class TrafficSimulator:
    """
    Local traffic simulation engine without hardware dependency
    Simulates intersection with 4 directions (N/E/S/W) using queue theory
    """
    
    def __init__(self):
        self.current_phase = "NS"  # NS (North-South) or EW (East-West)
        self.phase_start_time = time.time()
        self.queues = {"N": 0, "E": 0, "S": 0, "W": 0}
        self.total_served = 0
        self.total_wait_time = 0
        self.cycle_count = 0
        self.vehicles_in_system = 0
        
    def generate_arrivals(self, time_of_day: float) -> Dict[str, int]:
        """Generate realistic vehicle arrivals based on time of day"""
        # Peak hours: 7-9 AM, 5-7 PM have higher arrival rates
        hour = int(time_of_day) % 24
        base_rate = 0.3
        
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Peak hours
            multiplier = 2.5
        elif 10 <= hour <= 16:  # Daytime
            multiplier = 1.5
        elif 22 <= hour or hour <= 6:  # Night
            multiplier = 0.5
        else:  # Off-peak
            multiplier = 1.0
            
        arrivals = {}
        for direction in ["N", "E", "S", "W"]:
            # Poisson arrivals with direction-specific bias
            rate = base_rate * multiplier
            if direction in ["N", "S"]:  # Main corridor bias
                rate *= 1.2
            arrivals[direction] = np.random.poisson(rate)
            
        return arrivals
    
    def serve_vehicles(self, green_time: float, direction_group: str) -> int:
        """Serve vehicles during green phase"""
        service_rate = 0.5  # vehicles per second capacity
        max_served = int(green_time * service_rate)
        
        if direction_group == "NS":
            available_n = self.queues["N"]
            available_s = self.queues["S"]
            served_n = min(available_n, max_served // 2)
            served_s = min(available_s, max_served - served_n)
            self.queues["N"] -= served_n
            self.queues["S"] -= served_s
            total_served = served_n + served_s
        else:  # EW
            available_e = self.queues["E"]
            available_w = self.queues["W"]
            served_e = min(available_e, max_served // 2)
            served_w = min(available_w, max_served - served_e)
            self.queues["E"] -= served_e
            self.queues["W"] -= served_w
            total_served = served_e + served_w
            
        return total_served
    
    def calculate_wait_time(self) -> float:
        """Calculate average wait time based on current queues"""
        if self.vehicles_in_system == 0:
            return 0.0
        
        total_queue = sum(self.queues.values())
        if total_queue == 0:
            return 0.0
            
        # Simple wait time estimation: queue_length / service_rate
        avg_wait = total_queue / 0.5  # 0.5 vehicles/second service rate
        return min(avg_wait, 120)  # Cap at 2 minutes
    
    def step_simulation(self, mode: str, params: Dict, time_of_day: float) -> Dict:
        """Single simulation step - core traffic logic"""
        current_time = time.time()
        
        # Generate new arrivals
        arrivals = self.generate_arrivals(time_of_day)
        for direction, count in arrivals.items():
            self.queues[direction] += count
            
        self.vehicles_in_system = sum(self.queues.values())
        
        # Traffic signal control logic
        if mode == "Fixed 40s":
            # Traditional fixed-time control
            phase_duration = 40.0
            if current_time - self.phase_start_time >= phase_duration:
                # Switch phase
                served = self.serve_vehicles(phase_duration, self.current_phase)
                self.total_served += served
                self.current_phase = "EW" if self.current_phase == "NS" else "NS"
                self.phase_start_time = current_time
                self.cycle_count += 0.5
        
        else:  # Adaptive mode
            min_green = params.get("min_green", 15)
            max_green = params.get("max_green", 60)
            gap_time = params.get("gap_time", 3)
            max_wait = params.get("max_wait", 90)
            
            phase_elapsed = current_time - self.phase_start_time
            
            # Gap-out logic: extend green if vehicles keep arriving
            current_directions = ["N", "S"] if self.current_phase == "NS" else ["E", "W"]
            opposing_directions = ["E", "W"] if self.current_phase == "NS" else ["N", "S"]
            
            current_demand = sum(self.queues[d] for d in current_directions)
            opposing_demand = sum(self.queues[d] for d in opposing_directions)
            
            should_switch = False
            
            # Check switching conditions
            if phase_elapsed >= max_green:
                should_switch = True
            elif phase_elapsed >= min_green:
                # Gap-out: switch if no recent arrivals or high opposing demand
                if current_demand == 0 or opposing_demand > current_demand * 2:
                    should_switch = True
                # Max-wait: switch if opposing directions waiting too long
                if opposing_demand > 0 and phase_elapsed > max_wait * 0.6:
                    should_switch = True
                    
            if should_switch:
                served = self.serve_vehicles(phase_elapsed, self.current_phase)
                self.total_served += served
                self.current_phase = "EW" if self.current_phase == "NS" else "NS"
                self.phase_start_time = current_time
                self.cycle_count += 0.5
        
        # Serve vehicles during current green phase
        ongoing_served = self.serve_vehicles(1.0, self.current_phase)  # 1 second service
        self.total_served += ongoing_served
        
        # Calculate metrics
        avg_wait = self.calculate_wait_time()
        self.total_wait_time += avg_wait
        
        # Return simulation state
        return {
            "timestamp": datetime.now(),
            "current_phase": self.current_phase,
            "queues": self.queues.copy(),
            "vehicles_served": ongoing_served,
            "total_served": self.total_served,
            "avg_wait_time": avg_wait,
            "vehicles_in_system": self.vehicles_in_system,
            "cycle_count": self.cycle_count
        }

class GameificationEngine:
    """
    XP/Level/Badge system for traffic optimization performance
    Rewards efficiency improvements and optimization skills
    """
    
    def __init__(self):
        self.xp = 0
        self.level = 1
        self.badges = []
        self.session_stats = {
            "total_runs": 0,
            "best_efficiency": 0,
            "total_vehicles_served": 0,
            "best_wait_time": float('inf')
        }
    
    def calculate_efficiency_score(self, adaptive_metrics: Dict, fixed_metrics: Dict) -> float:
        """Calculate efficiency improvement vs fixed timing"""
        if not fixed_metrics:
            return 0.0
            
        wait_improvement = max(0, (fixed_metrics.get("avg_wait", 0) - adaptive_metrics.get("avg_wait", 0)) / 
                             max(fixed_metrics.get("avg_wait", 1), 1))
        throughput_improvement = max(0, (adaptive_metrics.get("throughput", 0) - fixed_metrics.get("throughput", 0)) / 
                                   max(fixed_metrics.get("throughput", 1), 1))
        
        efficiency = (wait_improvement * 0.6 + throughput_improvement * 0.4) * 100
        return min(efficiency, 100)  # Cap at 100%
    
    def award_xp(self, efficiency_score: float, vehicles_served: int):
        """Award XP based on performance"""
        base_xp = 10
        efficiency_bonus = int(efficiency_score * 2)  # Up to 200 XP for 100% efficiency
        volume_bonus = min(vehicles_served // 10, 50)  # Volume handling bonus
        
        earned_xp = base_xp + efficiency_bonus + volume_bonus
        self.xp += earned_xp
        
        # Level up logic
        new_level = min(10, 1 + self.xp // 1000)  # Level up every 1000 XP, max level 10
        if new_level > self.level:
            self.level = new_level
            return True, earned_xp  # Level up occurred
        
        return False, earned_xp
    
    def check_badges(self, efficiency_score: float, avg_wait: float, vehicles_served: int):
        """Check and award badges based on achievements"""
        new_badges = []
        
        # Efficiency badges
        if efficiency_score >= 50 and "Efficiency Expert" not in self.badges:
            new_badges.append("🎯 Efficiency Expert")
            self.badges.append("Efficiency Expert")
            
        if efficiency_score >= 80 and "Optimization Master" not in self.badges:
            new_badges.append("🚀 Optimization Master")
            self.badges.append("Optimization Master")
        
        # Wait time badges
        if avg_wait < 10 and "Speed Demon" not in self.badges:
            new_badges.append("⚡ Speed Demon")
            self.badges.append("Speed Demon")
            
        # Volume badges
        if vehicles_served > 500 and "Traffic Maestro" not in self.badges:
            new_badges.append("🎼 Traffic Maestro")
            self.badges.append("Traffic Maestro")
            
        if vehicles_served > 1000 and "Flow Champion" not in self.badges:
            new_badges.append("🏆 Flow Champion")
            self.badges.append("Flow Champion")
        
        return new_badges

# ====================== STREAMLIT UI & DASHBOARD ======================

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "simulator" not in st.session_state:
        st.session_state.simulator = TrafficSimulator()
    
    if "game_engine" not in st.session_state:
        st.session_state.game_engine = GameificationEngine()
    
    if "simulation_log" not in st.session_state:
        st.session_state.simulation_log = []
    
    if "is_running" not in st.session_state:
        st.session_state.is_running = False
    
    if "session_history" not in st.session_state:
        st.session_state.session_history = []
    
    if "current_metrics" not in st.session_state:
        st.session_state.current_metrics = {}
    
    if "fixed_baseline" not in st.session_state:
        st.session_state.fixed_baseline = {}

def render_professional_header():
    """Render professional enterprise header with real-time status"""
    current_time = datetime.now().strftime("%H:%M:%S")
    status = "ACTIVE" if st.session_state.is_running else "STANDBY"
    status_class = "status-active" if st.session_state.is_running else "status-standby"
    
    st.markdown(f"""
    <div class="enterprise-header">
        <div class="status-badge {status_class}">
            <span class="status-indicator {'status-online' if st.session_state.is_running else 'status-offline'}"></span>
            SYSTEM {status}
        </div>
        <h1 class="header-title">🚦 TrafficFlow Pro</h1>
        <p class="header-subtitle">
            Enterprise Traffic Signal Optimization Platform<br>
            <small>Advanced AI-Powered Traffic Management • Real-time Analytics • Performance Gamification</small>
        </p>
        <div style="text-align: center; margin-top: 1.5rem; color: var(--text-tertiary); font-size: 0.875rem;">
            System Time: {current_time} | Version 2.0.0 | Build: Professional
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_gamification_panel():
    """Render enhanced XP/Level/Badge panel with professional styling"""
    game = st.session_state.game_engine
    
    # Level and XP Section
    st.markdown('<div class="xp-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="level-badge">� Level {game.level} Operator</div>', unsafe_allow_html=True)
    
    progress = (game.xp % 1000) / 1000
    st.markdown("**Experience Points**")
    st.progress(progress, text=f"{game.xp} XP ({int(progress * 100)}% to Level {game.level + 1})")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{game.session_stats["total_runs"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Sessions Completed</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        efficiency = game.session_stats.get('best_efficiency', 0)
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{efficiency:.1f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Best Efficiency</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Badges Section
    if game.badges:
        st.markdown("**🏆 Achievement Badges**")
        badge_html = ""
        for badge in game.badges[-6:]:  # Show last 6 badges
            badge_html += f'<span class="badge-item">{badge}</span>'
        st.markdown(badge_html, unsafe_allow_html=True)
    else:
        st.info("Complete simulations to earn achievement badges!")

def render_enhanced_control_panel():
    """Render enhanced control panel with better UX"""
    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    st.markdown("### 🎛️ **Traffic Signal Control System**")
    
    # Mode Selection with description
    mode_options = ["Fixed 40s", "Adaptive"]
    mode_descriptions = {
        "Fixed 40s": "Traditional timer-based control with fixed 40-second cycles",
        "Adaptive": "AI-powered optimization using real-time traffic data"
    }
    
    mode = st.selectbox(
        "Control Algorithm",
        mode_options,
        help="Choose between traditional fixed timing or intelligent adaptive control"
    )
    
    st.info(f"ℹ️ {mode_descriptions[mode]}")
    
    # Adaptive Parameters
    params = {}
    if mode == "Adaptive":
        st.markdown("---")
        st.markdown("**⚙️ Algorithm Parameters**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            params["min_green"] = st.slider(
                "Minimum Green Time", 10, 30, 15,
                help="Shortest green phase duration (seconds)"
            )
            params["gap_time"] = st.slider(
                "Gap Detection Time", 2, 8, 3,
                help="Time gap required to trigger phase change (seconds)"
            )
        
        with col2:
            params["max_green"] = st.slider(
                "Maximum Green Time", 40, 120, 60,
                help="Longest green phase duration (seconds)"
            )
            params["max_wait"] = st.slider(
                "Maximum Wait Time", 60, 180, 90,
                help="Maximum wait time before forced phase change (seconds)"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    return mode, params

def render_enhanced_kpi_dashboard(metrics: Dict, baseline: Dict):
    """Professional KPI dashboard with enterprise-grade styling and advanced analytics"""
    
    st.markdown("""
    <div class="kpi-header">
        <div class="kpi-title-section">
            <h2 class="kpi-title">📊 Performance Analytics Center</h2>
            <p class="kpi-subtitle">Real-time Traffic Optimization Metrics & System Intelligence</p>
        </div>
        <div class="kpi-status-section">
            <div class="status-badge active">
                <span class="status-dot"></span>
                <span>SYSTEM OPERATIONAL</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not metrics:
        # Professional empty state
        st.markdown("""
        <div class="pro-card empty-state">
            <div class="empty-state-content">
                <div class="empty-state-icon">📋</div>
                <h3 style="color: var(--text-primary); margin: 1rem 0;">Awaiting System Initialization</h3>
                <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
                    Initialize the traffic optimization system to begin collecting performance metrics and analytics data.
                </p>
                <div class="metrics-preview">
                    <div class="metric-placeholder">
                        <span class="metric-icon">⚡</span>
                        <span>Efficiency Score</span>
                    </div>
                    <div class="metric-placeholder">
                        <span class="metric-icon">🚗</span>
                        <span>Throughput Analysis</span>
                    </div>
                    <div class="metric-placeholder">
                        <span class="metric-icon">⏱️</span>
                        <span>Wait Time Optimization</span>
                    </div>
                    <div class="metric-placeholder">
                        <span class="metric-icon">🔄</span>
                        <span>Cycle Performance</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Calculate advanced metrics
    efficiency = 0
    efficiency_change = 0
    efficiency_status = "neutral"
    
    if baseline:
        efficiency = (baseline["avg_wait_time"] - metrics["avg_wait_time"]) / baseline["avg_wait_time"] * 100
        efficiency_change = abs(efficiency)
        efficiency_status = "positive" if efficiency > 0 else "negative" if efficiency < -2 else "neutral"
    
    throughput_rate = metrics["total_served"] / max(metrics["runtime"], 1) * 60
    cycle_efficiency = (metrics["total_served"] / max(metrics["cycle_count"], 1)) if metrics.get("cycle_count", 0) > 0 else 0
    
    # Professional KPI Cards Grid
    st.markdown("""
    <div class="kpi-grid">
        <div class="kpi-card primary">
            <div class="kpi-card-header">
                <div class="kpi-icon">⚡</div>
                <div class="kpi-meta">
                    <h3>System Efficiency</h3>
                    <p>vs. Baseline Performance</p>
                </div>
            </div>
            <div class="kpi-value-section">
                <div class="kpi-main-value {}">{:+.1f}%</div>
                <div class="kpi-trend {}">
                    <span class="trend-icon">{}</span>
                    <span>Optimization Impact</span>
                </div>
            </div>
            <div class="kpi-progress">
                <div class="progress-bar">
                    <div class="progress-fill {}" style="width: {}%"></div>
                </div>
                <span class="progress-label">Performance Grade</span>
            </div>
        </div>
        
        <div class="kpi-card success">
            <div class="kpi-card-header">
                <div class="kpi-icon">🚗</div>
                <div class="kpi-meta">
                    <h3>Vehicle Throughput</h3>
                    <p>Real-time Processing Rate</p>
                </div>
            </div>
            <div class="kpi-value-section">
                <div class="kpi-main-value">{:.1f}</div>
                <div class="kpi-unit">vehicles/min</div>
                <div class="kpi-trend positive">
                    <span class="trend-icon">↗</span>
                    <span>Total Served: {:,}</span>
                </div>
            </div>
            <div class="kpi-progress">
                <div class="progress-bar">
                    <div class="progress-fill success" style="width: {}%"></div>
                </div>
                <span class="progress-label">Capacity Utilization</span>
            </div>
        </div>
        
        <div class="kpi-card warning">
            <div class="kpi-card-header">
                <div class="kpi-icon">⏱️</div>
                <div class="kpi-meta">
                    <h3>Average Wait Time</h3>
                    <p>Queue Management Efficiency</p>
                </div>
            </div>
            <div class="kpi-value-section">
                <div class="kpi-main-value">{:.1f}s</div>
                <div class="kpi-trend {}">
                    <span class="trend-icon">{}</span>
                    <span>{}</span>
                </div>
            </div>
            <div class="kpi-progress">
                <div class="progress-bar">
                    <div class="progress-fill warning" style="width: {}%"></div>
                </div>
                <span class="progress-label">Wait Time Index</span>
            </div>
        </div>
        
        <div class="kpi-card info">
            <div class="kpi-card-header">
                <div class="kpi-icon">�</div>
                <div class="kpi-meta">
                    <h3>Cycle Performance</h3>
                    <p>Signal Optimization Index</p>
                </div>
            </div>
            <div class="kpi-value-section">
                <div class="kpi-main-value">{:.1f}</div>
                <div class="kpi-unit">veh/cycle</div>
                <div class="kpi-trend positive">
                    <span class="trend-icon">🎯</span>
                    <span>Cycles: {}</span>
                </div>
            </div>
            <div class="kpi-progress">
                <div class="progress-bar">
                    <div class="progress-fill info" style="width: {}%"></div>
                </div>
                <span class="progress-label">Operational Efficiency</span>
            </div>
        </div>
    </div>
    """.format(
        efficiency_status,
        efficiency,
        efficiency_status,
        "↗" if efficiency_status == "positive" else "↘" if efficiency_status == "negative" else "→",
        min(abs(efficiency) * 2, 100),
        efficiency_status,
        throughput_rate,
        int(metrics["total_served"]),
        min(throughput_rate * 2, 100),
        "positive" if metrics["avg_wait_time"] < 30 else "negative",
        "↓" if metrics["avg_wait_time"] < 30 else "↑",
        "Optimized" if metrics["avg_wait_time"] < 30 else "Needs Optimization",
        max(0, 100 - metrics["avg_wait_time"] * 2),
        cycle_efficiency,
        metrics.get("cycle_count", 0),
        min(cycle_efficiency * 10, 100)
    ), unsafe_allow_html=True)
    
    # Professional system insights
    st.markdown("---")
    
    # Advanced Analytics Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="pro-card">
            <h3 style="color: var(--accent-primary); margin-bottom: 1.5rem;">
                🧠 AI Performance Analysis
            </h3>
        """, unsafe_allow_html=True)
        
        # Performance insights
        insights = []
        if efficiency > 10:
            insights.append("🎯 **Excellent Optimization**: System is performing significantly better than baseline")
        elif efficiency > 5:
            insights.append("✅ **Good Performance**: Notable improvement in traffic flow efficiency")
        elif efficiency > 0:
            insights.append("📈 **Modest Gains**: Slight improvement detected in system performance")
        elif efficiency < -10:
            insights.append("⚠️ **Performance Alert**: Current configuration shows reduced efficiency")
        else:
            insights.append("📊 **Baseline Performance**: System operating within expected parameters")
            
        if throughput_rate > 20:
            insights.append("🚀 **High Throughput**: Excellent vehicle processing rate achieved")
        elif throughput_rate > 15:
            insights.append("💨 **Strong Flow**: Good vehicle processing capacity")
        else:
            insights.append("🔧 **Optimization Opportunity**: Consider parameter adjustments for higher throughput")
            
        if metrics["avg_wait_time"] < 20:
            insights.append("⚡ **Low Latency**: Exceptional wait time minimization")
        elif metrics["avg_wait_time"] < 35:
            insights.append("⏳ **Moderate Wait Times**: Acceptable performance levels")
        else:
            insights.append("🔄 **Queue Management**: Focus on reducing average wait times")
        
        for insight in insights:
            st.markdown(f"- {insight}")
            
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pro-card">
            <h3 style="color: var(--accent-primary); margin-bottom: 1.5rem;">
                📈 Quick Stats
            </h3>
        """, unsafe_allow_html=True)
        
        # Professional metrics display
        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-label">System Runtime</div>
                <div class="stat-value">{metrics['runtime']:.1f}s</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Processing Rate</div>
                <div class="stat-value">{throughput_rate:.1f}/min</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Cycle Efficiency</div>
                <div class="stat-value">{cycle_efficiency:.1f} v/c</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Performance Index</div>
                <div class="stat-value">{efficiency:+.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_live_queue_visualization():
    """Render real-time queue visualization"""
    if not st.session_state.simulation_log:
        return
    
    latest_data = st.session_state.simulation_log[-1]
    queues = latest_data["queues"]
    current_phase = latest_data["current_phase"]
    
    st.markdown("### 🚦 **Live Intersection View**")
    
    # Phase indicator
    phase_class = "phase-ns" if current_phase == "NS" else "phase-ew"
    phase_text = "North-South Green" if current_phase == "NS" else "East-West Green"
    st.markdown(f'<div class="phase-indicator {phase_class}">🔴 {phase_text}</div>', unsafe_allow_html=True)
    
    # Queue visualization
    st.markdown(f"""
    <div class="queue-visual">
        <div class="queue-direction">
            <div>🔺</div>
            <div class="queue-count">{queues['N']}</div>
            <div>NORTH</div>
        </div>
        <div style="display: flex; flex-direction: column; align-items: center;">
            <div class="queue-direction">
                <div>◀️</div>
                <div class="queue-count">{queues['W']}</div>
                <div>WEST</div>
            </div>
            <div style="margin: 1rem; padding: 1rem; background: var(--accent-primary); border-radius: 50%; color: var(--bg-primary); font-weight: 700;">
                🚦
            </div>
            <div class="queue-direction">
                <div>▶️</div>
                <div class="queue-count">{queues['E']}</div>
                <div>EAST</div>
            </div>
        </div>
        <div class="queue-direction">
            <div>🔻</div>
            <div class="queue-count">{queues['S']}</div>
            <div>SOUTH</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_enhanced_live_log_table():
    """Render enhanced live simulation log table with better formatting"""
    st.markdown("### 📋 **Live Traffic Analytics** <span class='live-indicator'>🟢 LIVE</span>", unsafe_allow_html=True)
    
    if not st.session_state.simulation_log:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: var(--bg-secondary); border-radius: 10px; border: 1px solid var(--border);">
            <p style="color: var(--text-secondary);">📊 Waiting for simulation data...</p>
            <p style="color: var(--text-secondary); font-size: 0.9rem;">Start the simulation to see real-time traffic analytics</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Convert log to DataFrame
    df = pd.DataFrame(st.session_state.simulation_log[-15:])  # Show last 15 entries
    
    if not df.empty:
        # Format columns
        display_data = []
        for _, row in df.iterrows():
            display_data.append({
                "⏰ Time": row["timestamp"].strftime("%H:%M:%S"),
                "🚦 Phase": "🟢 NS" if row["current_phase"] == "NS" else "🟠 EW",
                "🔺 N": row["queues"]["N"],
                "▶️ E": row["queues"]["E"],
                "🔻 S": row["queues"]["S"],
                "◀️ W": row["queues"]["W"],
                "✅ Served": row["vehicles_served"],
                "⏱️ Wait": f"{row['avg_wait_time']:.1f}s",
                "🚗 Total": row["vehicles_in_system"]
            })
        
        display_df = pd.DataFrame(display_data).iloc[::-1]  # Reverse order
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=350,
            hide_index=True
        )

def render_enhanced_charts():
    """Render enhanced performance charts with professional styling"""
    if len(st.session_state.simulation_log) < 2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: var(--bg-secondary); border-radius: 10px; border: 1px solid var(--border);">
            <p style="color: var(--text-secondary);">📈 Charts will appear here once simulation data is available</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    df = pd.DataFrame(st.session_state.simulation_log)
    
    # Wait Time Trend Chart
    st.markdown("### 📈 **Performance Trends**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_wait = go.Figure()
        fig_wait.add_trace(go.Scatter(
            x=df["timestamp"], 
            y=df["avg_wait_time"],
            mode='lines+markers',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=6, color='#00d4ff'),
            name='Wait Time',
            hovertemplate='<b>Wait Time</b><br>%{y:.1f} seconds<br>%{x}<extra></extra>'
        ))
        
        fig_wait.update_layout(
            title="Average Wait Time Trend",
            xaxis_title="Time",
            yaxis_title="Wait Time (seconds)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ffffff'),
            height=350,
            showlegend=False
        )
        
        fig_wait.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
        fig_wait.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
        
        st.plotly_chart(fig_wait, use_container_width=True)
    
    with col2:
        # Queue lengths chart
        queue_data = []
        for _, row in df.iterrows():
            for direction, count in row["queues"].items():
                queue_data.append({
                    "timestamp": row["timestamp"],
                    "direction": direction,
                    "queue_length": count
                })
        
        if queue_data:
            queue_df = pd.DataFrame(queue_data)
            
            fig_queue = go.Figure()
            colors = {'N': '#ff6b35', 'E': '#00d4ff', 'S': '#48bb78', 'W': '#ed8936'}
            
            for direction in ['N', 'E', 'S', 'W']:
                dir_data = queue_df[queue_df['direction'] == direction]
                fig_queue.add_trace(go.Scatter(
                    x=dir_data["timestamp"],
                    y=dir_data["queue_length"],
                    mode='lines+markers',
                    name=f'{direction} Direction',
                    line=dict(color=colors[direction], width=2),
                    marker=dict(size=4),
                    hovertemplate=f'<b>{direction} Direction</b><br>%{{y}} vehicles<br>%{{x}}<extra></extra>'
                ))
            
            fig_queue.update_layout(
                title="Queue Lengths by Direction",
                xaxis_title="Time",
                yaxis_title="Queue Length (vehicles)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#ffffff'),
                height=350,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            fig_queue.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
            fig_queue.update_yaxes(gridcolor='rgba(255,255,255,0.1)')
            
            st.plotly_chart(fig_queue, use_container_width=True)

def render_enhanced_session_management():
    """Render enhanced session management with better UX"""
    st.markdown("### 💾 **Session Management**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("� **Save Session**", use_container_width=True):
            if st.session_state.simulation_log:
                session_data = {
                    "timestamp": datetime.now().isoformat(),
                    "metrics": st.session_state.current_metrics,
                    "log_entries": len(st.session_state.simulation_log),
                    "duration": len(st.session_state.simulation_log)
                }
                st.session_state.session_history.append(session_data)
                st.success("✅ Session saved successfully!")
            else:
                st.warning("⚠️ No simulation data to save")
    
    with col2:
        if st.button("🗑️ **Clear Session**", use_container_width=True):
            st.session_state.simulation_log = []
            st.session_state.current_metrics = {}
            st.success("🧹 Session cleared!")
            st.rerun()
    
    with col3:
        if st.session_state.simulation_log:
            df = pd.DataFrame(st.session_state.simulation_log)
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 **Export CSV**",
                csv,
                f"traffic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=True
            )
    
    # Session History
    if st.session_state.session_history:
        st.markdown("---")
        st.markdown("**📚 Recent Sessions**")
        
        for i, session in enumerate(st.session_state.session_history[-3:]):  # Show last 3
            with st.expander(f"📊 Session {len(st.session_state.session_history) - i} - {session['timestamp'][:16]}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Duration", f"{session.get('duration', 0)} steps")
                with col2:
                    st.metric("Log Entries", session.get('log_entries', 0))
                with col3:
                    if session.get('metrics') and session['metrics'].get('avg_wait_time'):
                        st.metric("Avg Wait", f"{session['metrics']['avg_wait_time']:.1f}s")

# ====================== MAIN APPLICATION ======================

def main():
    """Main application entry point with professional enterprise interface"""
    
    # Page configuration with professional branding
    st.set_page_config(
        page_title="TrafficFlow Pro - Enterprise Traffic Management",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🚦"
    )
    
    # Load professional CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Professional Header with real-time status
    render_professional_header()

    # ---------------- Gamified Spec Runner (Engine-wired) ----------------
    st.markdown("---")
    st.subheader("Gamified Simulation (Engine-Wired)")

    if "g_spec_history" not in st.session_state:
        st.session_state.g_spec_history = []  # list[dict]
    if "g_spec_baseline" not in st.session_state:
        st.session_state.g_spec_baseline = None  # type: ignore[assignment]
    if "g_spec_rows" not in st.session_state:
        st.session_state.g_spec_rows = pd.DataFrame()

    with st.sidebar:
        st.markdown("### Gamified Controls")
        ctrl_mode = st.radio("Controller Mode", ["Fixed 40s", "Adaptive", "NEAT"], index=1)
        with st.expander("Adaptive Params"):
            min_green = st.slider("min_green_sec", 5, 40, 7)
            max_green = st.slider("max_green_sec", 20, 80, 40)
            gap_time = st.slider("gap_time_sec", 1, 8, 3)
            max_wait = st.slider("max_wait_sec", 30, 180, 90)
        with st.expander("Traffic Scenario"):
            demand = st.selectbox("demand_level", ["Off-peak", "Typical", "Rush"], index=1)
            sim_duration = st.slider("sim_duration_sec", 30, 600, 90, step=10)
            seed = st.number_input("random_seed", value=42, step=1)
            auto_run = st.checkbox("auto_run", value=True)
            episodes = st.number_input("episodes", min_value=1, value=3, step=1)
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            run_once = st.button("Run Once", use_container_width=True)
        with col_btn2:
            reset_btn = st.button("Reset", use_container_width=True)
        with col_btn3:
            export_btn = st.button("Export CSV", use_container_width=True)

    params = HybridParams(min_green=min_green, max_green=max_green, gap=gap_time, max_wait=max_wait)
    store = SessionStore()

    def do_run(n: int) -> None:
        rows_all: list[pd.DataFrame] = []
        for ep in range(n):
            engine = _make_engine("NEAT" if ctrl_mode == "NEAT" else "Toy", demand, int(seed) + ep)
            rows, kpis, extras = run_episode(engine, ctrl_mode, params, int(sim_duration))
            if ctrl_mode == "Fixed 40s":
                st.session_state.g_spec_baseline = kpis
            improvement = compute_improvement(kpis, st.session_state.g_spec_baseline)
            badges = award_badges(extras, kpis, params, improvement)
            df = pd.DataFrame(rows)
            df["mode"] = ctrl_mode
            df["episode"] = len(st.session_state.g_spec_history) + 1
            st.session_state.g_spec_history.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "mode": ctrl_mode,
                    "kpis": kpis,
                    "improvement_pct": improvement,
                    "badges": badges,
                }
            )
            rows_all.append(df)
            # persist
            store.append(
                df.assign(
                    demand=demand,
                    seed=seed,
                    min_green=min_green,
                    max_green=max_green,
                    gap=gap_time,
                    max_wait=max_wait,
                ).to_dict("records")
            )
        st.session_state.g_spec_rows = pd.concat(rows_all, ignore_index=True) if rows_all else pd.DataFrame()

    if reset_btn:
        st.session_state.g_spec_history = []
        st.session_state.g_spec_rows = pd.DataFrame()
        st.session_state.g_spec_baseline = None

    if run_once or (auto_run and st.session_state.g_spec_rows.empty):
        do_run(int(episodes if auto_run else 1))

    # KPIs
    latest_kpis = st.session_state.g_spec_history[-1]["kpis"] if st.session_state.g_spec_history else {}
    improvement_pct = (
        st.session_state.g_spec_history[-1]["improvement_pct"] if st.session_state.g_spec_history else 0.0
    )
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    with col_k1:
        st.metric("Avg Wait (s)", f"{latest_kpis.get('avg_wait', 0.0):.1f}")
    with col_k2:
        st.metric("Throughput (veh/h)", f"{latest_kpis.get('throughput', 0)}")
    with col_k3:
        st.metric("Total Queue", f"{latest_kpis.get('total_queue', 0)}")
    with col_k4:
        st.metric("% vs Fixed", f"{improvement_pct:.1f}%")

    # Badges
    if st.session_state.g_spec_history:
        badges = st.session_state.g_spec_history[-1]["badges"]
        st.write("Badges:", ", ".join(badges) if badges else "None yet")

    # Tabs: table, charts, history
    t1, t2, t3 = st.tabs(["Live Table", "Charts", "History"])
    with t1:
        if not st.session_state.g_spec_rows.empty:
            st.dataframe(st.session_state.g_spec_rows)
        else:
            st.info("No simulation data yet.")
    with t2:
        if not st.session_state.g_spec_rows.empty:
            df = st.session_state.g_spec_rows
            fig1 = px.line(df, x="time", y=["ns_queue", "ew_queue"], title="Queue length over time")
            st.plotly_chart(fig1, use_container_width=True)
            if "ns_served" in df and "ew_served" in df:
                df2 = df.assign(throughput_sec=df["ns_served"] + df["ew_served"])
                fig2 = px.line(df2, x="time", y="throughput_sec", title="Throughput per second")
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Run a simulation to see charts.")
    with t3:
        if st.session_state.g_spec_history:
            hist_df = pd.DataFrame(
                [
                    {
                        "timestamp": h["timestamp"],
                        "mode": h["mode"],
                        "avg_wait": h["kpis"].get("avg_wait", 0.0),
                        "throughput": h["kpis"].get("throughput", 0),
                        "total_queue": h["kpis"].get("total_queue", 0),
                        "improvement_pct": h.get("improvement_pct", 0.0),
                        "badges": ", ".join(h.get("badges", [])),
                    }
                    for h in st.session_state.g_spec_history
                ]
            )
            st.dataframe(hist_df)
        else:
            st.info("No history yet.")

    if export_btn:
        path = store.export_timestamped(st.session_state.g_spec_rows if not st.session_state.g_spec_rows.empty else None)
        st.success(f"Exported CSV to {path}")
    
    # Professional Sidebar with enhanced controls
    with st.sidebar:
        st.markdown("## 🎮 **Performance Dashboard**")
        render_gamification_panel()
        st.markdown("---")
        
        # Enhanced Control panel with professional styling
        st.markdown('<div class="control-section">', unsafe_allow_html=True)
        st.markdown("""
        <div class="control-header">
            <div class="control-icon">🎛️</div>
            <div>
                <h3 style="margin: 0; color: var(--text-primary);">Signal Control System</h3>
                <p style="margin: 0; color: var(--text-secondary); font-size: 0.875rem;">Advanced Traffic Optimization</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        mode, params = render_enhanced_control_panel()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Professional simulation controls
        st.markdown("### ▶️ **System Operations**")
        
        col1, col2 = st.columns(2)
        with col1:
            start_disabled = st.session_state.is_running
            start_button = st.button(
                "🚀 **INITIALIZE**" if not start_disabled else "🔄 **RUNNING**", 
                disabled=start_disabled, 
                use_container_width=True,
                help="Initialize traffic optimization system"
            )
            if start_button:
                st.session_state.is_running = True
                st.session_state.simulation_log = []
                st.session_state.simulator = TrafficSimulator()
                st.success("✅ System initialized successfully!")
                st.rerun()
        
        with col2:
            stop_disabled = not st.session_state.is_running
            stop_button = st.button(
                "⏹️ **TERMINATE**", 
                disabled=stop_disabled, 
                use_container_width=True,
                help="Stop system and process results"
            )
            if stop_button:
                st.session_state.is_running = False
                
                # Enhanced results processing
                if st.session_state.simulation_log:
                    with st.spinner("Processing optimization results..."):
                        df = pd.DataFrame(st.session_state.simulation_log)
                        runtime = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
                        
                        final_metrics = {
                            "avg_wait_time": df["avg_wait_time"].mean(),
                            "total_served": df["vehicles_served"].sum(),
                            "runtime": runtime,
                            "cycle_count": df["cycle_count"].iloc[-1] if not df.empty else 0
                        }
                        
                        st.session_state.current_metrics = final_metrics
                        
                        # Professional XP and achievement processing
                        efficiency = 0
                        if st.session_state.fixed_baseline:
                            efficiency = st.session_state.game_engine.calculate_efficiency_score(
                                final_metrics, st.session_state.fixed_baseline
                            )
                        
                        level_up, xp_earned = st.session_state.game_engine.award_xp(
                            efficiency, final_metrics["total_served"]
                        )
                        
                        new_badges = st.session_state.game_engine.check_badges(
                            efficiency, final_metrics["avg_wait_time"], final_metrics["total_served"]
                        )
                        
                        # Update professional statistics
                        stats = st.session_state.game_engine.session_stats
                        stats["total_runs"] += 1
                        stats["best_efficiency"] = max(stats["best_efficiency"], efficiency)
                        stats["best_wait_time"] = min(stats["best_wait_time"], final_metrics["avg_wait_time"])
                        stats["total_vehicles_served"] += final_metrics["total_served"]
                        
                        if mode == "Fixed 40s":
                            st.session_state.fixed_baseline = final_metrics.copy()
                        
                        # Professional achievement notifications
                        if level_up:
                            st.balloons()
                            st.success(f"🎉 **PROMOTION ACHIEVED!** Advanced to Level {st.session_state.game_engine.level} Traffic Engineer!")
                        
                        if new_badges:
                            st.success(f"🏆 **Professional Achievement Unlocked:** {', '.join(new_badges)}")
                        
                        if xp_earned > 0:
                            st.info(f"✨ **Performance Bonus:** +{xp_earned} XP earned this session!")
                
                st.success("� System terminated successfully!")
                st.rerun()
        
        # Professional system monitoring
        st.markdown("---")
        st.markdown("### 📊 **System Monitor**")
        
        # Real-time metrics
        if st.session_state.simulation_log:
            latest_data = st.session_state.simulation_log[-1]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Active Phase", latest_data["current_phase"])
                st.metric("Queue Total", latest_data["vehicles_in_system"])
            with col2:
                st.metric("Served/Sec", f"{latest_data['vehicles_served']}")
                st.metric("Avg Wait", f"{latest_data['avg_wait_time']:.1f}s")
        
        # System speed control
        sim_speed = st.slider(
            "⚡ **Processing Speed**", 
            0.1, 3.0, 1.0, 0.1,
            help="Adjust system processing frequency"
        )
        
        # Professional system status
        if st.session_state.is_running:
            st.success("🟢 **SYSTEM OPERATIONAL**")
            st.markdown(f"<small>Processing: {len(st.session_state.simulation_log)} data points</small>", unsafe_allow_html=True)
        else:
            st.info("🔴 **SYSTEM STANDBY**")
            st.markdown("<small>Ready for initialization</small>", unsafe_allow_html=True)
    
    # Main Professional Dashboard Area
    
    # Enhanced KPI Dashboard
    render_enhanced_kpi_dashboard(st.session_state.current_metrics, st.session_state.fixed_baseline)
    
    st.markdown("---")
    
    # Live professional intersection visualization
    if st.session_state.simulation_log:
        render_live_queue_visualization()
        st.markdown("---")
    
    # Professional analytics in columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_enhanced_charts()
    
    with col2:
        render_enhanced_live_log_table()
    
    st.markdown("---")
    
    # Professional session management
    render_enhanced_session_management()
    
    # Enhanced simulation loop with professional status
    if st.session_state.is_running:
        # Simulation processing
        current_sim_time = datetime.now().hour + datetime.now().minute / 60.0
        
        # Execute traffic optimization
        step_data = st.session_state.simulator.step_simulation(mode, params, current_sim_time)
        st.session_state.simulation_log.append(step_data)
        
        # Professional memory management
        if len(st.session_state.simulation_log) > 1200:  # Increased for better data retention
            st.session_state.simulation_log = st.session_state.simulation_log[-1200:]
        
        # Professional auto-refresh with smooth processing
        time.sleep(1.0 / sim_speed)
        st.rerun()
    
    # Professional system documentation
    st.markdown("---")
    st.markdown("""
    <div class="pro-card" style="margin-top: 2rem;">
        <h3 style="color: var(--accent-primary); text-align: center; margin-bottom: 2rem;">
            🎯 Professional Traffic Engineering Guide
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 2rem;">
            <div>
                <h4 style="color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                    <span>🚀</span> System Initialization
                </h4>
                <ul style="color: var(--text-secondary); line-height: 1.8;">
                    <li>Select <strong>Fixed 40s</strong> mode for baseline performance analysis</li>
                    <li>Click <strong>INITIALIZE</strong> to start traffic optimization</li>
                    <li>Monitor real-time KPIs and intersection visualization</li>
                    <li>Analyze traffic flow patterns and system efficiency</li>
                </ul>
            </div>
            
            <div>
                <h4 style="color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                    <span>⚡</span> Advanced Optimization
                </h4>
                <ul style="color: var(--text-secondary); line-height: 1.8;">
                    <li>Switch to <strong>Adaptive</strong> mode for AI-driven optimization</li>
                    <li>Fine-tune parameters: green times, gap detection, wait thresholds</li>
                    <li>Monitor efficiency improvements vs. baseline performance</li>
                    <li>Achieve professional certifications and unlock achievements</li>
                </ul>
            </div>
            
            <div>
                <h4 style="color: var(--text-primary); display: flex; align-items: center; gap: 0.5rem;">
                    <span>🏆</span> Professional Development
                </h4>
                <ul style="color: var(--text-secondary); line-height: 1.8;">
                    <li>Earn XP for optimizing wait times and maximizing throughput</li>
                    <li>Unlock professional achievements and engineering certifications</li>
                    <li>Export detailed analytics for regulatory compliance</li>
                    <li>Build expertise through progressive challenge completion</li>
                </ul>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border-color);">
            <p style="color: var(--text-tertiary); font-size: 0.875rem;">
                <strong>TrafficFlow Pro</strong> • Enterprise Traffic Management System • Version 2.0.0<br>
                Advanced AI Optimization • Real-time Analytics • Professional Gamification
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
