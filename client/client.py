import streamlit as st

# Page Config
st.set_page_config(page_title="Applyst | Job Tracker", layout="wide")

# Title
st.markdown("""
    <h1 style='text-align: center; font-size: 3rem; color: #4A90E2;'>Applyst</h1>
    <h3 style='text-align: center; font-weight: normal;'>Your AI-Powered Job Application Tracker</h3>
    <hr style='border-top: 2px solid #bbb;'>
""", unsafe_allow_html=True)

# Four Category Columns
col1, col2, col3, col4 = st.columns(4)

# Dummy Content for Now 
with col1:
    st.subheader("📤 Applied")
    st.info("No new applications detected.")

with col2:
    st.subheader("🗓️ Interview")
    st.warning("No upcoming interviews.")

with col3:
    st.subheader("❌ Rejected")
    st.error("No rejections (yet!)")

with col4:
    st.subheader("✅ Accepted")
    st.success("Keep it up!")

# Footer
st.markdown("""
    <hr style='border-top: 1px solid #ddd;'>
    <p style='text-align: center; color: gray;'>Applyst helps you keep track of your job hunt with smart email parsing.</p>
""", unsafe_allow_html=True)
