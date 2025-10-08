# Django QuickDraw Project
# Project Structure:
#
# django_backend/
# ├── quickdraw_project/          # Main Django project
# │   ├── __init__.py
# │   ├── settings.py             # Django settings
# │   ├── urls.py                 # Main URL configuration  
# │   ├── wsgi.py                 # WSGI config for deployment
# │   └── asgi.py                 # ASGI config for async
# ├── drawing_app/                # Django app for drawing functionality
# │   ├── __init__.py
# │   ├── views.py                # API views (replaces FastAPI routes)
# │   ├── models.py               # Django models (if needed)
# │   ├── serializers.py          # DRF serializers (replaces Pydantic)
# │   ├── ml_models.py            # ML model integration
# │   ├── urls.py                 # App-specific URLs
# │   ├── apps.py                 # App configuration
# │   └── tests.py                # Unit tests
# ├── manage.py                   # Django management script
# └── requirements.txt            # Django-specific dependencies
#
# Key Migration Points:
# 1. FastAPI app → Django project + apps
# 2. Pydantic models → DRF serializers
# 3. FastAPI routes → Django REST views
# 4. uvicorn → Django development server
# 5. FastAPI middleware → Django middleware