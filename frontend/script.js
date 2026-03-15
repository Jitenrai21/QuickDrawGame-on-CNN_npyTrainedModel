/**
 * QuickDraw Game Frontend
 * 
 * A real-time drawing recognition game powered by deep learning.
 * Detects 32 QuickDraw categories with live AI feedback.
 * 
 * Architecture:
 * - State: Centralized game state object
 * - UI: Cached DOM references for performance
 * - Events: Modular event handlers for user input
 * - API: Abstracted fetch operations with error handling
 * - Rendering: DOM-based (no innerHTML string interpolation)
 * 
 * @module frontend/script.js
 */

// ===================== API & Config =====================

/** @type {string} API base URL - localhost for development, current origin for production */
const API_BASE_URL = window.location.origin.includes('localhost')
    ? 'http://localhost:8000'
    : window.location.origin;

/** @type {number} Duration of each game round in seconds */
const ROUND_DURATION_SECONDS = 30;

/** @type {number} Minimum interval between real-time model evaluations (ms) */
const REALTIME_EVAL_MIN_INTERVAL_MS = 1000;

/** @type {number} Delay before evaluating drawing after stroke completes (ms) */
const STROKE_EVAL_DELAY_MS = 550;

/** @type {number} Canvas size in pixels (400x400) */
const CANVAS_SIZE = 400;

/** 
 * Emoji mapping for recognized objects
 * Maintains consistent visual identity for game objects
 * Falls back to question mark if object is unrecognized
 * @type {Object<string, string>}
 */
const FALLBACK_EMOJIS = {
    airplane: '✈️', apple: '🍎', banana: '🍌', bicycle: '🚲', bowtie: '🎀',
    bus: '🚌', candle: '🕯️', car: '🚗', cat: '🐱', computer: '💻',
    dog: '🐶', door: '🚪', elephant: '🐘', envelope: '✉️', fish: '🐟',
    flower: '🌸', guitar: '🎸', horse: '🐴', house: '🏠', 'ice cream': '🍦',
    lightning: '⚡', moon: '🌙', mountain: '⛰️', rabbit: '🐰', 'smiley face': '😊',
    star: '⭐', sun: '☀️', tent: '⛺', toothbrush: '🪥', tree: '🌳',
    truck: '🚚', wristwatch: '⌚'
};


/** @type {Array<string>} List of all supported object classes in fallback mode */
const FALLBACK_CLASSES = Object.keys(FALLBACK_EMOJIS);

/**
 * Central state management object
 * Tracks all game variables and player progress
 * @type {Object}
 * @property {number|null} timerId - Active interval ID for game timer
 * @property {number|null} evaluationTimeoutId - Pending evaluation timeout ID
 * @property {Object|null} modelInfo - Backend model metadata
 * @property {string} currentObject - Target object label player must draw
 * @property {boolean} gameActive - Whether game is currently running
 * @property {boolean} gameWon - Whether player successfully matched target
 * @property {number} timeLeft - Seconds remaining in current round
 * @property {boolean} drawing - Whether user is actively drawing
 * @property {Array<Object>} drawingData - Complete stroke history with timestamps
 * @property {Array<Object>} currentStroke - Points in stroke being drawn
 * @property {Object} lastPoint - Last canvas coordinate drawn
 * @property {number} lastRealtimeEvalAt - Timestamp of last real-time evaluation
 * @property {boolean} isEvaluating - Whether evaluation is in progress
 */
const state = {
    timerId: null,
    evaluationTimeoutId: null,
    modelInfo: null,
    currentObject: '',
    gameActive: false,
    gameWon: false,
    timeLeft: ROUND_DURATION_SECONDS,
    drawing: false,
    drawingData: [],
    currentStroke: [],
    lastPoint: { x: 0, y: 0 },
    lastRealtimeEvalAt: 0,
    isEvaluating: false
};

/**
 * Cached DOM element references
 * Centralizes selectors to prevent repeated queries
 * @type {Object}
 * @property {HTMLElement} startScreen - Start game screen container
 * @property {HTMLElement} gameScreen - Active game screen container
 * @property {HTMLElement} postGameScreen - Results screen container
 * @property {HTMLElement} startButton - Button to begin new game
 * @property {HTMLElement} restartButton - Button to restart game
 * @property {HTMLElement} clearButton - Button to clear canvas
 * @property {HTMLElement} objectPlaceholder - Emoji display during start screen
 * @property {HTMLElement} currentObjectLabel - Object label during game
 * @property {HTMLElement} timerContainer - Timer display container
 * @property {HTMLElement} timeLeft - Time remaining text
 * @property {HTMLElement} predictionText - Live model prediction display
 * @property {HTMLElement} modelGuess - Result display area
 * @property {HTMLElement} liveStatus - Accessibility live region
 * @property {HTMLElement} loadingResult - Loading spinner/message
 * @property {HTMLCanvasElement} canvas - Drawing canvas element
 */
