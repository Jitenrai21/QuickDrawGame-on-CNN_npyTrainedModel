"""
URL Configuration for Drawing App
Maps URLs to views (replaces FastAPI router)
"""
from django.urls import path
from . import views

# App namespace
app_name = 'drawing_app'

urlpatterns = [
    # Main API endpoints (class-based views)
    path('api/recognize-drawing/', views.RecognizeDrawingView.as_view(), name='recognize_drawing'),
    path('api/random-object/', views.RandomObjectView.as_view(), name='random_object'),
    path('api/model-info/', views.ModelInfoView.as_view(), name='model_info'),
    path('api/health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # Alternative function-based views (uncomment if preferred)
    # path('api/recognize-drawing/', views.recognize_drawing_function_view, name='recognize_drawing_func'),
    # path('api/random-object/', views.random_object_function_view, name='random_object_func'),
    # path('api/model-info/', views.model_info_function_view, name='model_info_func'),
    # path('api/health/', views.health_check_function_view, name='health_check_func'),
]