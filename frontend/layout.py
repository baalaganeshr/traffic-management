# frontend/layout.py

import streamlit as st

def setup_layout():
    st.set_page_config(
        page_title="UrbanFlow360 - Real-Time Traffic Dashboard",
        layout="wide",
        page_icon="🚦"
    )

    # App header container
    with st.container():
        st.markdown(
            """
            <div style='display: flex; align-items: center;'>
                <h1 style='color: #FF4B4B; margin-right: 10px;'>🚦 UrbanFlow360</h1>
                <h3 style='color: white;'>Real-Time Traffic Dashboard</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color: #AAAAAA;'>Monitoring Bangalore Traffic with Predictive Alerts</p>",
            unsafe_allow_html=True
        )
        st.markdown("---")
