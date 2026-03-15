import tensorflow as tf
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter
import io
import base64
import cv2
import random

# Navigate from backend/app/models/ to project root, then to models/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MODEL_PATH = os.path.join(PROJECT_ROOT, 'model_training', 'model_revised', 'QuickDraw_revised.keras')

# Load the 32-class QuickDraw model from revised training
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    print(f"Error loading model: {e}")
    # Fallback to previous models (64x64 compatible)
    fallback_paths = [
        os.path.join(PROJECT_ROOT, 'model_training', 'model_trad', 'QuickDraw_improved_final.keras'),
        os.path.join(PROJECT_ROOT, 'model_training', 'model_trad', 'QuickDraw_tradDataset.keras')
    ]
    
    model = None
    for fallback_path in fallback_paths:
        try:
            model = tf.keras.models.load_model(fallback_path)
            print(f"Using fallback model - performance may be reduced")
            break
        except Exception as e2:
            continue
    
    if model is None:
        print(f"Could not load any model. Please ensure model files exist.")

# Class labels for QuickDraw model (32 classes) - Updated to match revised training
CLASS_LABELS = [
    'airplane', 'apple', 'banana', 'bicycle', 'bowtie', 'bus', 'candle', 'car', 'cat', 'computer',
    'dog', 'door', 'elephant', 'envelope', 'fish', 'flower', 'guitar', 'horse', 'house', 'ice cream',
    'lightning', 'moon', 'mountain', 'rabbit', 'smiley face', 'star', 'sun', 'tent', 'toothbrush',
    'tree', 'truck', 'wristwatch'
]

