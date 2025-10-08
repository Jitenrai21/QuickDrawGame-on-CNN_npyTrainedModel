@echo off
REM Django QuickDraw Game - Windows Startup Script
REM Usage: start_django.bat

echo 🚀 Starting Django QuickDraw Game...
echo 📁 Working directory: %cd%

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call django_env\Scripts\activate.bat

REM Install dependencies if needed
echo 📦 Checking dependencies...
pip install -q -r requirements.txt

REM Run migrations (optional - only needed if using Django models)
echo 🗄️ Running Django migrations...
python manage.py makemigrations
python manage.py migrate

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Start Django development server
echo 🌐 Starting Django development server...
echo 🎮 Game will be available at: http://localhost:8000
echo 📋 API documentation at: http://localhost:8000/admin/
echo 🎯 API endpoints:
echo    - POST /api/recognize-drawing/
echo    - GET  /api/random-object/
echo    - GET  /api/model-info/
echo    - GET  /api/health/
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

python manage.py runserver 0.0.0.0:8000
pause