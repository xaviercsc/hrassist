# hr_dashboard.py

import streamlit as st
import sqlite3

DB_PATH = "data/users.db"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# -----------------------------
# JOB TABLE SETUP
# -----------------------------
def init_job_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        posted_by TEXT
    )''')
    conn.commit()
    conn.close()

# -----------------------------
# JOB POSTING FUNCTIONS
# -----------------------------
def post_job(title, description, posted_by):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO jobs (title, description, posted_by) VALUES (?, ?, ?)",
              (title, description, posted_by))
    conn.commit()
    conn.close()

def get_jobs_by_hr(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT title, description FROM jobs WHERE posted_by = ?", (username,))
    jobs = c.fetchall()
    conn.close()
    return jobs

# -----------------------------
# HR DASHBOARD UI
# -----------------------------
def hr_dashboard():
    st.header("📢 HR Dashboard: Post a Job")

    title = st.text_input("Job Title")
    description = st.text_area("Job Description")

    if st.button("Post Job"):
        if title and description:
            post_job(title, description, st.session_state.username)
            st.success("Job posted successfully!")
        else:
            st.error("Please fill in all fields.")

    st.subheader("📄 Jobs You Posted")
    jobs = get_jobs_by_hr(st.session_state.username)
    for job in jobs:
        st.markdown(f"**{job[0]}**\n\n{job[1]}")

