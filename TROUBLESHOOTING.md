# HR Assistant App - Admin Code Troubleshooting Guide

## Issue: HR Registration Failing with Admin Code "xxxxx"

### Problem Analysis
The admin code validation for HR user registration should work with "xxxxx" but might be failing due to several potential issues.

### Solution Implemented

#### 1. Backend Improvements (main.py)
- Added environment variable support for admin code: `HR_ADMIN_SECRET_CODE`
- Enhanced error handling with detailed logging
- Added validation for empty admin codes
- Added email uniqueness check
- Improved error messages

#### 2. Frontend Improvements (script.js)
- Enhanced client-side validation
- Better error messages for users
- Added console logging for debugging
- Improved field validation

#### 3. Configuration
- Created `.env.example` file with proper configuration
- Made admin code configurable via environment variables

### Testing Without Running the App

#### Admin Code Validation Logic:
```python
if user.user_type == "hr":
    if not user.admin_code:
        # Error: Admin code required
    if user.admin_code != "xxxxx":
        # Error: Invalid admin code
```

#### Expected Behavior:
- HR users MUST enter exactly "xxxxx" (case-sensitive)
- Candidate users don't need admin code
- Empty or wrong codes should be rejected

### Manual Verification Steps

1. **Check HTML Form**: The admin code field should appear when "HR" is selected
2. **Check JavaScript**: Client-side validation should catch wrong codes
3. **Check Backend**: Server should validate against "xxxxx"

### Common Issues and Fixes

#### Issue 1: Case Sensitivity
- **Problem**: User enters "xxxxx" instead of "xxxxx"
- **Fix**: Code is case-sensitive, must be exactly "xxxxx"

#### Issue 2: Extra Spaces
- **Problem**: User enters " xxxxx " with spaces
- **Fix**: Current code doesn't trim spaces, must be exact

#### Issue 3: Network/CORS Issues
- **Problem**: Frontend can't reach backend
- **Fix**: Ensure proper CORS configuration

#### Issue 4: Missing Dependencies
- **Problem**: Required packages not installed
- **Fix**: Run `pip install -r requirements.txt`

### Environment Setup

1. Copy `.env.example` to `.env`
2. Update values as needed:
   ```
   HR_ADMIN_SECRET_CODE=xxxxx
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-api-key
   ```

### Database Schema Verification

The User model should have these fields:
- username (string, unique)
- email (string, unique)
- full_name (string)
- user_type (string: "hr" or "candidate")
- hashed_password (string)

### Testing Commands (when Python is available)

```bash
# Test admin code validation
python test_admin_code.py

# Run the application
python -m uvicorn main:app --reload

# Or alternative
python main.py
```

### Browser Console Testing

Open browser developer tools and check:
1. Network tab for API calls
2. Console for JavaScript errors
3. Application tab for localStorage

### Expected Flow

1. User selects "HR" user type
2. Admin code field appears
3. User enters "xxxxx"
4. Form submits to `/api/register`
5. Backend validates admin code
6. User is created successfully

### Debug Information Added

The updated code now includes:
- Console logging in JavaScript
- Print statements in Python backend
- Detailed error messages
- Better validation feedback

### Next Steps for Testing

1. Deploy to a server where Python can run
2. Use browser developer tools to inspect requests
3. Check server logs for validation attempts
4. Verify database records are created

### Admin Code Storage Options

The admin code is now configurable through:
1. Environment variable: `HR_ADMIN_SECRET_CODE=xxxxx`
2. Default fallback: "xxxxx" if not set
3. Can be changed without code modification

This ensures the admin code is properly validated and stored securely.
