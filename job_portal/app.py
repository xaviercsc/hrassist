# app.py

import streamlit as st
from auth import login_view, register_view
from hr_dashboard import hr_dashboard
from candidate_dashboard import candidate_dashboard
from db import init_db

# -----------------------------
# APP CONFIG
# -----------------------------
st.set_page_config(page_title="AI Job Portal", layout="wide")

# -----------------------------
# INITIALIZE DATABASE
# -----------------------------
init_db()

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
st.title("🧠 AI-Powered Job Portal")

menu = st.sidebar.selectbox("Select Option", ["Login", "Register"])

if menu == "Login":
    login_view()
elif menu == "Register":
    register_view()

# -----------------------------
# ROUTE TO USER DASHBOARDS
# -----------------------------
if st.session_state.get("logged_in"):
    role = st.session_state.get("role")
    if role == "hr":
        hr_dashboard()
    elif role == "candidate":
        candidate_dashboard()
