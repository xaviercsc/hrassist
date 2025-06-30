import pickle
from pathlib import Path
import hashlib

# Define user names, usernames, and passwords
names = ["Peter Parker", "Rebecca Miller"]
usernames = ["pparker", "rmiller"]
passwords = ["abc123", "def456"]

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Hash the passwords
hashed_passwords = [hash_password(pw) for pw in passwords]

# Determine the file path for storing hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"

# Save the hashed passwords to a file
with file_path.open("wb") as file:
    pickle.dump(hashed_passwords, file)
