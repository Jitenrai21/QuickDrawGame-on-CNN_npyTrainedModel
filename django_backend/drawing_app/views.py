"""
Django REST Framework Views for QuickDraw Game
Replaces FastAPI routes with Django REST views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import time
import json

# Import our serializers and ML functions
from .serializers import (
    DrawingDataSerializer, 
    PredictionResponseSerializer,
    RandomObjectResponseSerializer,
    ModelInfoResponseSerializer,
    HealthResponseSerializer
)
from .ml_models import (
    predict_drawing, 
    get_random_object, 
    get_model_info, 
    get_class_emoji
)


@method_decorator(csrf_exempt, name='dispatch')
class RecognizeDrawingView(APIView):
    """
    API View for drawing recognition
    Replaces FastAPI: @router.post("/api/recognize-drawing")
    """
    
    def post(self, request):
        """
        Recognize drawing from 15 QuickDraw classes
        """
        try:
            # Validate input data using serializer
            serializer = DrawingDataSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid input data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validated_data = serializer.validated_data
            drawing = validated_data['drawing']
            object_to_draw = validated_data['object']
            
            print(f"🔍 Received drawing request:")
            print(f"   Object: {object_to_draw}")
            print(f"   Drawing points: {len(drawing)}")
            print(f"   Sample points: {drawing[:3] if len(drawing) >= 3 else drawing}")
            
            if not drawing:
                print("❌ No drawing data provided")
                return Response(
                    {"error": "No drawing data provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Record start time for performance tracking
            start_time = time.time()
            
            # Get the prediction from the model
            prediction_result = predict_drawing(drawing)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            print(f"🤖 Prediction result: {prediction_result}")
            
            # Check if there was an error in prediction
            if "error" in prediction_result:
                print(f"❌ Prediction error: {prediction_result['error']}")
                return Response(
                    {
                        "error": prediction_result["error"],
                        "prediction": "unknown",
                        "expected_object": object_to_draw
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Calculate if the prediction is correct
            predicted_object = prediction_result["prediction"]
            is_correct = predicted_object.lower() == object_to_draw.lower()
            
            print(f"✅ Returning successful prediction: {predicted_object}")
            
            # Return comprehensive prediction results
            response_data = {
                "success": True,
                "prediction": predicted_object,
                "expected_object": object_to_draw,
                "is_correct": is_correct,
                "confidence": prediction_result["confidence"],
                "top_predictions": prediction_result.get("top_predictions", {}),
                "all_probabilities": prediction_result.get("all_probabilities", {}),
                "model_info": prediction_result.get("model_info", "64x64 HYBRID model"),
                "resolution": prediction_result.get("resolution", "64x64"),
                "preprocessing_approach": prediction_result.get("preprocessing_approach", "HYBRID"),
                "processing_time_ms": processing_time_ms,
                "message": f"I think you drew a {predicted_object}!" if prediction_result["confidence"] > 0.5 else f"I'm not sure, but I think it might be a {predicted_object}."
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Server error in recognize_drawing: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {
                    "error": f"Server error: {str(e)}",
                    "prediction": "unknown",
                    "expected_object": request.data.get('object', 'unknown') if hasattr(request, 'data') else "unknown"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class RandomObjectView(APIView):
    """
    API View for getting random object to draw
    Replaces FastAPI: @router.get("/api/random-object")
    """
    
    def get(self, request):
        """
        Get a random object for the user to draw from 15 QuickDraw classes
        """
        try:
            random_object = get_random_object()
            emoji = get_class_emoji(random_object)
            
            response_data = {
                "success": True,
                "object": random_object,
                "emoji": emoji
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Server error: {str(e)}", "object": "apple"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class ModelInfoView(APIView):
    """
    API View for model information
    Replaces FastAPI: @router.get("/api/model-info")
    """
    
    def get(self, request):
        """
        Get information about the loaded model
        """
        try:
            info = get_model_info()
            return Response(info, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(APIView):
    """
    API View for health check
    Replaces FastAPI: @router.get("/api/health")
    """
    
    def get(self, request):
        """
        Simple health check for the API
        """
        response_data = {
            "status": "healthy",
            "message": "QuickDraw 15-Class Django API is running!",
            "version": "2.0.0",
            "framework": "Django + Django REST Framework"
        }
        return Response(response_data, status=status.HTTP_200_OK)


# Alternative function-based views (if you prefer them over class-based views)
@csrf_exempt
@api_view(['POST'])
def recognize_drawing_function_view(request):
    """
    Function-based view alternative for drawing recognition
    """
    view = RecognizeDrawingView()
    return view.post(request)


@csrf_exempt
@api_view(['GET'])
def random_object_function_view(request):
    """
    Function-based view alternative for random object
    """
    view = RandomObjectView()
    return view.get(request)


@csrf_exempt
@api_view(['GET'])
def model_info_function_view(request):
    """
    Function-based view alternative for model info
    """
    view = ModelInfoView()
    return view.get(request)


@csrf_exempt
@api_view(['GET'])
def health_check_function_view(request):
    """
    Function-based view alternative for health check
    """
    view = HealthCheckView()
    return view.get(request)
