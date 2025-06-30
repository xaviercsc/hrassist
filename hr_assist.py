import streamlit as st
import pickle
from pathlib import Path
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Save user data to a file
def save_user_data(user_data):
    file_path = Path(__file__).parent / "user_data.pkl"
    if file_path.exists():
        with file_path.open("rb") as file:
            existing_data = pickle.load(file)
    else:
        existing_data = []

    existing_data.append(user_data)

    with file_path.open("wb") as file:
        pickle.dump(existing_data, file)

# Load user data from the pickle file
def load_user_data():
    file_path = Path(__file__).parent / "user_data.pkl"
    if file_path.exists():
        with file_path.open("rb") as file:
            return pickle.load(file)
    return []

# Authentication function
def authenticate(username, password):
    user_data = load_user_data()
    hashed_input_password = hash_password(password)
    for user in user_data:
        if user['username'] == username and user['password'] == hashed_input_password:
            return True, user['user_type'], user['full_name']
    return False, None, None

# Streamlit app
def main():
    st.title("Smart HR Assistant")

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    menu = ["Login", "Signup"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        if not st.session_state['authenticated']:
            st.header("Login")

            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")

                if submitted:
                    authenticated, user_type, full_name = authenticate(username, password)
                    if authenticated:
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.session_state['login_type'] = user_type
                        st.session_state['full_name'] = full_name
                        st.success("Login successful!")
                    else:
                        st.error("Invalid username or password.")
        else:
            st.sidebar.title("Options")
            if st.sidebar.button("Logout"):
                st.session_state['authenticated'] = False
                st.session_state['username'] = None
                st.session_state['login_type'] = None
                st.session_state['full_name'] = None
                st.info("You have been logged out. Please refresh the page.")

            st.header(f"Welcome to Smart HR Assistant ({st.session_state['login_type']})")
            st.write(f"Hello, {st.session_state['full_name']}! This is your HR management dashboard.")
            
            # Add more HR functionalities here
            
    elif choice == "Signup":
        st.header("Signup")

        with st.form("signup_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            user_type = st.selectbox("User Type", ["HR", "Candidate"])
            email = st.text_input("Email Address")
            
            submitted = st.form_submit_button("Sign Up")

            if submitted:
                if full_name and username and password and email:
                    hashed_password = hash_password(password)
                    user_data = {
                        "full_name": full_name,
                        "username": username,
                        "password": hashed_password,
                        "user_type": user_type,
                        "email": email
                    }
                    save_user_data(user_data)
                    st.success("Signup successful!")
                else:
                    st.error("Please fill in all the fields.")

if __name__ == "__main__":
    main()
