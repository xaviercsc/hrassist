# cv_parser.py

from docx import Document
import os

# -----------------------------
# PARSE DOCX RESUME CONTENT
# -----------------------------
def parse_docx_resume(file_path):
    if not os.path.exists(file_path):
        return ""

    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text.strip())
        return "\n".join([t for t in full_text if t])
    except Exception as e:
        return f"Error reading resume: {e}"

# -----------------------------
# USAGE EXAMPLE
# -----------------------------
# profile_text = parse_docx_resume("data/uploads/john_doe_resume.docx")