const ui = {
    startScreen: document.getElementById('start-screen'),
    gameScreen: document.getElementById('game-screen'),
    postGameScreen: document.getElementById('post-game-screen'),
    startButton: document.getElementById('start-button'),
    restartButton: document.getElementById('restart-button'),
    clearButton: document.getElementById('clear-button'),
    siteHeader: document.getElementById('site-header'),
    objectPlaceholder: document.getElementById('object-placeholder'),
    currentObjectLabel: document.getElementById('current-object'),
    timerContainer: document.getElementById('timer'),
    timeLeft: document.getElementById('time-left'),
    predictionText: document.getElementById('prediction-text'),
    modelGuess: document.getElementById('model-guess'),
    liveStatus: document.getElementById('live-status'),
    loadingResult: document.getElementById('loading-result'),
    canvas: document.getElementById('drawing-canvas')
};

/** @type {CanvasRenderingContext2D} 2D canvas drawing context */
const ctx = ui.canvas.getContext('2d', { willReadFrequently: true });

/**
 * Application bootstrap
 * Initializes canvas, event handlers, and game state
 * Called on DOMContentLoaded
 */
function bootstrap() {
    configureCanvas();
    bindUiEvents();
    initializeGame();
}

/**
 * Configures canvas drawing properties
 * Sets size, drawing style, and performance hints
 * Must be called before any drawing operations
 */
function configureCanvas() {
    ui.canvas.width = CANVAS_SIZE;
    ui.canvas.height = CANVAS_SIZE;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    const strokeColor = getComputedStyle(document.documentElement)
        .getPropertyValue('--ink-color')
        .trim();
    ctx.strokeStyle = strokeColor || '#2c2a27';
    ctx.lineWidth = 5;
    clearCanvas();
}

/**
 * Attaches event listeners to UI controls
 * Handles click events on buttons and pointer events on canvas
 * Also sets up keyboard shortcuts (C for clear, Enter to start/restart)
 */
function bindUiEvents() {
    ui.startButton.addEventListener('click', startGame);
    ui.restartButton.addEventListener('click', restartGame);
    ui.clearButton.addEventListener('click', clearCanvas);

    ui.canvas.addEventListener('pointerdown', onPointerDown);
    ui.canvas.addEventListener('pointermove', onPointerMove);
    ui.canvas.addEventListener('pointerup', onPointerUp);
    ui.canvas.addEventListener('pointerleave', onPointerUp);
    ui.canvas.addEventListener('pointercancel', onPointerUp);

    document.addEventListener('keydown', handleKeyboardShortcuts);
}

/**
 * Initializes game by fetching model metadata and loading target object
 * Handles fallback if backend is unavailable
 * Updates live status and disables buttons during loading
 * @async
 */
async function initializeGame() {
    setLiveStatus('Connecting to backend...');
    setButtonsLoading(true);

    try {
        state.modelInfo = await fetchJson(`${API_BASE_URL}/api/model-info`);

        if (state.modelInfo && state.modelInfo.error) {
            throw new Error(state.modelInfo.error);
        }

        await loadNewTargetObject();
        setLiveStatus('Ready. Press Enter or Start Round to begin.');
    } catch (error) {
        console.error('Initialization error:', error);
        setNotice(
            ui.modelGuess,
            'error',
            `Could not connect to the backend. ${error.message || 'Please verify the API server is running.'}`
        );
        setLiveStatus('Backend unavailable. Fallback mode enabled.');
        await loadNewTargetObject();
    } finally {
        setButtonsLoading(false);
    }
}

/**
 * Enables or disables start and restart buttons
 * Called during async operations (model loading, API calls)
 * @param {boolean} isLoading - True to disable, false to enable
 */
function setButtonsLoading(isLoading) {
    ui.startButton.disabled = isLoading;
    ui.restartButton.disabled = isLoading;
}

/**
 * Switches active game screen with animation
 * Hides all screens except the active one
 * Also controls header visibility (hidden during game/results screens)
 * @param {HTMLElement} activeScreen - Screen element to display (start, game, or result)
 */
