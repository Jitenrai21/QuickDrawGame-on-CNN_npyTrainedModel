#!/bin/bash
# Django QuickDraw Game - Startup Script
# Usage: ./start_django.sh

echo "🚀 Starting Django QuickDraw Game..."
echo "📁 Working directory: $(pwd)"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source django_env/bin/activate 2>/dev/null || echo "⚠️ Virtual environment activation failed (Windows?)"

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -q -r requirements.txt

# Run migrations (optional - only needed if using Django models)
echo "🗄️ Running Django migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Start Django development server
echo "🌐 Starting Django development server..."
echo "🎮 Game will be available at: http://localhost:8000"
echo "📋 API documentation at: http://localhost:8000/admin/"
echo "🎯 API endpoints:"
echo "   - POST /api/recognize-drawing/"
echo "   - GET  /api/random-object/"
echo "   - GET  /api/model-info/"
echo "   - GET  /api/health/"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python manage.py runserver 0.0.0.0:8000