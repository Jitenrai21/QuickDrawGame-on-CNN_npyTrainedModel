"""
URL configuration for QuickDraw Game Django project.
Replaces FastAPI main routing with Django URL patterns.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.shortcuts import redirect


def root_view(request):
    """
    Root API view - equivalent to FastAPI root endpoint
    """
    return JsonResponse({
        "message": "Welcome to QuickDraw 15-Class Django API!",
        "docs": "/admin/",  # Django admin instead of FastAPI docs
        "frontend": "/static/index.html",
        "game": "Open /static/index.html to play the game!",
        "classes": "15 classes: apple, bowtie, candle, door, envelope, fish, guitar, ice cream, lightning, moon, mountain, star, tent, toothbrush, wristwatch",
        "framework": "Django + Django REST Framework"
    })


def game_redirect_view(request):
    """
    Game redirect view - equivalent to FastAPI /game endpoint
    """
    return redirect('/static/index.html')


urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API root and game redirect (FastAPI equivalents)
    path('', root_view, name='root'),
    path('game/', game_redirect_view, name='game'),
    
    # Include drawing app URLs
    path('', include('drawing_app.urls')),
    
    # Health check at root level (optional)
    path('health/', include('drawing_app.urls')),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