function setScreen(activeScreen) {
    const screens = [ui.startScreen, ui.gameScreen, ui.postGameScreen];
    screens.forEach((screen) => {
        const isActive = screen === activeScreen;
        screen.classList.toggle('is-active', isActive);
        screen.hidden = !isActive;
    });
    
    // Hide header during game and post-game screens, show on start screen
    const shouldHideHeader = activeScreen !== ui.startScreen;
    ui.siteHeader.classList.toggle('hidden-for-game', shouldHideHeader);
}

/**
 * Updates live status aria-live region for accessibility
 * Announces game messages to screen readers
 * @param {string} message - Status message to display and announce
 */
function setLiveStatus(message) {
    ui.liveStatus.textContent = message || '';
}

/**
 * Resets prediction display to hint text
 * Called when game starts or canvas is cleared
 */
function resetPredictionLabel() {
    ui.predictionText.textContent = 'Start drawing...';
}

/**
 * Resets game timer to maximum duration
 * Clears any custom timer styling
 */
function resetTimer() {
    state.timeLeft = ROUND_DURATION_SECONDS;
    ui.timeLeft.textContent = state.timeLeft;
    ui.timerContainer.style.color = '';
}

/**
 * Loads new random target object from backend
 * Falls back to random selection if API unavailable
 * Updates both start screen and game screen labels
 * @async
 */
async function loadNewTargetObject() {
    let objectLabel;

    try {
        const data = await fetchJson(`${API_BASE_URL}/api/random-object`);
        if (data && data.success && data.object) {
            objectLabel = data.object.toLowerCase();
            if (data.emoji) {
                FALLBACK_EMOJIS[objectLabel] = data.emoji;
            }
        }
    } catch (error) {
        console.warn('Could not fetch random object, using fallback:', error);
    }

    if (!objectLabel) {
        objectLabel = FALLBACK_CLASSES[Math.floor(Math.random() * FALLBACK_CLASSES.length)];
    }

    state.currentObject = objectLabel;
    const display = getObjectDisplay(objectLabel);
    ui.objectPlaceholder.textContent = display;
    ui.currentObjectLabel.textContent = display;
}

/**
 * Initiates new game round
 * Clears canvas, resets state, starts timer
 * Transitions to game screen
 */
function startGame() {
    setScreen(ui.gameScreen);
    state.gameActive = true;
    state.gameWon = false;
    state.isEvaluating = false;
    state.lastRealtimeEvalAt = 0;
    state.drawingData = [];
    state.currentStroke = [];

    clearPendingEval();
    clearCanvas();
    resetPredictionLabel();
    resetTimer();
    startTimer();

    setLiveStatus('Draw now. The model updates after each stroke.');
}

/**
 * Starts the round timer
 * Updates display every second, changes color as time runs out
 * Ends game when timer reaches zero
 * Uses 1-second interval; cleared when game ends
 */
function startTimer() {
    clearInterval(state.timerId);

    state.timerId = setInterval(() => {
        if (!state.gameActive || state.gameWon) {
            clearInterval(state.timerId);
            return;
        }

        state.timeLeft -= 1;
        ui.timeLeft.textContent = Math.max(state.timeLeft, 0);

        if (state.timeLeft <= 10) {
            ui.timerContainer.style.color = '#7f2c1f';
        } else if (state.timeLeft <= 20) {
            ui.timerContainer.style.color = '#7d6f65';
        }

        if (state.timeLeft <= 0) {
            clearInterval(state.timerId);
            state.gameActive = false;
            endGame();
        }
    }, 1000);
}

/**
 * Cancels any pending evaluation timeout
 * Prevents evaluation duplication if drawing is rapid
 */
function clearPendingEval() {
    if (state.evaluationTimeoutId) {
        clearTimeout(state.evaluationTimeoutId);
        state.evaluationTimeoutId = null;
    }
}

/**
 * Handles pointer down on canvas
 * Initializes new stroke with first point
 * Captures pointer to canvas to support all input types (mouse, touch, pen)
 * @param {PointerEvent} event - Pointer down event
 */
function onPointerDown(event) {
    if (!state.gameActive) {
        return;
    }

    ui.canvas.setPointerCapture(event.pointerId);
    state.drawing = true;

    const point = getCanvasCoordinates(event);
    state.lastPoint = point;
    state.currentStroke = [{ x: point.x, y: point.y, timestamp: Date.now() }];
}

