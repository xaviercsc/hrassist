# auth.py

import streamlit as st
import sqlite3
import hashlib

DB_PATH = "data/users.db"

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hash_password(password), role))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pw = hash_password(password)
    c.execute("SELECT username, password, role FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    return user

def login_view():
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        user = login_user(username, password)
        if user and len(user) >= 3:
            st.session_state.logged_in = True
            st.session_state.username = user[0]  # username
            st.session_state.role = user[2]      # role
            st.success(f"Logged in as {user[2].capitalize()}: {user[0]}")
        else:
            st.error("Invalid credentials or unexpected user format.")

def register_view():
    st.subheader("📝 Register")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    role = st.selectbox("Register as", ["hr", "candidate"])
    register_btn = st.button("Register")

    if register_btn:
        try:
            register_user(username, password, role)
            st.success("Registered successfully. Please log in.")
        except sqlite3.IntegrityError:
            st.error("Username already exists. Try a different one.")
