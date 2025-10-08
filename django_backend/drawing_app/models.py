"""
Django Models for QuickDraw Game
Optional models for data persistence and analytics
"""
from django.db import models
from django.utils import timezone
import json


class DrawingSession(models.Model):
    """
    Model to track drawing sessions (optional - for analytics)
    Can be used to store user interactions for model improvement
    """
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.session_id} - {self.created_at}"


class DrawingPrediction(models.Model):
    """
    Model to store individual drawing predictions (optional - for analytics)
    Useful for model performance tracking and improvement
    """
    session = models.ForeignKey(
        DrawingSession, 
        on_delete=models.CASCADE, 
        related_name='predictions',
        null=True, 
        blank=True
    )
    
    # Drawing data
    expected_object = models.CharField(max_length=100)
    drawing_data = models.JSONField(help_text="JSON array of coordinate points")
    
    # Prediction results
    predicted_object = models.CharField(max_length=100)
    confidence = models.FloatField()
    is_correct = models.BooleanField()
    all_probabilities = models.JSONField(null=True, blank=True)
    
    # Model metadata
    model_version = models.CharField(max_length=50, default="64x64_hybrid")
    processing_time_ms = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['expected_object']),
            models.Index(fields=['predicted_object']),
            models.Index(fields=['confidence']),
            models.Index(fields=['is_correct']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.expected_object} → {self.predicted_object} ({self.confidence:.2f})"
    
    @property
    def accuracy_percentage(self):
        return self.confidence * 100
    
    def save(self, *args, **kwargs):
        """Override save to validate drawing data"""
        if self.drawing_data:
            if not isinstance(self.drawing_data, list):
                raise ValueError("Drawing data must be a list of coordinate points")
        super().save(*args, **kwargs)


class ModelPerformanceMetrics(models.Model):
    """
    Model to track overall model performance (optional - for monitoring)
    """
    date = models.DateField(default=timezone.now)
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    average_confidence = models.FloatField(default=0.0)
    accuracy_percentage = models.FloatField(default=0.0)
    
    # Per-class metrics (JSON field for flexibility)
    class_metrics = models.JSONField(default=dict, blank=True)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Metrics for {self.date} - {self.accuracy_percentage:.1f}% accuracy"
    
    def calculate_accuracy(self):
        """Calculate accuracy percentage"""
        if self.total_predictions > 0:
            self.accuracy_percentage = (self.correct_predictions / self.total_predictions) * 100
        else:
            self.accuracy_percentage = 0.0
        return self.accuracy_percentage


# NOTE: These models are OPTIONAL for the FastAPI migration
# The main functionality works without database persistence
# You can comment out or skip migrations if you don't want data persistence
# To use these models, run: python manage.py makemigrations && python manage.py migrate
