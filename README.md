# 🎨 QuickDraw Game - AI-Powered Drawing Recognition

A full-stack AI-powered drawing game where users draw objects and a trained CNN model tries to recognize them in real-time.

## Architecture Overview

```
QuickDrawGame/
├── frontend/           # Vanilla JS frontend with canvas drawing
├── backend/            # FastAPI backend with ML model integration
├── model_training/     # Jupyter notebook & trained models
├── requirements.txt    # Python dependencies
├── features_onTrad     # Feature data files
├── labels_onTrad       # Label data files
└── Project_Structure   # Project structure documentation
```

## Features

- **Real-time Drawing Recognition**: Draw with mouse/touch, get instant AI feedback
- **Multi-class Drawing Classification**: Trained CNN model for various object recognition
- **Responsive Design**: Works on desktop and mobile devices
- **Detailed Results**: Shows confidence scores and analysis
- **Modern UI**: Beautiful styling with smooth animations
- **Confidence Calibration**: Enhanced model training with calibrated confidence scores

## 🎬 Demo Video

<div align="center">
  <img src="https://github.com/Jitenrai21/QuickDrawGame/blob/main/demo/quickdraw-demo.gif" alt="QuickDraw Game Demo" width="600"/>
  <p><em>🎮 Watch the AI recognize drawings in real-time!</em></p>
</div>

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Model Training
Ensure your model is trained and saved in `model_training/model_trad/`:
- `QuickDraw_CALIBRATED_FINAL_64x64.keras` (recommended)
- `QuickDraw_improved_64x64_final.keras` (alternative)
- Or any other trained model from the `model_trad/` directory

### 3. Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open Frontend
Open `frontend/index.html` in your browser or serve it through a web server.

### 5. Play the Game!
Start drawing and see what the AI recognizes!

## 🔧 Technical Details

### Backend (FastAPI)
- **Model Loading**: Automatic loading of Keras/TensorFlow model
- **Image Processing**: Converts drawing coordinates to 32x32 images
- **API Endpoints**: 
  - `/api/recognize-drawing` - Main prediction endpoint
  - `/api/random-object` - Get random apple/banana
  - `/api/model-info` - Model status and info
  - `/docs` - Interactive API documentation

### Frontend (Vanilla JS)
- **Canvas Drawing**: Smooth drawing with mouse/touch support
- **Real-time Feedback**: Instant recognition results
- **Mobile Responsive**: Touch-friendly interface
- **Error Handling**: Graceful handling of network/server issues

### Model Integration
- **Input Processing**: Drawing coordinates → 64x64 grayscale image
- **Normalization**: Pixel values normalized to [0,1] range
- **Prediction**: Multi-class classification with confidence scores
- **Calibration**: Enhanced confidence calibration for better reliability
- **Output**: Detailed results with per-class probabilities

## 📊 Model Performance

Based on training results from `confidence_calibrated_training.ipynb`:
- **Model Architecture**: Improved CNN with calibration
- **Input Size**: 64x64x1 grayscale images
- **Training**: Confidence calibrated for better reliability
- **Available Models**: Multiple trained variants in `model_trad/` directory

## 🎮 How to Play

1. **Start Drawing**: Use your mouse or touch to draw on the canvas
2. **Submit Drawing**: Click the submit button when you're done
3. **View Results**: See what the AI thinks you drew with confidence scores
4. **Try Again**: Clear the canvas and draw something new

## 🛠️ Development

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload
```

### Adding New Features

#### New Object Classes
1. Retrain model with additional classes in `confidence_calibrated_training.ipynb`
2. Update `CLASS_LABELS` in `drawing_model.py`
3. Update frontend object selection logic

#### Improve Model Accuracy
1. Use different training datasets
2. Add data augmentation techniques
3. Try different CNN architectures available in the notebook
4. Experiment with confidence calibration methods

### API Endpoints

#### POST `/api/recognize-drawing`
```json
{
  "drawing": [{"x": 100, "y": 150}, ...],
  "object": "drawing_object"
}
```

Response:
```json
{
  "success": true,
  "prediction": "predicted_class",
  "confidence": 0.87,
  "class_probabilities": {...},
  "message": "Prediction result message"
}
```

#### GET `/api/model-info`
```json
{
  "success": true,
  "model_loaded": true,
  "model_path": "model_trad/QuickDraw_CALIBRATED_FINAL_64x64.keras",
  "input_shape": [64, 64, 1]
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Model Not Loading**
   - Check if model files exist in `model_training/model_trad/`
   - Verify TensorFlow installation: `pip install tensorflow`
   - Ensure correct model path in `drawing_model.py`

2. **CORS Errors**
   - Backend should include CORS middleware for frontend access
   - Check browser developer tools for specific errors

3. **Drawing Not Recognized**
   - Draw clearly and use more of the canvas area
   - Ensure drawing has sufficient detail
   - Check model training quality in the notebook

4. **Server Won't Start**
   - Install dependencies: `pip install -r requirements.txt`
   - Check if port 8000 is available
   - Run uvicorn from the backend directory

### Development Tips

1. **Model Improvements**
   - Experiment with different models in `model_trad/`
   - Use confidence calibration techniques
   - Try different CNN architectures
   - Implement ensemble methods

2. **Frontend Enhancements**
   - Add drawing tools and brush sizes
   - Implement drawing tutorials
   - Add animation effects
   - Improve mobile responsiveness

3. **Backend Optimizations**
   - Add model caching and optimization
   - Implement batch predictions
   - Add request rate limiting
   - Enhance error handling

## Mobile Support

The game is fully responsive and supports:
- Touch drawing on tablets/phones
- Responsive canvas sizing
- Mobile-friendly UI elements
- Touch event handling

## Future Enhancements

- [ ] Add more object classes and training data
- [ ] Implement user scoring and progress tracking
- [ ] Add multiplayer functionality
- [ ] Progressive Web App (PWA) support
- [ ] Real-time collaborative drawing
- [ ] Advanced drawing tools and features
- [ ] Model ensemble and improved accuracy
- [ ] Mobile app development

## Training Details

The model training is handled in `confidence_calibrated_training.ipynb` which includes:
- Data preprocessing and augmentation
- CNN architecture design and optimization
- Confidence calibration techniques
- Model evaluation and comparison
- Multiple model variants in `model_trad/` directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Happy Drawing! 🎨✨**
