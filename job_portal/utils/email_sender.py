# email_sender.py

import smtplib
from email.message import EmailMessage
import os

# -----------------------------
# SEND EMAIL
# -----------------------------
def send_email(to_email, subject, body):
    EMAIL_ADDRESS = os.getenv("SMTP_USER")
    EMAIL_PASSWORD = os.getenv("SMTP_PASS")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise EnvironmentError("SMTP_USER and SMTP_PASS must be set as environment variables")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# -----------------------------
# USAGE EXAMPLE
# -----------------------------
# send_email("candidate@example.com", "Shortlisted for Interview", "Congratulations! You have been shortlisted.")