/**
 * Handles pointer move on canvas
 * Draws line from last point to current point
 * Accumulates point data for stroke
 * Only active when pointer is down and game is running
 * @param {PointerEvent} event - Pointer move event
 */
function onPointerMove(event) {
    if (!state.gameActive || !state.drawing) {
        return;
    }

    const point = getCanvasCoordinates(event);
    const timestamp = Date.now();

    state.currentStroke.push({ x: point.x, y: point.y, timestamp });

    ctx.beginPath();
    ctx.moveTo(state.lastPoint.x, state.lastPoint.y);
    ctx.lineTo(point.x, point.y);
    ctx.stroke();

    state.lastPoint = point;
}

/**
 * Handles pointer up / pointer leave from canvas
 * Finalizes stroke and triggers evaluation
 * Releases pointer capture and resets drawing flag
 * @param {PointerEvent} event - Pointer up or leave event
 */
function onPointerUp(event) {
    if (!state.drawing) {
        return;
    }

    state.drawing = false;

    if (state.currentStroke.length > 0) {
        state.drawingData = state.drawingData.concat(state.currentStroke);

        const last = state.currentStroke[state.currentStroke.length - 1];
        state.drawingData.push({
            x: Math.min(CANVAS_SIZE, last.x + 100),
            y: Math.min(CANVAS_SIZE, last.y + 100),
            timestamp: Date.now(),
            strokeEnd: true
        });

        state.currentStroke = [];

        if (state.gameActive && !state.gameWon) {
            clearPendingEval();
            state.evaluationTimeoutId = setTimeout(evaluateDrawingRealtime, STROKE_EVAL_DELAY_MS);
        }
    }

    if (ui.canvas.hasPointerCapture(event.pointerId)) {
        ui.canvas.releasePointerCapture(event.pointerId);
    }
}

/**
 * Converts page coordinates to canvas coordinates
 * Accounts for canvas size and DPI scaling
 * Essential for accurate drawing across different screen sizes
 * @param {PointerEvent} event - Event with clientX, clientY coordinates
 * @returns {Object} Canvas coordinates {x, y}
 */
function getCanvasCoordinates(event) {
    const rect = ui.canvas.getBoundingClientRect();
    const scaleX = ui.canvas.width / rect.width;
    const scaleY = ui.canvas.height / rect.height;

    return {
        x: (event.clientX - rect.left) * scaleX,
        y: (event.clientY - rect.top) * scaleY
    };
}

/**
 * Clears canvas and resets drawing state
 * Updates status message and prediction label
 * Cancels any pending evaluation
 * Called on button click or 'C' keyboard shortcut
 */
function clearCanvas() {
    ctx.clearRect(0, 0, ui.canvas.width, ui.canvas.height);
    state.drawingData = [];
    state.currentStroke = [];

    if (state.gameActive) {
        resetPredictionLabel();
        setLiveStatus('Canvas cleared. Draw again.');
    }

    clearPendingEval();
}

/**
 * Evaluates drawing in real-time during gameplay
 * Debounces API calls to avoid overwhelming server
 * Automatically ends game if target is matched
 * Updates prediction display with confidence
 * @async
 */
async function evaluateDrawingRealtime() {
    if (!state.gameActive || state.gameWon || state.isEvaluating) {
        return;
    }

    if (state.drawingData.length < 10) {
        return;
    }

    const now = Date.now();
    if (now - state.lastRealtimeEvalAt < REALTIME_EVAL_MIN_INTERVAL_MS) {
        return;
    }

    state.lastRealtimeEvalAt = now;
    state.isEvaluating = true;

    try {
        const data = await recognizeDrawing();
        updatePredictionDisplay(data.prediction);

        if (normalizeLabel(data.prediction) === normalizeLabel(state.currentObject)) {
            state.gameWon = true;
            state.gameActive = false;
            clearInterval(state.timerId);
            renderImmediateSuccess(data);
            setScreen(ui.postGameScreen);
            setLiveStatus('Great job. The AI recognized your drawing early.');
        }
    } catch (error) {
        console.warn('Realtime evaluation failed:', error);
    } finally {
        state.isEvaluating = false;
    }
}

/**
 * Updates live prediction display with emoji and label
 * Called after each real-time evaluation
 * @param {string} prediction - Predicted object label
 */