def preprocess_drawing_to_image(drawing_data, canvas_size=(400, 400), target_size=(64, 64)):
    """
    Convert drawing coordinates to a 64x64 grayscale image for the revised model
    Combines web coordinate conversion + OpenCV preprocessing from QuickDrawApp.py
    
    PREPROCESSING PIPELINE:
    1. Convert coordinates to canvas image (PIL)
    2. Apply OpenCV preprocessing (medianBlur + GaussianBlur + OTSU threshold)
    3. Find contours and extract tight bounding box
    4. Crop to content + scale to 64x64
    
    Args:
        drawing_data: List of coordinate points [{x: int, y: int}]
        canvas_size: Original canvas size (width, height) - square (400, 400)
        target_size: Target image size for model (64, 64) - Standard size for revised model
    
    Returns:
        np.array: Preprocessed 64x64 image ready for model prediction
    """
    try:
        if not drawing_data or len(drawing_data) == 0:
            return None
        
        # STEP 1: Convert coordinates to canvas image with optimized stroke width
        canvas_ratio = canvas_size[0] / canvas_size[1]  # 400/400 = 1.0
        target_ratio = target_size[0] / target_size[1]  # 64/64 = 1.0
        
        # Create initial canvas - BLACK background, WHITE strokes (matches training)
        img = Image.new('L', canvas_size, color=0)  # BLACK background
        draw = ImageDraw.Draw(img)
        
        # Process strokes with improved stroke detection
        strokes = []
        current_stroke = []
        
        for i, point in enumerate(drawing_data):
            # Skip stroke end markers
            if 'strokeEnd' in point:
                if current_stroke:
                    strokes.append(current_stroke)
                    current_stroke = []
                continue
            
            current_stroke.append(point)
            
            # Check if this is the end of a stroke (gap detection)
            if i < len(drawing_data) - 1:
                next_point = drawing_data[i + 1]
                if 'strokeEnd' not in next_point:
                    # Calculate distance between consecutive points
                    dist = ((next_point['x'] - point['x'])**2 + (next_point['y'] - point['y'])**2)**0.5
                    
                    # If distance is too large, consider it a new stroke
                    if dist > 40:  # Threshold for square canvas
                        strokes.append(current_stroke)
                        current_stroke = []
        
        # Add final stroke
        if current_stroke:
            strokes.append(current_stroke)
        
        # Optimized stroke width for 64x64 (balance between detail and processing)
        line_width = max(6, min(10, int(min(canvas_size) / 50)))  # Optimized for 64x64
        
        for stroke in strokes:
            if len(stroke) > 1:
                # Draw lines connecting points in this stroke
                for i in range(len(stroke) - 1):
                    x1, y1 = int(stroke[i]['x']), int(stroke[i]['y'])
                    x2, y2 = int(stroke[i + 1]['x']), int(stroke[i + 1]['y'])
                    draw.line([(x1, y1), (x2, y2)], fill=255, width=line_width)  # WHITE strokes
            elif len(stroke) == 1:
                # Single point - draw a small circle
                x, y = int(stroke[0]['x']), int(stroke[0]['y'])
                radius = line_width // 2
                draw.ellipse([(x-radius, y-radius), (x+radius, y+radius)], fill=255)  # WHITE fill
        
        # Convert PIL to numpy for OpenCV processing
        canvas_array = np.array(img, dtype=np.uint8)
        
        # print(f"Preprocessing - Step 1: Canvas created ({canvas_array.shape}) with optimized strokes")
        
        # STEP 2: Apply OpenCV preprocessing (adapted from QuickDrawApp.py)
        
        # Apply median blur to remove noise (from QuickDrawApp.py line 86)
        blurred = cv2.medianBlur(canvas_array, 15)
        
        # Apply Gaussian blur for additional smoothing (from QuickDrawApp.py line 87)
        blurred = cv2.GaussianBlur(blurred, (5, 5), 0)
        
        # Apply OTSU thresholding for automatic threshold selection (from QuickDrawApp.py line 88)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # print(f"Preprocessing - Step 2: OpenCV preprocessing applied (medianBlur + GaussianBlur + OTSU)")
        
        # STEP 3: Find contours and extract tight bounding box (from QuickDrawApp.py lines 89-93)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        if len(contours) >= 1:
            # Find the largest contour (main drawing)
            cnt = max(contours, key=cv2.contourArea)
            contour_area = cv2.contourArea(cnt)
            
            print(f"Preprocessing - Step 3: Largest contour area = {contour_area}")
            
            # Only proceed if contour is significant (adapted threshold from QuickDrawApp.py)
            if contour_area > 1000:  # Threshold adapted for web drawings
                # Get tight bounding rectangle (from QuickDrawApp.py line 93)
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Extract the digit/drawing region (from QuickDrawApp.py line 94)
                digit = thresh[y:y + h, x:x + w]
                
                print(f"Preprocessing - Step 3: Bounding box = ({x}, {y}, {w}, {h})")
                print(f"Preprocessing - Step 3: Cropped to content ({digit.shape})")
                
                # STEP 4: Scale cropped content to 28x28
                digit_resized = cv2.resize(digit, target_size, interpolation=cv2.INTER_LANCZOS4)
                
                print(f"Preprocessing - Step 4: Scaled to {target_size}")
                
            else:
                print(f"Preprocessing - Warning: Small contour area ({contour_area}), using full canvas")
                # Fallback: use full canvas if no significant contours
                digit_resized = cv2.resize(thresh, target_size, interpolation=cv2.INTER_LANCZOS4)
                
        else:
            print(f"Preprocessing - Warning: No contours found, using full canvas")
            # Fallback: use full canvas if no contours
            digit_resized = cv2.resize(thresh, target_size, interpolation=cv2.INTER_LANCZOS4)
        
        # Convert to numpy array and normalize for model input
        img_array = np.array(digit_resized, dtype=np.float32)
        
        # Normalize pixel values to [0, 1] (model expects this for 28x28)
        img_array = img_array / 255.0
        
        # Reshape for model input: (1, 28, 28, 1)
        img_array = img_array.reshape(1, target_size[0], target_size[1], 1)

        
        # print(f"Preprocessing - COMPLETE:")
        # print(f"   OpenCV preprocessing: medianBlur + GaussianBlur + OTSU threshold")
        # print(f"   Intelligent cropping: contour detection + bounding box")
        # print(f"   28x28 scaling: Standard size for revised model")
        # print(f"   Content-focused: cropped to actual drawing area")
        # print(f"   Optimized stroke width: {line_width}px for 28x28")
        # print(f"   Normalized [0-1] values: proper for revised model")
        # print(f"   Final shape: {img_array.shape}")
        
        return img_array
        
    except Exception as e:
        print(f"Error in hybrid preprocessing: {e}")
        return None

