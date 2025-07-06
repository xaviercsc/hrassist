# db.py

import sqlite3
import os

DB_PATH = "data/users.db"

# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT CHECK(role IN ('hr', 'candidate'))
    )''')

    # Jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        posted_by TEXT
    )''')

    # Applications table
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
# GET CONNECTION
# -----------------------------
def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

