"""
URL Configuration for Drawing App
Maps URLs to views (replaces FastAPI router)
"""
from django.urls import path
from . import views

# App namespace
app_name = 'drawing_app'

urlpatterns = [
    # Main API endpoints (class-based views) - support both with and without trailing slash
    path('api/recognize-drawing/', views.RecognizeDrawingView.as_view(), name='recognize_drawing'),
    path('api/recognize-drawing', views.RecognizeDrawingView.as_view(), name='recognize_drawing_no_slash'),
    path('api/random-object/', views.RandomObjectView.as_view(), name='random_object'),
    path('api/random-object', views.RandomObjectView.as_view(), name='random_object_no_slash'),
    path('api/model-info/', views.ModelInfoView.as_view(), name='model_info'),
    path('api/model-info', views.ModelInfoView.as_view(), name='model_info_no_slash'),
    path('api/health/', views.HealthCheckView.as_view(), name='health_check'),
    path('api/health', views.HealthCheckView.as_view(), name='health_check_no_slash'),
    
    # Alternative function-based views (uncomment if preferred)
    # path('api/recognize-drawing/', views.recognize_drawing_function_view, name='recognize_drawing_func'),
    # path('api/random-object/', views.random_object_function_view, name='random_object_func'),
    # path('api/model-info/', views.model_info_function_view, name='model_info_func'),
    # path('api/health/', views.health_check_function_view, name='health_check_func'),
]