def predict_drawing(drawing_data):
    """
    Predict the drawing from 32 QuickDraw classes using revised model
    Classes: airplane, apple, banana, bicycle, bowtie, bus, candle, car, cat, computer,
    dog, door, elephant, envelope, fish, flower, guitar, horse, house, ice cream,
    lightning, moon, mountain, rabbit, smiley face, star, sun, tent, toothbrush,
    tree, truck, wristwatch
    
    28x28 input with OpenCV preprocessing + normalized [0-1] values
    
    Args:
        drawing_data: List of coordinates [{x: int, y: int}]
    
    Returns:
        dict: Prediction results with confidence scores
    """
    if model is None:
        return {"error": "Model not loaded", "prediction": "unknown", "confidence": 0.0}
    
    try:
        # Convert drawing coordinates to 28x28 image with preprocessing
        processed_image = preprocess_drawing_to_image(drawing_data)
        
        if processed_image is None:
            return {"error": "Failed to process drawing", "prediction": "unknown", "confidence": 0.0}
        
        # Log image shape for debugging
        print(f"Processed image shape: {processed_image.shape}")
        
        # Check model input shape and ensure compatibility
        expected_shape = model.input_shape[1:3]  # (height, width)
        actual_shape = processed_image.shape[1:3]  # (height, width)
        
        print(f"Model expects: {expected_shape}, Got: {actual_shape}")
        
        if actual_shape != expected_shape:
            print(f"Shape mismatch! Resizing {actual_shape} to {expected_shape}")
            from PIL import Image
            # Convert back to PIL for resizing (keeping normalized values)
            img_pil = Image.fromarray((processed_image[0, :, :, 0] * 255).astype(np.uint8))
            img_resized = img_pil.resize(expected_shape[::-1], Image.Resampling.LANCZOS)  # PIL uses (width, height)
            processed_image = np.array(img_resized, dtype=np.float32) / 255.0  # Normalize for revised model
            processed_image = processed_image.reshape(1, expected_shape[0], expected_shape[1], 1)
            print(f"Resized to {processed_image.shape} for model compatibility (normalized values)")
        else:
            print(f"Perfect shape match! Using 64x64 directly with preprocessing!")
        
        # Make prediction
        prediction_probs = model.predict(processed_image, verbose=0)
        predicted_class_idx = np.argmax(prediction_probs[0])
        confidence = float(prediction_probs[0][predicted_class_idx])
        predicted_label = CLASS_LABELS[predicted_class_idx]
        
        # Get top 3 predictions
        top_indices = np.argsort(prediction_probs[0])[-3:][::-1]
        top_predictions = {}
        for idx in top_indices:
            top_predictions[CLASS_LABELS[idx]] = float(prediction_probs[0][idx])
        
        # if confidence > 0.5:
        #     print(f" EXCELLENT confidence! Hybrid approach working perfectly.")
        # elif confidence > 0.3:
        #     print(f" Good confidence improvement from hybrid preprocessing.")
        # else:
        #     print(f" Still optimizing - hybrid approach may need fine-tuning.")
        
        return {
            "prediction": predicted_label,
            "confidence": confidence,
            "top_predictions": top_predictions,
            "all_probabilities": {CLASS_LABELS[i]: float(prediction_probs[0][i]) for i in range(len(CLASS_LABELS))},
            "model_info": "32-class revised model with OpenCV preprocessing",
            "resolution": "64x64",
            "num_classes": 32,
            "preprocessing_approach": "Web coordinates + OpenCV (medianBlur + GaussianBlur + OTSU + contour crop)",
            "opencv_preprocessing": True,
            "content_cropping": True,
            "normalized_values": True,
            "model_version": "revised_32class"
        }
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        return {"error": str(e), "prediction": "unknown", "confidence": 0.0}

def get_random_object():
    """
    Get a random object for the user to draw from 32 QuickDraw classes
    Classes: airplane, apple, banana, bicycle, bowtie, bus, candle, car, cat, computer,
    dog, door, elephant, envelope, fish, flower, guitar, horse, house, ice cream,
    lightning, moon, mountain, rabbit, smiley face, star, sun, tent, toothbrush,
    tree, truck, wristwatch
    """
    return random.choice(CLASS_LABELS)

def get_model_info():
    """
    Get information about the loaded model
    """
    if model is None:
        return {"error": "Model not loaded"}
    
    try:
        return {
            "model_loaded": True,
            "input_shape": list(model.input_shape[1:]),
            "output_classes": len(CLASS_LABELS),
            "classes": CLASS_LABELS,
            "total_parameters": model.count_params()
        }
    except Exception as e:
        return {"error": str(e)}

def get_class_emoji(class_name):
    """
    Get emoji for a class name - Updated for new 32 class list
    """
    emoji_map = {
        'airplane': '✈️', 'apple': '🍎', 'banana': '🍌', 'bicycle': '🚲', 'bowtie': '🎀',
        'bus': '🚌', 'candle': '🕯️', 'car': '🚗', 'cat': '🐱', 'computer': '💻',
        'dog': '🐶', 'door': '🚪', 'elephant': '🐘', 'envelope': '✉️', 'fish': '🐟',
        'flower': '🌸', 'guitar': '🎸', 'horse': '🐴', 'house': '🏠', 'ice cream': '🍦',
        'lightning': '⚡', 'moon': '🌙', 'mountain': '⛰️', 'rabbit': '🐰', 'smiley face': '😊',
        'star': '⭐', 'sun': '☀️', 'tent': '⛺', 'toothbrush': '🪥', 'tree': '🌳',
        'truck': '🚚', 'wristwatch': '⌚'
    }
    return emoji_map.get(class_name, '❓')