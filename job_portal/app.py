# app.py

import streamlit as st
from auth import login_view, register_view
from hr_dashboard import hr_dashboard
from candidate_dashboard import candidate_dashboard

st.set_page_config(page_title="AI Job Portal", layout="wide")
st.title("🔐 AI-Powered Job Portal")

menu = st.sidebar.selectbox("Menu", ["Login", "Register"])
if menu == "Login":
    login_view()
elif menu == "Register":
    register_view()

# Role-based dashboards
if st.session_state.get("logged_in"):
    if st.session_state.get("role") == "hr":
        hr_dashboard()
    elif st.session_state.get("role") == "candidate":
        candidate_dashboard()
