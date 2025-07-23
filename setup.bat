@echo off
echo Setting up HR Assist AI Django Application...
echo.

echo Step 1: Install Python dependencies...
pip install -r requirements.txt
echo.

echo Step 2: Create database migrations...
python manage.py makemigrations hrapp
echo.

echo Step 3: Apply migrations...
python manage.py migrate
echo.

echo Step 4: Create superuser (optional)...
echo You can create a superuser now or skip this step.
python manage.py createsuperuser
echo.

echo Step 5: Starting development server...
echo The server will start at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver

pause
