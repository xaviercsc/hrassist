# db.py

import sqlite3

def init_db():
    conn = sqlite3.connect("data/users.db")
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

    # Applications table (full structure)
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

# Call this once on app startup
init_db()