function updatePredictionDisplay(prediction) {
    const label = normalizeLabel(prediction);
    const emoji = FALLBACK_EMOJIS[label] || '🤔';
    ui.predictionText.textContent = `${emoji} ${toTitleCase(label)}`;
}

/**
 * Ends active game round
 * Sends final drawing to backend for recognition
 * Displays result card with confidence and top predictions
 * Handles empty drawing and network errors gracefully
 * @async
 */
async function endGame() {
    setScreen(ui.postGameScreen);

    if (state.drawingData.length === 0) {
        setNotice(ui.modelGuess, 'error', 'No drawing detected. Try another round and sketch at least one line.');
        return;
    }

    setResultLoading(true, 'Analyzing your final drawing...');

    try {
        const data = await recognizeDrawing();
        renderResult(data);
    } catch (error) {
        console.error('Final recognition failed:', error);
        setNotice(ui.modelGuess, 'error', `Network or API error: ${error.message || 'Unknown error'}`);
    } finally {
        setResultLoading(false, '');
    }
}

/**
 * Shows or hides loading state during result evaluation
 * Updates status message in results container
 * @param {boolean} isLoading - True to show loading state
 * @param {string} message - Loading message to display
 */
function setResultLoading(isLoading, message) {
    ui.loadingResult.hidden = !isLoading;
    if (isLoading) {
        ui.modelGuess.innerHTML = '';
        ui.modelGuess.appendChild(ui.loadingResult);
        ui.loadingResult.querySelector('span:last-child').textContent = message;
    }
}

/**
 * Sends drawing to backend for AI recognition
 * Includes stroke data and target object for context
 * @async
 * @returns {Promise<Object>} Recognition result with prediction, confidence, top_predictions
 * @throws {Error} If network error or API returns error
 */
async function recognizeDrawing() {
    const payload = {
        drawing: state.drawingData,
        object: state.currentObject
    };

    const data = await fetchJson(`${API_BASE_URL}/api/recognize-drawing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (!data || data.error) {
        throw new Error(data && data.error ? data.error : 'Recognition failed.');
    }

    return data;
}

/**
 * Displays success message when object is recognized during gameplay
 * Shows before final round evaluation
 * Used for early match detection
 * @param {Object} data - Recognition data with confidence
 */
function renderImmediateSuccess(data) {
    const text = `Excellent. AI recognized ${getObjectDisplay(state.currentObject)}.`;

    const container = document.createElement('div');
    container.className = 'notice success';
    container.textContent = text;

    ui.modelGuess.innerHTML = '';
    ui.modelGuess.appendChild(container);
}

/**
 * Displays comprehensive result card with all recognition metrics
 * Shows expected vs. guessed objects with confidence
 * Lists top 3 predictions with confidence scores
 * Used for final round evaluation
 * Creates DOM elements dynamically (no innerHTML)
 * @param {Object} data - Recognition result data
 */
function renderResult(data) {
    const prediction = normalizeLabel(data.prediction);
    const target = normalizeLabel(state.currentObject);
    const isCorrect = prediction === target;
    const topPredictions = data.top_predictions || {};

    const card = document.createElement('div');
    card.className = 'result-card';
    card.classList.add(isCorrect ? 'result-correct' : 'result-try');

    const title = document.createElement('h3');
    title.className = 'result-title';
    title.textContent = isCorrect ? 'Perfect Match' : 'Good Attempt';

    const badge = document.createElement('p');
    badge.className = 'result-badge';
    badge.textContent = isCorrect
        ? 'The AI matched your target object.'
        : 'The AI guessed a different object.';

    const summary = document.createElement('p');
    summary.className = 'result-summary';
    summary.textContent = isCorrect
        ? 'Great line quality and recognizable shape. Keep the same clarity in your next round.'
        : 'Nice attempt. Emphasize the object outline and one defining detail for better recognition.';

    const grid = document.createElement('div');
    grid.className = 'result-grid';

    const expected = document.createElement('article');
    expected.className = 'result-block';
    expected.innerHTML = `<strong>You drew</strong><span>${getObjectDisplay(target)}</span>`;

    const guessed = document.createElement('article');
    guessed.className = 'result-block';
    guessed.innerHTML = `<strong>AI guessed</strong><span>${getObjectDisplay(prediction)}</span>`;

    grid.appendChild(expected);
    grid.appendChild(guessed);

    card.appendChild(title);
    card.appendChild(badge);
    card.appendChild(summary);
    card.appendChild(grid);

    const topRows = Object.entries(topPredictions).slice(0, 3);
    if (topRows.length > 0) {
        const topWrapper = document.createElement('div');
        topWrapper.className = 'result-block top-preds';
        topWrapper.innerHTML = '<strong>Top guesses</strong>';

        topRows.forEach(([label], index) => {
            const row = document.createElement('div');
            row.className = 'top-pred-row';
            row.innerHTML = `<span>${getObjectDisplay(label)}</span><span>#${index + 1}</span>`;
            topWrapper.appendChild(row);
        });

        card.appendChild(topWrapper);
    }

    ui.modelGuess.innerHTML = '';
    ui.modelGuess.appendChild(card);
}

