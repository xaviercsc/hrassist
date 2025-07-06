# hr_dashboard.py

import streamlit as st
import sqlite3
import os
from utils.chatgpt import get_profile_match_percentage, generate_interview_questions
from utils.email_sender import send_email
from datetime import datetime

DB_PATH = "data/users.db"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# -----------------------------
# DATABASE FUNCTIONS
# -----------------------------
def get_jobs_by_hr(hr_username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, title, description FROM jobs WHERE posted_by = ?", (hr_username,))
    jobs = c.fetchall()
    conn.close()
    return jobs

def get_applicants_for_job(job_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT candidate, resume_path FROM applications WHERE job_id = ?", (job_id,))
    applicants = c.fetchall()
    conn.close()
    return applicants

def update_application_status(candidate, job_id, new_status):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE applications SET status = ? WHERE candidate = ? AND job_id = ?", (new_status, candidate, job_id))
    conn.commit()
    conn.close()

# -----------------------------
# HR DASHBOARD UI
# -----------------------------
def hr_dashboard():
    st.header("📋 HR Dashboard – Your Job Postings")

    jobs = get_jobs_by_hr(st.session_state.username)

    for job in jobs:
        with st.expander(f"📌 {job[1]}"):
            st.write(job[2])
            st.markdown("**📨 Applicants:**")
            applicants = get_applicants_for_job(job[0])
            if not applicants:
                st.info("No applications yet.")
            for candidate, resume_path in applicants:
                with st.container():
                    st.subheader(f"👤 {candidate}")

                    # Preview resume
                    profile_text = parse_docx_resume(resume_path)
                    st.text_area("Resume Preview:", profile_text, height=150)

                    # Match % button
                    if st.button("🔎 Check Match %", key=f"match_{candidate}_{job[0]}"):
                        result = get_profile_match_percentage(job[2], profile_text)
                        st.info(f"Match Result: {result}")

                    # Interview questions
                    if st.button("🧠 Generate Interview Questions", key=f"questions_{candidate}_{job[0]}"):
                        questions = generate_interview_questions(job[2], profile_text)
                        st.text_area("Interview Questions:", questions, height=250, key=f"qbox_{candidate}_{job[0]}")

                        # Schedule interview
                        interview_date = st.date_input("📅 Select Interview Date", key=f"date_{candidate}_{job[0]}")
                        if st.button("📤 Confirm and Schedule Interview", key=f"confirm_{candidate}_{job[0]}"):
                            update_application_status(candidate, job[0], "Interview Scheduled")
                            send_email(to_email=st.session_state.username, subject="Interview Questions", body=questions)
                            send_email(to_email=candidate, subject="Interview Scheduled", body=f"You are scheduled for an interview on {interview_date}.")
                            st.success("Interview confirmed and emails sent.")
