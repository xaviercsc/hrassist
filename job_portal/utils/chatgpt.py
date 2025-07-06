# chatgpt.py

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# MATCHING PROFILE TO JD
# -----------------------------
def get_profile_match_percentage(job_description, candidate_profile):
    prompt = f"""
Compare the following job description and candidate profile.
Return only the match percentage (0-100) and a one-line justification.

Job Description:
{job_description}

Candidate Profile:
{candidate_profile}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# -----------------------------
# GENERATE INTERVIEW QUESTIONS
# -----------------------------
def generate_interview_questions(job_description, candidate_profile):
    prompt = f"""
Based on the following job description and candidate profile, generate 10 relevant technical interview questions.

Job Description:
{job_description}

Candidate Profile:
{candidate_profile}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