/**
 * Resets game state and loads new target object
 * Called when user clicks "Play Again" or presses Enter on result screen
 * Clears canvas and timers, transitions back to start screen
 * @async
 */
async function restartGame() {
    clearInterval(state.timerId);
    clearPendingEval();

    state.gameActive = false;
    state.gameWon = false;
    state.isEvaluating = false;
    state.lastRealtimeEvalAt = 0;

    resetTimer();
    resetPredictionLabel();
    clearCanvas();
    await loadNewTargetObject();

    setScreen(ui.startScreen);
    setLiveStatus('New object loaded. Press Enter or Start Round.');
}

/**
 * Handles keyboard shortcuts for game control
 * 'C' key: Clear canvas during gameplay
 * 'Enter' key: Start game or restart after result
 * @param {KeyboardEvent} event - Keyboard event
 */
function handleKeyboardShortcuts(event) {
    if (event.key === 'c' || event.key === 'C') {
        if (ui.gameScreen.classList.contains('is-active')) {
            clearCanvas();
        }
        return;
    }

    if (event.key !== 'Enter') {
        return;
    }

    if (ui.startScreen.classList.contains('is-active')) {
        startGame();
    } else if (ui.postGameScreen.classList.contains('is-active')) {
        restartGame();
    }
}

/**
 * Displays error or success notice in container
 * Creates colored banner with message
 * Clears previous content
 * @param {HTMLElement} container - Element to insert notice into
 * @param {string} type - 'error' or 'success' class
 * @param {string} message - Message text to display
 */
function setNotice(container, type, message) {
    const notice = document.createElement('div');
    notice.className = `notice ${type}`;
    notice.textContent = message;

    container.innerHTML = '';
    container.appendChild(notice);
}

/**
 * Normalizes label to lowercase, trimmed string
 * Ensures consistent comparison across different inputs
 * @param {string} label - Raw label string
 * @returns {string} Normalized label
 */
function normalizeLabel(label) {
    return String(label || '').trim().toLowerCase();
}

/**
 * Converts label to title case (Capitalized Words)
 * Normalizes first, handles multi-word labels
 * @param {string} label - Raw label string
 * @returns {string} Title case label
 */
function toTitleCase(label) {
    return normalizeLabel(label)
        .split(' ')
        .filter(Boolean)
        .map((segment) => segment[0].toUpperCase() + segment.slice(1))
        .join(' ');
}

/**
 * Formats object label with emoji for display
 * Combines emoji from FALLBACK_EMOJIS with title-cased label
 * Falls back to question mark emoji if unknown
 * @param {string} label - Object label
 * @returns {string} Formatted display with emoji and label
 */
function getObjectDisplay(label) {
    const normalized = normalizeLabel(label);
    const emoji = FALLBACK_EMOJIS[normalized] || '❓';
    return `${emoji} ${toTitleCase(normalized)}`;
}

/**
 * Utility function for JSON fetch with error handling
 * Parses error responses and throws descriptive errors
 * Used for all API communication
 * @async
 * @param {string} url - Endpoint URL
 * @param {Object} [options] - Fetch options (method, headers, body, etc.)
 * @returns {Promise<Object>} Parsed JSON response
 * @throws {Error} Descriptive error with HTTP status and API error message
 */
async function fetchJson(url, options = undefined) {
    const response = await fetch(url, options);

    if (!response.ok) {
        let detail = '';

        try {
            const errorData = await response.json();
            detail = errorData.error || errorData.detail || '';
        } catch (parseError) {
            detail = '';
        }

        throw new Error(`${response.status}${detail ? `: ${detail}` : ''}`);
    }

    return response.json();
}

/**
 * Application entry point
 * Triggered when DOM is fully loaded
 * Initiates game bootstrap sequence
 */
document.addEventListener('DOMContentLoaded', bootstrap);
