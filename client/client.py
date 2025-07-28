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
.loading-container { display: flex; flex-direction: column; align-items: center; justify-content: center; 
    padding: 3rem; text-align: center; background: #f8f9fa; border-radius: 10px; margin: 2rem 0; }
.spinner { border: 4px solid #f3f3f3; border-top: 4px solid #4A90E2; border-radius: 50%; 
    width: 40px; height: 40px; animation: spin 1s linear infinite; margin-bottom: 1rem; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = 0
if 'post_auth_loading' not in st.session_state:
    st.session_state.post_auth_loading = False
if 'auth_loading_start' not in st.session_state:
    st.session_state.auth_loading_start = 0

# Handle auth success
if st.query_params.get('auth') == 'success':
    st.query_params.clear()
    st.session_state.post_auth_loading = True
    st.session_state.auth_loading_start = time.time()
    st.rerun()

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

# Handle post-auth loading
if st.session_state.post_auth_loading:
    total_apps = sum(len(stage_apps) for stage_apps in apps.values())
    if monitoring and total_apps > 0:
        st.session_state.post_auth_loading = False
        st.rerun()
    elif time.time() - st.session_state.auth_loading_start > 30:
        st.session_state.post_auth_loading = False
        st.error("⚠️ Authentication completed but setup is taking longer than expected. Try refreshing.")
        st.rerun()
    else:
        st.markdown("""
            <div class="loading-container">
                <div class="spinner"></div>
                <h3 style="color: #4A90E2; margin: 0;">Setting up your job tracker...</h3>
                <p style="color: #666; margin: 0.5rem 0;">
                    ✅ Gmail connected successfully<br>🔄 Loading applications and starting monitoring...
                </p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(2)
        st.rerun()

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

# Auto-refresh (skip during loading)
if not st.session_state.post_auth_loading and monitoring and time.time() - st.session_state.last_refresh > 10:
    st.session_state.last_refresh = time.time()
    st.rerun()

stages = ["Applied", "Interview", "Offer", "Rejected"]
colors = ["#4A90E2", "#F39C12", "#27AE60", "#E74C3C"]
emojis = ["📄", "🎤", "🎉", "❌"]

# Metrics
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
                new_stage = st.selectbox("Move to:", stages, key=f"m{app['id']}", label_visibility="collapsed", index=stages.index(stage))
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
