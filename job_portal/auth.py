# auth.py

import sqlite3
from hashlib import sha256

DB_PATH = "data/users.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_user_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT CHECK(role IN ('hr', 'candidate'))
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def register_user(username, password, role):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, hash_password(password), role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def login_view():
    import streamlit as st
    st.subheader("Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            conn.row_factory = sqlite3.Row
            user = c.execute(...).fetchone()
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.success(f"Logged in as {user[3].capitalize()}: {user[1]}")
        else:
            st.error("Invalid credentials")

def register_view():
    import streamlit as st
    st.subheader("Create a New Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    role = st.selectbox("Role", ["hr", "candidate"])
    if st.button("Register"):
        if register_user(username, password, role):
            st.success("User registered successfully!")
        else:
            st.error("Username already exists.")

