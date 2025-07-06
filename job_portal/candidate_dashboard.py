# candidate_dashboard.py

import streamlit as st
import sqlite3
import os

DB_PATH = "data/users.db"
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        resume_path TEXT,
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

def apply_to_job(candidate, job_id, resume_path):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO applications (candidate, job_id, resume_path) VALUES (?, ?, ?)",
              (candidate, job_id, resume_path))
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
                resume = st.file_uploader("Upload your resume (docx)", type=["docx"], key=f"resume_{job[0]}")
                submitted = st.form_submit_button("Apply")
                if submitted:
                    if resume:
                        file_path = os.path.join(UPLOAD_DIR, f"{st.session_state.username}_{job[0]}.docx")
                        with open(file_path, "wb") as f:
                            f.write(resume.read())
                        apply_to_job(st.session_state.username, job[0], file_path)
                        st.success("Application submitted!")
                    else:
                        st.error("Please upload your resume.")

    st.subheader("📥 Your Applications")
    apps = get_candidate_applications(st.session_state.username)
    for title, status in apps:
        st.markdown(f"- **{title}** → `{status}`")

