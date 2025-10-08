"""
Django REST Framework Serializers for QuickDraw Game
Replaces FastAPI Pydantic models with DRF serializers
"""
from rest_framework import serializers


class CoordinatePointSerializer(serializers.Serializer):
    """
    Serializer for individual coordinate points
    Equivalent to FastAPI CoordinatePoint Pydantic model
    """
    x = serializers.FloatField(
        help_text="X coordinate (float for decimal precision)"
    )
    y = serializers.FloatField(
        help_text="Y coordinate (float for decimal precision)"
    )


class DrawingDataSerializer(serializers.Serializer):
    """
    Serializer for drawing data input
    Equivalent to FastAPI DrawingData Pydantic model
    """
    drawing = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of coordinate points [{'x': float, 'y': float}, ...]",
        allow_empty=False
    )
    object = serializers.CharField(
        max_length=100,
        help_text="The object that the user was supposed to draw"
    )

    def validate_drawing(self, value):
        """
        Validate that each drawing point has x and y coordinates
        """
        if not value:
            raise serializers.ValidationError("Drawing data cannot be empty")
        
        for i, point in enumerate(value):
            if not isinstance(point, dict):
                raise serializers.ValidationError(
                    f"Point {i} must be a dictionary with x and y coordinates"
                )
            
            if 'x' not in point or 'y' not in point:
                raise serializers.ValidationError(
                    f"Point {i} must contain both 'x' and 'y' coordinates"
                )
            
            try:
                float(point['x'])
                float(point['y'])
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f"Point {i} coordinates must be numeric (x: {point.get('x')}, y: {point.get('y')})"
                )
        
        return value


class PredictionResponseSerializer(serializers.Serializer):
    """
    Serializer for prediction response data
    Structures the response from ML model predictions
    """
    success = serializers.BooleanField(default=True)
    prediction = serializers.CharField(max_length=100)
    expected_object = serializers.CharField(max_length=100)
    is_correct = serializers.BooleanField()
    confidence = serializers.FloatField()
    top_predictions = serializers.DictField()
    all_probabilities = serializers.DictField()
    model_info = serializers.CharField()
    resolution = serializers.CharField()
    preprocessing_approach = serializers.CharField()
    message = serializers.CharField()


class RandomObjectResponseSerializer(serializers.Serializer):
    """
    Serializer for random object response
    """
    success = serializers.BooleanField(default=True)
    object = serializers.CharField(max_length=100)
    emoji = serializers.CharField(max_length=10)


class ModelInfoResponseSerializer(serializers.Serializer):
    """
    Serializer for model information response
    """
    model_loaded = serializers.BooleanField()
    input_shape = serializers.ListField(child=serializers.IntegerField())
    output_classes = serializers.IntegerField()
    classes = serializers.ListField(child=serializers.CharField())
    total_parameters = serializers.IntegerField()


class HealthResponseSerializer(serializers.Serializer):
    """
    Serializer for health check response
    """
    status = serializers.CharField()
    message = serializers.CharField()
    version = serializers.CharField()