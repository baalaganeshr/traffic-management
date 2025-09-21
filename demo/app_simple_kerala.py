import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Kerala Traffic Demo", 
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kerala Traffic Data - Simple and Clean
KERALA_TRAFFIC_DATA = {
    "Kochi": {"vehicles": 2450, "speed": 25, "direction": "North-South"},
    "Thiruvananthapuram": {"vehicles": 1890, "speed": 32, "direction": "East-West"},
    "Kozhikode": {"vehicles": 1650, "speed": 28, "direction": "North-South"},
    "Thrissur": {"vehicles": 1220, "speed": 35, "direction": "East-West"},
    "Kollam": {"vehicles": 980, "speed": 38, "direction": "North-South"},
    "Alappuzha": {"vehicles": 850, "speed": 42, "direction": "East-West"},
    "Palakkad": {"vehicles": 750, "speed": 45, "direction": "North-South"},
    "Kottayam": {"vehicles": 680, "speed": 40, "direction": "East-West"}
}

# Simple, clean CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
    background: #1e293b;
    color: white;
}

/* Header with proper layout */
.demo-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    padding: 1.5rem 2rem;
    margin: -1rem -1rem 1rem -1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #475569;
}

.demo-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: white;
    margin: 0;
}

/* Back button styled like second image - pill shaped with proper arrow */
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
    letter-spacing: 0.025em;
}

.back-button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #3b36ef 100%);
    color: white !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    text-decoration: none !important;
}

.back-button:visited {
    text-decoration: none !important;
    color: white !important;
}

.back-button:focus {
    text-decoration: none !important;
    outline: none;
}

.back-button:active {
    text-decoration: none !important;
}

.back-button:link {
    text-decoration: none !important;
}

/* Override all possible link styles */
a.back-button, a.back-button:hover, a.back-button:visited, a.back-button:focus, a.back-button:active {
    text-decoration: none !important;
    border-bottom: none !important;
    text-underline-offset: unset !important;
    text-decoration-line: none !important;
    text-decoration-style: none !important;
}

/* Remove any potential border-bottom that might look like underline */
.back-button * {
    text-decoration: none !important;
    border-bottom: none !important;
}

.back-arrow {
    font-size: 16px;
    font-weight: 700;
}

/* Simple table styling */
.stDataFrame {
    background: #334155 !important;
    border-radius: 8px;
    border: 1px solid #475569;
}

.stDataFrame [data-testid="stTable"] {
    background: #334155 !important;
    color: white !important;
}

.stDataFrame table {
    background: #334155 !important;
    color: white !important;
}

.stDataFrame th {
    background: #475569 !important;
    color: white !important;
    border-bottom: 1px solid #64748b !important;
}

.stDataFrame td {
    background: #334155 !important;
    color: white !important;
    border-bottom: 1px solid #475569 !important;
}

