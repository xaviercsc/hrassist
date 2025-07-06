# hr_dashboard.py

import streamlit as st
import sqlite3
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
    c.execute("""
        SELECT candidate, full_name, email, phone, linkedin, github, objective,
               skills, experience, education, certifications
        FROM applications
        WHERE job_id = ?
    """, (job_id,))
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

            for applicant in applicants:
                (candidate, full_name, email, phone, linkedin, github, objective,
                 skills, experience, education, certifications) = applicant

                with st.container():
                    st.subheader(f"👤 {full_name} ({candidate})")
                    st.markdown(f"**Email:** {email}")
                    st.markdown(f"**Phone:** {phone}")
                    st.markdown(f"**LinkedIn:** {linkedin}")
                    st.markdown(f"**GitHub:** {github}")
                    st.markdown("---")
                    st.markdown(f"**Objective:**\n{objective}")
                    st.markdown(f"**Skills:**\n{skills}")
                    st.markdown(f"**Experience:**\n{experience}")
                    st.markdown(f"**Education:**\n{education}")
                    st.markdown(f"**Certifications:**\n{certifications}")

                    profile_text = f"""
Objective: {objective}
Skills: {skills}
Experience: {experience}
Education: {education}
Certifications: {certifications}
                    """

                    if st.button("🔎 Check Match %", key=f"match_{candidate}_{job[0]}"):
                        result = get_profile_match_percentage(job[2], profile_text)
                        st.info(f"Match Result: {result}")

                    if st.button("🧠 Generate Interview Questions", key=f"questions_{candidate}_{job[0]}"):
                        questions = generate_interview_questions(job[2], profile_text)
                        st.text_area("Interview Questions:", questions, height=250, key=f"qbox_{candidate}_{job[0]}")

                        interview_date = st.date_input("📅 Select Interview Date", key=f"date_{candidate}_{job[0]}")
                        if st.button("📤 Confirm and Schedule Interview", key=f"confirm_{candidate}_{job[0]}"):
                            update_application_status(candidate, job[0], "Interview Scheduled")
                            send_email(to_email=st.session_state.username, subject="Interview Questions", body=questions)
                            send_email(to_email=email, subject="Interview Scheduled", body=f"Dear {full_name},\n\nYou are scheduled for an interview on {interview_date}.")
                            st.success("Interview confirmed and emails sent.")
