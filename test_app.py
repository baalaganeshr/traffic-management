import streamlit as st
import os

# Simple test app for deployment verification
st.title("🚦 Traffic Management System - Deployment Test")

st.success("✅ App is successfully deployed!")

# Environment info
st.subheader("🔍 Environment Information")
col1, col2 = st.columns(2)

with col1:
    st.metric("Port", os.environ.get('PORT', 'Not set'))
    st.metric("Environment", os.environ.get('RENDER', 'Local'))

with col2:
    st.metric("Working Directory", os.getcwd())
    st.metric("Python Version", f"{st.__version__}")

# Test basic functionality
st.subheader("🧪 Basic Functionality Test")
if st.button("Test Button"):
    st.balloons()
    st.success("Button works! 🎉")

# Navigation
st.subheader("🔗 Navigation")
st.markdown("**Next Steps:**")
st.info("Once this test page works, the main app should work too!")

if st.button("🚀 Go to Main App"):
    st.switch_page("frontend/app_unified_improved.py")