/* Simple button styling */
.stButton > button {
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

.stButton > button:hover {
    background: #2563eb;
}

/* Special styling for back button */
.stButton[data-testid="baseButton-secondary"] > button {
    background: linear-gradient(135deg, #3b82f6 0%, #4f46e5 100%) !important;
    color: white !important;
    border-radius: 50px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    transition: all 0.3s ease !important;
}

.stButton[data-testid="baseButton-secondary"] > button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #3b36ef 100%) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* Enhanced chart styling */
.stPlotlyChart {
    background: #334155;
    border-radius: 12px;
    border: 1px solid #475569;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    margin-bottom: 1rem;
}

.chart-container {
    background: #334155;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid #475569;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .demo-header {
        flex-direction: column;
        gap: 1rem;
        padding: 1rem;
        margin: -1rem -0.5rem 1rem -0.5rem;
    }
    
    .demo-title {
        font-size: 1.5rem;
        text-align: center;
    }
    
    .back-button {
        padding: 0.75rem 1.5rem;
        font-size: 0.9rem;
        width: 100%;
        justify-content: center;
    }
    
    .stDataFrame {
        font-size: 0.85rem;
    }
    
    .chart-container {
        padding: 0.75rem;
    }
    
    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
}

@media (max-width: 480px) {
    .demo-header {
        padding: 0.75rem;
    }
    
    .demo-title {
        font-size: 1.3rem;
    }
    
    .back-button {
        padding: 0.625rem 1rem;
        font-size: 0.85rem;
    }
    
    .stDataFrame {
        font-size: 0.8rem;
    }
    
    .chart-container {
        padding: 0.5rem;
    }
}
</style>
""", unsafe_allow_html=True)

def create_traffic_dataframe():
    """Create the main traffic data DataFrame"""
    data = []
    for city, info in KERALA_TRAFFIC_DATA.items():
        data.append({
            "City": city,
            "Vehicle Count": info["vehicles"],
            "Speed (km/h)": info["speed"],
            "Direction": info["direction"],
            "Last Updated": datetime.now().strftime("%H:%M:%S")
        })
    return pd.DataFrame(data)

def export_data(df, format_type):
    """Export data in different formats (CSV and JSON only)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format_type == "CSV":
        csv_data = df.to_csv(index=False)
        return csv_data, f"kerala_traffic_{timestamp}.csv", "text/csv"
    
    elif format_type == "JSON":
        json_data = df.to_json(orient="records", indent=2)
        return json_data, f"kerala_traffic_{timestamp}.json", "application/json"

def create_vehicle_chart(df):
    """Create professional vehicle count chart"""
    try:
        fig = px.bar(
            df, 
            x="City", 
            y="Vehicle Count",
            title="Vehicle Count by City"
        )
        
        fig.update_layout(
            title={
                'text': "Vehicle Count by City",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': 'white', 'family': 'Inter'}
            },
            font=dict(color="white", family="Inter"),
            plot_bgcolor="#2d3748",
            paper_bgcolor="#334155",
            height=350,
            showlegend=False,
            margin=dict(l=60, r=40, t=80, b=80),
            xaxis=dict(
                tickangle=45, 
                color="white",
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True
            ),
            yaxis=dict(
                color="white",
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True,
                title="Vehicle Count"
            )
        )
        
        fig.update_traces(
            marker_color="#4f46e5",
            marker_line_color="rgba(255,255,255,0.2)",
            marker_line_width=1,
            hovertemplate='<b>%{x}</b><br>Vehicles: %{y:,}<extra></extra>'
        )
        
        return fig
    except Exception:
        return go.Figure().add_annotation(text="Chart loading...", showarrow=False)

def create_speed_chart(df):
    """Create professional speed chart with color coding"""
    try:
        # Enhanced color scheme for speed ranges
        colors = []
        for speed in df['Speed (km/h)']:
            if speed < 25:
                colors.append('#ef4444')  # Red for slow
            elif speed < 35:
                colors.append('#f59e0b')  # Orange for medium
            else:
                colors.append('#10b981')  # Green for fast
        
        fig = go.Figure(data=[go.Bar(
            x=df["City"],
            y=df["Speed (km/h)"],
            marker_color=colors,
            text=[f"{speed}" for speed in df["Speed (km/h)"]],
            textposition='outside',
            textfont=dict(color="white", size=12),
            marker_line_color="rgba(255,255,255,0.2)",
            marker_line_width=1,
            hovertemplate='<b>%{x}</b><br>Speed: %{y} km/h<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': "Speed by City",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': 'white', 'family': 'Inter'}
            },
            font=dict(color="white", family="Inter"),
            plot_bgcolor="#2d3748",
            paper_bgcolor="#334155",
            height=350,
            margin=dict(l=60, r=40, t=80, b=80),
            xaxis=dict(
                tickangle=45,
                color="white",
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True,
                title=""
            ),
            yaxis=dict(
                color="white",
                gridcolor="rgba(255,255,255,0.1)",
                showgrid=True,
                title="Speed (km/h)"
            )
        )
        
        return fig
    except Exception:
        return go.Figure().add_annotation(text="Chart loading...", showarrow=False)

def main():
    # Header with functional back button
    st.markdown("""
    <div class="demo-header" style="background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 1.5rem 2rem; margin: -1rem -1rem 1rem -1rem; border-bottom: 2px solid #475569; border-radius: 0 0 12px 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="demo-title" style="font-size: 1.8rem; font-weight: 600; color: white; margin: 0; font-family: 'Inter', sans-serif;">🚦 Kerala Traffic Demo</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("📊 Dashboard", key="go_dashboard", use_container_width=True, help="Go to Professional Dashboard"):
            st.switch_page("frontend/app_unified_improved.py")
    with col3:
        if st.button("🔄 Refresh", key="refresh_demo", use_container_width=True, help="Refresh Kerala traffic data"):
            st.rerun()

    # Create main DataFrame
    df = create_traffic_dataframe()
    
    # Simple export buttons (CSV and JSON only)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export CSV", use_container_width=True):
            data, filename, mime = export_data(df, "CSV")
            st.download_button("Download CSV", data, filename, mime, key="csv")
    
    with col2:
        if st.button("📋 Export JSON", use_container_width=True):
            data, filename, mime = export_data(df, "JSON")
            st.download_button("Download JSON", data, filename, mime, key="json")
    
    with col3:
        if st.button("� Refresh", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Simple table without too many decorations
    st.markdown("**Traffic Data:**")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Enhanced charts section
    st.markdown("---")
    st.markdown("### 📊 Traffic Analytics")
    
    chart_col1, chart_col2 = st.columns(2, gap="large")
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        try:
            st.plotly_chart(create_vehicle_chart(df), use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.info("📊 Vehicle chart loading...")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        try:
            st.plotly_chart(create_speed_chart(df), use_container_width=True, config={'displayModeBar': False})
        except Exception as e:
            st.info("⚡ Speed chart loading...")
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()