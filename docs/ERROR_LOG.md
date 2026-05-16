# Error Log - Sign Language Interpreter

## Overview
This log tracks all issues, errors, and bugs encountered during development.

---

## Session 1: Environment Setup

### Date: April 15, 2026

### Issue 1: Dependencies Not System-Installed
**Error:**
```
ModuleNotFoundError: No module named 'mediapipe'
```

**Cause:** Python packages not installed system-wide on externally-managed environment.

**Solution:** Created virtual environment and installed dependencies:
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

---

### Issue 2: MediaPipe API Change - Missing `solutions` Module
**Error:**
```
AttributeError: module 'mediapipe' has no attribute 'solutions'
```

**Cause:** MediaPipe 0.10.33 uses a new API structure. The old `mediapipe.solutions.hands` is no longer available.

**Attempted Solutions:**
- Tried `from mediapipe import solutions` - failed
- Tried installing older version (`mediapipe==0.10.9`) - not available (only 0.10.30-0.10.33)

**Solution:** Updated code to use new Tasks API:
```python
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
```

---

### Issue 3: Missing Hand Landmark Model
**Error:** Code required `hand_landmarker.task` model file.

**Solution:** Downloaded model:
```bash
wget https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

---

### Issue 4: Wrong Running Mode
**Error:**
```
ValueError: Task is not initialized with the image mode. Current running mode: live stream mode
```

**Cause:** Used `RunningMode.LIVE_STREAM` with `detect()` method instead of `detect_for_video()`.

**Solution:** Changed to `RunningMode.VIDEO` with `detect_for_video()`:
```python
options = vision.HandLandmarkerOptions(
    running_mode=vision.RunningMode.VIDEO
)
result = detector.detect_for_video(mp_image, frame_idx)
```

---

### Issue 5: Missing `Image` Class
**Error:**
```
AttributeError: module 'mediapipe.tasks.python.vision' has no attribute 'Image'
```

**Cause:** Used wrong module for `mp.Image`.

**Solution:**
```python
import mediapipe as mp  # For mp.Image
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
```

---

### Issue 6: Missing `HAND_CONNECTIONS` Constant
**Error:**
```
AttributeError: type object 'HandLandmarker' has no attribute 'HAND_CONNECTIONS'
```

**Cause:** `HandLandmarker.HAND_CONNECTIONS` doesn't exist in new API.

**Attempted Solution:** Tried importing from different modules - all failed.

**Solution:** Defined connections manually:
```python
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]
```

---

### Issue 7: `draw_landmarks()` API Incompatibility
**Error:**
```
AttributeError: 'tuple' object has no attribute 'start'
```

**Cause:** `mp_drawing.draw_landmarks()` expects objects with `.start` and `.end` attributes, not tuples.

**Solution:** Created custom drawing function using OpenCV:
```python
def draw_hand(frame, landmarks, connections):
    h, w = frame.shape[:2]
    for landmark in landmarks:
        x = int(landmark.x * w)
        y = int(landmark.y * h)
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
    
    for start, end in connections:
        start_pt = (int(landmarks[start].x * w), int(landmarks[start].y * h))
        end_pt = (int(landmarks[end].x * w), int(landmarks[end].y * h))
        cv2.line(frame, start_pt, end_pt, (0, 255, 0), 2)
```

---

## Key Learnings

1. **MediaPipe 0.10.x has breaking API changes** - The Tasks API is now the primary interface
2. **Drawing utilities may not work** - Custom OpenCV drawing often more reliable
3. **Model file required** - Must download `.task` file separately
4. **Running modes matter** - VIDEO mode for webcam, IMAGE mode for single images

---

## Warnings (Non-Critical)

These warnings appear but don't affect functionality:
- `QFontDatabase: Cannot find font directory` - OpenCV font issue (cosmetic)
- `Using NORM_RECT without IMAGE_DIMENSIONS` - MediaPipe internal warning
- `Feedback manager requires a model with a single signature` - MediaPipe internal warning
- `XDG_SESSION_TYPE=wayland` - Display server warning

---

## Status: Phase 1 Complete ✓

Hand detector working with:
- 21 landmarks detected
- Connection lines drawn
- 30 FPS webcam feed

---

## Session 2: UI Development

### Date: April 15, 2026

### Files Created:
1. `src/app.py` - Basic Streamlit UI structure
2. `src/streamlit_app.py` - Full Streamlit application with:
   - Live camera placeholder
   - Word buffer display
   - Control buttons (Start, Stop, Speak, Clear)
   - Confidence display
   - ASL alphabet reference
   - Instructions panel

### Streamlit Running:
- Local: http://localhost:8501
- Network: http://192.168.0.6:8501

### To Run UI:
```bash
source venv/bin/activate
streamlit run src/streamlit_app.py
```

### UI Features:
- Two-column layout (video + output)
- Real-time word buffer
- Text-to-speech integration (pyttsx3)
- Clear/copy controls
- ASL alphabet quick reference
- Help/instructions panel

### UI Still Needs:
- Integration with hand_detector.py
- Real-time video feed display
- Actual prediction display
- Confidence score updates

---

## Session 3: HTML UI + Flask Backend

### Date: April 16, 2026

### Issue 8: Streamlit-WebRTC Import Error
**Error:**
```
ImportError: cannot import name 'VideoTransformConfig' from 'streamlit_webrtc'
```

**Cause:** `VideoTransformConfig` doesn't exist in the installed version of streamlit-webrtc.

**Solution:** Removed unused import:
```python
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
```

---

### Issue 9: Streamlit Camera Not Working
**Error:** Camera stream not displaying in browser (streamlit-webrtc unreliable)

**Solution:** Switched to Flask + HTML frontend approach for better browser compatibility.

**New Architecture:**
- `server.py` - Flask backend serving HTML UI and handling detection
- `src/index.html` - Frontend with modern UI
- `src/streamlit_app.py` - Deprecated (kept for reference)

---

### Issue 10: Flask 404 for index.html
**Error:**
```
Failed to load resource: the server responded with a status of 404 (NOT FOUND)
Camera error: TypeError: Cannot read properties of undefined (reading 'getUserMedia')
```

**Cause:** Flask's `render_template()` looking for template in wrong path.

**Solution:** Used `send_from_directory()` instead:
```python
from flask import send_from_directory

@app.route("/")
def index():
    return send_from_directory("src", "index.html")
```

---

### Issue 11: Camera Access Blocked
**Error:** `getUserMedia` undefined / camera access denied

**Cause:** Browser requires HTTPS or localhost for camera access.

**Solution:** Access via `http://localhost:5000` (not `0.0.0.0` or other URLs).

---

## Architecture Update

### New Components:
- `server.py` - Flask backend (API endpoints for detection)
- `src/index.html` - Modern HTML/CSS/JS UI

### Running the App:
```bash
source venv/bin/activate
python server.py
```
Open: http://localhost:5000

### API Endpoints:
- `POST /api/annotate` - Returns annotated frame with landmarks
- `POST /api/detect` - Returns detection results
- `POST /api/stop` - Stops detection processor

### Dependencies Added:
```
flask>=2.0.0
flask-cors>=3.0.0
```

---

## Status: Phase 2 Complete ✓

UI-Detector integration working:
- Modern HTML UI served via Flask
- Camera access via WebRTC (getUserMedia)
- Hand detection and landmark rendering
- Real-time FPS display

**Still Needed:**
- Classifier model training
- Letter prediction display
- Word buffer logic
