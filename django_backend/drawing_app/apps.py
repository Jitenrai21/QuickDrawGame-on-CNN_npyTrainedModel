from django.apps import AppConfig


class DrawingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'drawing_app'
    verbose_name = 'QuickDraw Drawing Recognition'
    
    def ready(self):
        """
        Initialize ML model when Django app starts
        This replaces the FastAPI startup event
        """
        try:
            from .ml_models import load_model
            print("🚀 Django App: Initializing ML model...")
            load_model()
            print("✅ Django App: ML model initialized successfully!")
        except Exception as e:
            print(f"⚠️ Django App: Warning during ML model initialization: {e}")
            print("   Model will be loaded on first prediction request.")
