# QuickDraw Game - 32-Class AI Drawing Recognition

QuickDraw Game is a full-stack drawing recognition project where a user sketches an object and a trained convolutional neural network predicts what was drawn. The latest edition supports 32 drawing classes, updated gameplay, and improved UI behavior for desktop and mobile usage.

## Table of Contents

1. [Overview](#overview)
2. [What Is New in This Edition](#what-is-new-in-this-edition)
3. [Demo](#demo)
4. [Core Features](#core-features)
5. [Repository Structure and Component Assessment](#repository-structure-and-component-assessment)
6. [Technology Stack](#technology-stack)
7. [Prerequisites](#prerequisites)
8. [Installation](#installation)
9. [Running the Application (FastAPI Primary Path)](#running-the-application-fastapi-primary-path)
10. [Optional Django Backend Path](#optional-django-backend-path)
11. [How to Play](#how-to-play)
12. [API Reference](#api-reference)
13. [Supported 32 Classes](#supported-32-classes)
14. [Model and Inference Pipeline](#model-and-inference-pipeline)
15. [Training Workflow](#training-workflow)
16. [Troubleshooting](#troubleshooting)
17. [Testing and Validation](#testing-and-validation)
18. [Development Notes and Best Practices](#development-notes-and-best-practices)
19. [Roadmap](#roadmap)
20. [Contributing](#contributing)

## Overview

The repository includes:

- A Vanilla JavaScript frontend for drawing, round control, and real-time prediction display.
- A FastAPI backend (primary runtime) for model serving and inference endpoints.
- An optional Django backend implementation that mirrors API behavior.
- Training notebooks, data-loading scripts, and multiple model artifacts (legacy and revised).

The currently integrated backend route module uses the revised 32-class model path (`backend/app/models/drawing_model_revised.py`) and exposes APIs used by the frontend game flow.

## What Is New in This Edition

- Expanded from smaller class sets to a 32-class gameplay target space.
- Updated backend metadata and root API response for 32-class operation.
- Frontend object/category handling aligned with 32 categories.
- Updated demo asset for the latest gameplay edition.
- Documentation rewritten to reflect current repository state, including optional Django migration assets.

## Demo

The latest demo for the 32-class edition is available here:

<div align="center">
  <img src="https://github.com/Jitenrai21/QuickDrawGame/blob/main/demo/QD_32_demo.gif" alt="QuickDraw Game Demo" width="1280"/>
  <p><em>Watch the AI recognize drawings in real-time!</em></p>
</div>

## Core Features

- Real-time drawing game with a 30-second round timer.
- 32-class object recognition workflow.
- Backend model inference with class probabilities and top predictions.
- Touch, mouse, and pointer-device support for drawing.
- Mobile-friendly responsive frontend layout.
- API endpoints for prediction, random target retrieval, model info, and health checks.
- Optional Django backend implementation for teams preferring the Django ecosystem.

## Repository Structure and Component Assessment

```text
QuickDrawGame/
|-- backend/
|   |-- app/
|   |   |-- main.py
|   |   |-- routes/
|   |   |   |-- drawing.py
|   |   |-- models/
|   |   |   |-- drawing_model.py
|   |   |   |-- drawing_model_revised.py
|   |   |-- __init__.py
|-- frontend/
|   |-- index.html
|   |-- script.js
|   |-- css/
|   |   |-- main.css
|-- model_training/
|   |-- confidence_calibrated_training.ipynb
|   |-- model_training_revised.ipynb
|   |-- visualization.ipynb
|   |-- load_data_onTrad.py
|   |-- load_data_revised.py
|   |-- model_revised/
|   |   |-- QuickDraw_revised.keras
|   |-- model_trad/
|   |   |-- QuickDraw_CALIBRATED_64x64.keras
|   |   |-- QuickDraw_CALIBRATED_FINAL_64x64.keras
|   |   |-- QuickDraw_improved.keras
|   |   |-- QuickDraw_improved_64x64.keras
|   |   |-- QuickDraw_improved_64x64_final.keras
|   |   |-- QuickDraw_improved_final.keras
|   |   |-- QuickDraw_tradDataset.keras
|-- demo/
|   |-- QD_32_demo.gif
|   |-- quickdraw-demo.gif
|   |-- quickdraw-demo.mp4
|-- django_backend/
|   |-- manage.py
|   |-- README_DJANGO.md
|   |-- MIGRATION_NOTES.md
|   |-- requirements.txt
|   |-- start_django.bat
|   |-- start_django.sh
|   |-- test_api.py
|   |-- quickdraw_project/
|   |   |-- settings.py
|   |   |-- urls.py
|   |   |-- asgi.py
|   |   |-- wsgi.py
|   |-- drawing_app/
|   |   |-- views.py
|   |   |-- urls.py
|   |   |-- serializers.py
|   |   |-- ml_models.py
|   |   |-- models.py
|   |   |-- tests.py
|   |   |-- admin.py
|   |   |-- apps.py
|   |   |-- model_training/
|   |   |   |-- model_trad/
|   |   |   |   |-- QuickDraw_CALIBRATED_FINAL_64x64.keras
|-- features_onTrad
|-- features_revised
|-- labels_onTrad
|-- labels_revised
|-- Project_Structure
|-- requirements.txt
|-- README.md
```

Component assessment:

- `backend/app/main.py`: FastAPI app definition, CORS setup, static frontend mounting, root and health routes.
- `backend/app/routes/drawing.py`: API contract for inference, random target selection, model info, and API health. Imports the revised model adapter.
- `backend/app/models/drawing_model_revised.py`: Primary 32-class inference module currently wired into the API.
- `backend/app/models/drawing_model.py`: Legacy calibrated model module for earlier class sets; useful for historical comparison and fallback ideas.
- `frontend/index.html`, `frontend/script.js`, `frontend/css/main.css`: User gameplay experience, drawing events, round logic, and current visual design.
- `model_training/`: Training and experimentation workspace with revised and legacy notebooks, loaders, and model artifacts.
- `demo/`: Visual demo assets, including the latest 32-class GIF.
- `django_backend/`: Alternate backend implementation using Django REST Framework, plus migration and startup scripts.
- `features_*` and `labels_*`: Dataset-derived feature and label files used during model preparation workflows.
- `Project_Structure`: Existing project structure reference artifact retained from earlier documentation work.

## Technology Stack

- Frontend: HTML5, CSS3, Vanilla JavaScript, Canvas API.
- Primary API backend: FastAPI, Uvicorn, Pydantic.
- Optional backend path: Django, Django REST Framework, django-cors-headers.
- ML and data: TensorFlow/Keras, NumPy, OpenCV, Pillow, SciPy, scikit-learn, pandas.
- Notebook and analysis tooling: Jupyter notebooks, Matplotlib, Seaborn.

## Prerequisites

- Python 3.9 or newer recommended.
- `pip` for dependency installation.
- A machine capable of loading TensorFlow models.
- Browser with modern Canvas and Pointer Events support.

## Installation

1. Clone the repository and enter the root directory.
2. Install primary dependencies:

```bash
pip install -r requirements.txt
```

3. Confirm key model file availability for the revised edition:

- `model_training/model_revised/QuickDraw_revised.keras`

## Running the Application (FastAPI Primary Path)

1. Start the API server from `backend`:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open one of the following URLs:

- API root: `http://localhost:8000/`
- Interactive API docs: `http://localhost:8000/docs`
- Game page (served by backend): `http://localhost:8000/static/index.html`
- Game redirect endpoint: `http://localhost:8000/game`

3. Alternative frontend-only opening (if you are not serving static files through FastAPI):

- Open `frontend/index.html` directly in the browser.
- Ensure backend API is still running on port `8000` so game requests succeed.

## Optional Django Backend Path

Use this path only if you want to run the Django migration version in `django_backend/`.

1. Create and activate a virtual environment inside `django_backend`.
2. Install Django dependencies:

```bash
cd django_backend
pip install -r requirements.txt
```

3. Apply migrations and run the server:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

4. See `django_backend/README_DJANGO.md` and `django_backend/MIGRATION_NOTES.md` for migration-specific details.

## How to Play

1. Start a round.
2. Draw the target object within 30 seconds.
3. Watch live model guesses while drawing.
4. Review the round result.
5. Restart and repeat with a new target category.

Tips:

- Draw large and centered on the canvas.
- Use clear object-defining shapes.
- Avoid very short or sparse strokes.

## API Reference

Base URL (FastAPI default local): `http://localhost:8000`

`GET /`

- Returns service intro, docs path, static game path, and class metadata.

`GET /health`

- General service health status.

`GET /api/health`

- API health check route from drawing router.

`GET /api/random-object`

- Returns a random target object (from current class list).

`GET /api/model-info`

- Returns model shape, class count, class labels, and model metadata.

`POST /api/recognize-drawing`

- Request body:

```json
{
  "drawing": [{"x": 100.2, "y": 150.6}, {"x": 110.0, "y": 160.8}],
  "object": "apple"
}
```

- Response fields include:
  - `success`
  - `prediction`
  - `expected_object`
  - `is_correct`
  - `confidence`
  - `top_predictions`
  - `all_probabilities`
  - `message`

## Supported 32 Classes

The revised class set currently used by the backend model adapter is:

- airplane
- apple
- banana
- bicycle
- bowtie
- bus
- candle
- car
- cat
- computer
- dog
- door
- elephant
- envelope
- fish
- flower
- guitar
- horse
- house
- ice cream
- lightning
- moon
- mountain
- rabbit
- smiley face
- star
- sun
- tent
- toothbrush
- tree
- truck
- wristwatch

## Model and Inference Pipeline

Current primary path (`drawing_model_revised.py`):

1. Accept drawing coordinates captured from browser canvas interactions.
2. Rasterize strokes onto a grayscale canvas.
3. Apply OpenCV preprocessing:
   - Median blur
   - Gaussian blur
   - OTSU thresholding
4. Detect content contour and crop to a tight bounding box when possible.
5. Resize to model input shape and normalize pixel values to `[0, 1]`.
6. Run TensorFlow model inference and return prediction probabilities.

Model assets:

- Primary revised model: `model_training/model_revised/QuickDraw_revised.keras`
- Legacy/fallback artifacts: `model_training/model_trad/*.keras`

## Training Workflow

Main training and analysis files:

- `model_training/model_training_revised.ipynb`
- `model_training/confidence_calibrated_training.ipynb`
- `model_training/visualization.ipynb`
- `model_training/load_data_revised.py`
- `model_training/load_data_onTrad.py`

Typical workflow:

1. Prepare labels and features from dataset exports.
2. Train revised architecture and evaluate class-wise performance.
3. Export candidate models.
4. Validate integration through `/api/model-info` and gameplay tests.

## Troubleshooting

Model load failures:

- Verify the model file exists at `model_training/model_revised/QuickDraw_revised.keras`.
- Confirm TensorFlow version compatibility.
- Check backend logs for fallback behavior and path resolution.

API connectivity issues:

- Confirm FastAPI is running on `http://localhost:8000`.
- Check browser developer tools for request failures.
- Verify CORS settings if frontend is hosted from a different origin.

Drawing quality and recognition issues:

- Draw with larger strokes and clearer shape structure.
- Use more canvas area and avoid overly tiny drawings.
- Verify preprocessing assumptions in model code when changing brush behavior.

Port conflicts:

- If port `8000` is occupied, run on a different port and update frontend API base settings accordingly.

## Testing and Validation

Suggested checks after backend or model changes:

1. Start backend and verify `GET /health` and `GET /api/health`.
2. Verify model metadata with `GET /api/model-info`.
3. Validate random target retrieval with `GET /api/random-object`.
4. Run manual gameplay rounds across multiple classes.
5. If using Django path, run `django_backend/test_api.py` and Django tests.

## Development Notes and Best Practices

- Keep backend and frontend class lists synchronized.
- Avoid committing large local virtual environment directories.
- Version model files explicitly and document when class sets change.
- Treat `drawing_model.py` as legacy unless intentionally switching inference paths.
- Keep API response contracts stable to avoid frontend regressions.

## Roadmap

- Expand dataset quality checks for hard-to-distinguish class pairs.
- Add per-class evaluation summaries to repository docs.
- Add automated API smoke tests in CI.
- Introduce model version configuration via environment variables.
- Add optional persistence for game sessions and analytics.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Open a pull request with a clear summary of impact and validation steps.
