# frontend/components/kpi_card.py

import streamlit as st
import streamlit.components.v1 as components

def kpi_card(title, value, color="green"):
    """
    Display a styled KPI card.

    Args:
        title (str): KPI title
        value (str or int): KPI value
        color (str): Indicator color ('green', 'orange', 'red')
    """
    st.markdown(f"""
        <div style="background-color: #f9f9f9;
                    padding: 1rem 1.5rem;
                    border-left: 5px solid {color};
                    border-radius: 0.5rem;
                    box-shadow: 1px 1px 5px rgba(0, 0, 0, 0.1);
                    margin-bottom: 1rem;">
            <h5 style="margin: 0; color: #333;">{title}</h5>
            <h3 style="margin: 0; color: #111;">{value}</h3>
        </div>
    """, unsafe_allow_html=True)
