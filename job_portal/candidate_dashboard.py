# candidate_dashboard.py

import streamlit as st
import sqlite3
import os

DB_PATH = "data/users.db"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# -----------------------------
# JOB APPLICATION TABLE SETUP
# -----------------------------
def init_application_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate TEXT,
        job_id INTEGER,
        full_name TEXT,
        email TEXT,
        phone TEXT,
        linkedin TEXT,
        github TEXT,
        objective TEXT,
        skills TEXT,
        experience TEXT,
        education TEXT,
        certifications TEXT,
        status TEXT DEFAULT 'Submitted'
    )''')
    conn.commit()
    conn.close()

# -----------------------------
# DATABASE FUNCTIONS
# -----------------------------
def get_all_jobs():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, description FROM jobs")
    jobs = c.fetchall()
    conn.close()
    return jobs

def apply_to_job(candidate, job_id, data):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO applications (
            candidate, job_id, full_name, email, phone, linkedin, github,
            objective, skills, experience, education, certifications
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        candidate, job_id, data["full_name"], data["email"], data["phone"],
        data["linkedin"], data["github"], data["objective"], data["skills"],
        data["experience"], data["education"], data["certifications"]
    ))
    conn.commit()
    conn.close()

def get_candidate_applications(candidate):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT j.title, a.status FROM applications a JOIN jobs j ON a.job_id = j.id WHERE a.candidate = ?", (candidate,))
    apps = c.fetchall()
    conn.close()
    return apps

# -----------------------------
# CANDIDATE DASHBOARD UI
# -----------------------------
def candidate_dashboard():
    st.header("🔍 Browse Jobs and Apply")

    jobs = get_all_jobs()
    for job in jobs:
        with st.expander(f"{job[1]}"):
            st.write(job[2])
            with st.form(f"apply_form_{job[0]}"):
                data = {}
                data["full_name"] = st.text_input("Full Name")
                data["email"] = st.text_input("Email")
                data["phone"] = st.text_input("Phone")
                data["linkedin"] = st.text_input("LinkedIn")
                data["github"] = st.text_input("GitHub/Portfolio")
                data["objective"] = st.text_area("Objective (2-3 lines)")
                data["skills"] = st.text_area("Skills (comma-separated or list)")
                data["experience"] = st.text_area("Experience")
                data["education"] = st.text_area("Education")
                data["certifications"] = st.text_area("Certifications")
                submitted = st.form_submit_button("Apply")
                if submitted:
                    if data["full_name"] and data["email"]:
                        apply_to_job(st.session_state.username, job[0], data)
                        st.success("Application submitted!")
                    else:
                        st.error("Full name and email are required.")

    st.subheader("📥 Your Applications")
    apps = get_candidate_applications(st.session_state.username)
    for title, status in apps:
        st.markdown(f"- **{title}** → `{status}`")
