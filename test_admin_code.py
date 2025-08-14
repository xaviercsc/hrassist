#!/usr/bin/env python3
"""
Test script to validate admin code logic without running the full application.
This will help identify if the issue is with the validation logic itself.
"""

# Simulate the admin code validation logic from main.py
def validate_admin_code(user_type, admin_code):
    """
    Simulate the admin code validation from the registration endpoint
    """
    if user_type == "hr":
        if not admin_code or admin_code != "xxxxx":
            return False, "Invalid admin secret code"
    return True, "Valid"

# Test cases
test_cases = [
    ("hr", "xxxxx"),      # Should pass
    ("hr", "xxxxx"),      # Should fail (case sensitive)
    ("hr", "WRONG"),       # Should fail
    ("hr", ""),            # Should fail (empty)
    ("hr", None),          # Should fail (None)
    ("candidate", None),   # Should pass (candidate doesn't need admin code)
    ("candidate", "xxxxx"), # Should pass (candidate with admin code)
]

print("Admin Code Validation Test Results:")
print("=" * 50)

for user_type, admin_code in test_cases:
    is_valid, message = validate_admin_code(user_type, admin_code)
    status = "✅ PASS" if is_valid else "❌ FAIL"
    print(f"{status} | User: {user_type:9} | Code: {str(admin_code):8} | {message}")

print("\n" + "=" * 50)
print("Expected behavior:")
print("- HR users MUST provide exactly 'xxxxx' (case sensitive)")
print("- Candidate users don't need admin code")
print("- Only the first test case should PASS for HR users")
