import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Applyst | Auto Job Tracker", layout="wide")

# Minimal CSS
st.markdown("""
<style>
.metric-card { background: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
.app-card { background: white; padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; 
           border-left: 4px solid #4A90E2; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.monitoring { background: #d4edda; border: 1px solid #c3e6cb; padding: 10px; 
             border-radius: 5px; margin: 10px 0; text-align: center; }
</style>
""", unsafe_allow_html=True)

# Auto-refresh state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0

# Check for auth success and trigger immediate refresh
if st.query_params.get('auth') == 'success':
    st.query_params.clear()
    st.rerun()

# Title
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>Applyst</h1><h3 style='text-align: center; color: #666;'>Auto Job Application Tracker</h3>", unsafe_allow_html=True)

# API helper
def api(endpoint, method='GET', data=None):
    try:
        response = getattr(requests, method.lower())(f"{os.getenv("BACKEND_URL", "http://localhost")}:{os.getenv("BACKEND_PORT", "5000")}{endpoint}", json=data)
        return response.status_code == 200, response.json() if response.content else None
    except:
        return False, None

# Get data
monitor_ok, monitor = api("/api/monitor/status")
apps_ok, apps = api("/api/applications")

if not apps_ok:
    st.error("⚠️ Backend not running. Start server: `cd server && python app.py`")
    apps = {"Applied": [], "Interview": [], "Offer": [], "Rejected": []}

monitoring = monitor_ok and monitor and monitor.get('is_running', False)

# Sidebar
with st.sidebar:
    st.markdown("### 📧 Gmail Connection")
    
    if not monitoring:
        if st.button("🔐 Sign in with Google", use_container_width=True):
            ok, auth = api("/api/gmail/auth-url")
            if ok and auth:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={auth["auth_url"]}" />', unsafe_allow_html=True)
            else:
                st.error("❌ Failed to get authorization URL")
    else:
        st.success(f"✅ {monitor.get('gmail_email', 'Gmail')} Connected")
        if st.button("🛑 Stop Monitoring", use_container_width=True):
            api("/api/monitor/stop", "POST")
            st.rerun()
    
    st.markdown("➕ Manually Add Application")
    
    with st.form("add_app"):
        company = st.text_input("Company Name")
        position = st.text_input("Position")
        stage = st.selectbox("Stage", ["Applied", "Interview", "Offer", "Rejected"])
        
        if st.form_submit_button("Add Application", use_container_width=True):
            if company and position:
                if api("/api/applications", "POST", {"company": company, "position": position, "stage": stage})[0]:
                    st.success("✅ Application added!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Failed to add application")
            else:
                st.error("Please fill in both company and position")

# Auto-refresh
if monitoring and time.time() - st.session_state.last_refresh > 10:
    st.session_state.last_refresh = time.time()
    st.rerun()

stages = ["Applied", "Interview", "Offer", "Rejected"]
colors = ["#4A90E2", "#F39C12", "#27AE60", "#E74C3C"]
emojis = ["📄", "🎤", "🎉", "❌"]

cols = st.columns(4)
for i, (stage, color, emoji) in enumerate(zip(stages, colors, emojis)):
    with cols[i]:
        st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid {color};">
                <h3 style="margin:0; color:{color};">{emoji} {stage}</h3>
                <h2 style="margin:0; color:{color};">{len(apps.get(stage, []))}</h2>
            </div>
        """, unsafe_allow_html=True)

# Applications
st.markdown("### 📋 Your Applications")
cols = st.columns(4)

for i, stage in enumerate(stages):
    with cols[i]:
        st.markdown(f"#### {emojis[i]} {stage}")
        
        for app in apps.get(stage, []):
            color = colors[i]
            st.markdown(f"""
                <div class="app-card" style="border-left-color: {color};">
                    <strong style="color: {color};">{app['company']}</strong><br>
                    <em style="color: {color};">{app['position']}</em><br>
                    <small style="color: {color};">Added: {app['date_added']}</small>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                next_stages = stages
                if next_stages:
                    new_stage = st.selectbox("Move to:", next_stages, key=f"m{app['id']}", label_visibility="collapsed", index=stages.index(stage))
                    if st.button("Move", key=f"bm{app['id']}", use_container_width=True):
                        if api(f"/api/applications/{app['id']}", "PUT", {"stage": new_stage})[0]:
                            st.success(f"Moved to {new_stage}!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed")
            
            with col2:
                if st.button("🗑️", key=f"bd{app['id']}", use_container_width=True):
                    if api(f"/api/applications/{app['id']}", "DELETE")[0]:
                        st.success("Deleted!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed")

# Empty state
if sum(len(apps.get(stage, [])) for stage in stages) == 0:
    st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h3>No applications yet!</h3>
            <p>Connect your Gmail to start automatic tracking, or add applications manually.</p>
        </div>
    """, unsafe_allow_html=True)
