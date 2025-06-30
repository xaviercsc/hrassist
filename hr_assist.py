import streamlit as st
import pickle
from pathlib import Path
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Load hashed passwords from the pickle file
def load_hashed_passwords():
    file_path = Path(__file__).parent / "hashed_pw.pkl"
    with file_path.open("rb") as file:
        return pickle.load(file)

# Define user names and usernames
names = ["Peter Parker", "Rebecca Miller"]
usernames = ["pparker", "rmiller"]

# Load hashed passwords
hashed_passwords = load_hashed_passwords()

# Authentication function
def authenticate(username, password):
    hashed_input_password = hash_password(password)
    if username in usernames:
        index = usernames.index(username)
        return hashed_input_password == hashed_passwords[index]
    return False

# Streamlit app
def main():
    st.title("Smart HR Assistant")

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        st.header("Login")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                if authenticate(username, password):
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    st.success("Login successful!")
                else:
                    st.error("Invalid username or password.")
    else:
        st.sidebar.title("Options")
        if st.sidebar.button("Logout"):
            st.session_state['authenticated'] = False
            st.session_state['username'] = None
            st.info("You have been logged out. Please refresh the page.")

        st.header("Welcome to Smart HR Assistant")
        st.write(f"Hello, {st.session_state['username']}! This is your HR management dashboard.")
        
        # Add more HR functionalities here

if __name__ == "__main__":
    main()
