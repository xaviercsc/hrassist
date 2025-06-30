import streamlit as st
import hashlib
import pickle
from pathlib import Path

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

# Streamlit app for user signup
def main():
    st.title("User Signup")

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
