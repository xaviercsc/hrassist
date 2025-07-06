# db.py

import sqlite3
import os

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "users.db")

# Ensure the data folder exists
os.makedirs(DB_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )''')

    # Jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        posted_by TEXT
    )''')

    # Applications table (basic if fresh)
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate TEXT,
        job_id INTEGER,
        status TEXT DEFAULT 'Submitted'
    )''')

    conn.commit()
    conn.close()

    # Run migration after initial setup
    migrate_applications_table()

def migrate_applications_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    columns = [
        "full_name TEXT", "email TEXT", "phone TEXT", "linkedin TEXT", "github TEXT",
        "objective TEXT", "skills TEXT", "experience TEXT", "education TEXT", "certifications TEXT"
    ]
    for col in columns:
        try:
            c.execute(f"ALTER TABLE applications ADD COLUMN {col}")
        except sqlite3.OperationalError:
            pass  # Column already exists

    conn.commit()
    conn.close()

# Call this once on app startup
init_db()
