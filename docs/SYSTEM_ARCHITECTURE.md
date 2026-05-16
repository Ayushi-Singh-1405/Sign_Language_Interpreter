# System Architecture & Workflow

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Streamlit/Flask Web UI                                  │   │
│  │  - Live webcam feed display                              │   │
│  │  - Real-time text output                                 │   │
│  │  - Confidence scores                                     │   │
│  │  - Control buttons (Clear, Copy, Settings)               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LOGIC LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Main Inference Pipeline                                 │   │
│  │  - Frame processing                                      │   │
│  │  - Prediction orchestration                              │   │
│  │  - Text buffering & word formation                       │   │
│  │  - Output generation                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
    ┌────────────┐    ┌──────────────┐    ┌──────────────┐
    │   Video    │    │ ML Inference │    │ Text-to-     │
    │  Capture   │    │   Module     │    │  Speech      │
    │  Module    │    │              │    │  Module      │
    └────────────┘    └──────────────┘    └──────────────┘
         ↓                    ↓
    ┌────────────┐    ┌──────────────┐
    │  OpenCV    │    │  MediaPipe   │
    │            │    │  + Classifier│
    └────────────┘    └──────────────┘
         ↓                    ↓
    ┌────────────────────────────────┐
    │      HARDWARE LAYER            │
    │  - Webcam                      │
    │  - CPU/GPU                     │
    │  - Audio Output                │
    └────────────────────────────────┘
```

## Component Architecture

### 1. Video Capture Module
**Purpose**: Acquire and preprocess video frames

```
Webcam (30 FPS)
    ↓
Frame Capture (OpenCV)
    ↓
Preprocessing:
  - Resize to 640×480
  - Flip horizontally (mirror mode)
  - Convert BGR to RGB
    ↓
Frame Queue (Buffer)
```

**Key Functions**:
- `capture_frame()`: Get frame from webcam
- `preprocess_frame()`: Resize, flip, color convert
- `get_frame_rate()`: Monitor FPS

### 2. Hand Detection Module
**Purpose**: Extract hand landmarks from frames

```
Preprocessed Frame
    ↓
MediaPipe Hands Detector
    ↓
Detection Results:
  - Hand presence (confidence)
  - 21 landmark coordinates (x, y, z)
  - Handedness (left/right)
    ↓
Landmark Validation:
  - Check confidence > 0.7
  - Verify all 21 points detected
    ↓
Normalized Landmarks
```

**Key Functions**:
- `detect_hand()`: Run MediaPipe inference
- `extract_landmarks()`: Get 21 keypoints
- `validate_detection()`: Check quality

### 3. Feature Extraction Module
**Purpose**: Convert landmarks to ML-ready features

```
Raw Landmarks (21 points × 3 coords = 63 values)
    ↓
Normalization:
  - Subtract wrist position (landmark 0)
  - Scale by hand size
    ↓
Feature Vector (42 dimensions):
  - 21 landmarks × 2 coordinates (x, y)
  - Z-coordinate discarded for simplicity
    ↓
Feature Array [x1, y1, x2, y2, ..., x21, y21]
```

**Key Functions**:
- `normalize_landmarks()`: Center at wrist
- `extract_features()`: Create feature vector
- `scale_features()`: Normalize range

### 4. Classification Module
**Purpose**: Predict letter from features

```
Feature Vector (42 dims)
    ↓
Load Trained Model (Random Forest)
    ↓
Prediction:
  - Forward pass through model
  - Get predicted class (A-Z)
  - Get confidence scores
    ↓
Output:
  - Predicted letter
  - Confidence (0-1)
  - Top-3 alternatives
```

**Key Functions**:
- `load_model()`: Load .pkl file
- `predict()`: Get letter prediction
- `get_confidence()`: Extract probability

### 5. Stability Module
**Purpose**: Reduce jitter and false positives

```
Prediction Stream: [A, A, B, B, B, A, A, A, A, A, ...]
    ↓
Stability Check:
  - Count consecutive same predictions
  - Require N frames (typically 15-20)
  - Check confidence > threshold (0.85)
    ↓
Stable Prediction: Only output when criteria met
    ↓
Output: [A (stable), B (stable), A (stable)]
```

**Key Functions**:
- `check_stability()`: Validate prediction
- `update_counter()`: Track consecutive frames
- `reset_counter()`: Reset on change

### 6. Text Processing Module
**Purpose**: Build words from letters

```
Stable Predictions: [A, B, C, ...]
    ↓
Word Buffer Management:
  - Append letter to buffer
  - Detect space gesture → confirm word
  - Detect delete gesture → remove char
    ↓
Word Formation:
  - "A" + "B" + "C" = "ABC"
  - Space detected → Add to word list
  - Buffer reset
    ↓
Output: Complete words + current buffer
```

**Key Functions**:
- `append_letter()`: Add to buffer
- `detect_space()`: Recognize space gesture
- `detect_delete()`: Recognize delete gesture
- `form_word()`: Finalize word

### 7. Output Module
**Purpose**: Display results and generate speech

```
Recognized Text
    ↓
Display Output:
  - Show on screen
  - Update UI
  - Log to file
    ↓
Text-to-Speech:
  - Convert text to speech
  - Play audio
  - Optional: Save to file
    ↓
User Feedback:
  - Visual confirmation
  - Audio confirmation
```

**Key Functions**:
- `display_text()`: Show on screen
- `speak_text()`: Generate speech
- `log_output()`: Save to file

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      REAL-TIME INFERENCE LOOP                    │
└─────────────────────────────────────────────────────────────────┘

START
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 1. CAPTURE FRAME                                                 │
│    - Read from webcam                                            │
│    - Preprocess (resize, flip, color convert)                   │
└─────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. DETECT HAND                                                   │
│    - Run MediaPipe inference                                     │
│    - Extract 21 landmarks                                        │
│    - Validate detection (confidence > 0.7)                       │
└─────────────────────────────────────────────────────────────────┘
  ↓
  ├─ Hand NOT detected?
  │  └─ Display "No hand detected"
  │     └─ Go to DISPLAY & LOOP
  │
  └─ Hand detected?
     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. EXTRACT FEATURES                                              │
│    - Normalize landmarks (subtract wrist)                        │
│    - Create feature vector (42 dims)                             │
└─────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. CLASSIFY                                                      │
│    - Load model                                                  │
│    - Predict letter (A-Z)                                        │
│    - Get confidence score                                        │
└─────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. CHECK STABILITY                                               │
│    - Compare with previous prediction                            │
│    - Count consecutive frames                                    │
│    - Verify confidence > 0.85                                    │
└─────────────────────────────────────────────────────────────────┘
  ↓
  ├─ Prediction stable (N frames)?
  │  └─ YES: Append to word buffer
  │         └─ Check for space/delete gesture
  │            └─ Update word buffer
  │
  └─ NO: Continue counting
     └─ Display current prediction (not yet added)
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. DISPLAY & OUTPUT                                              │
│    - Show frame with skeleton overlay                            │
│    - Display current prediction                                  │
│    - Show confidence score                                       │
│    - Display word buffer                                         │
│    - Trigger TTS if word completed                               │
└─────────────────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. CHECK EXIT CONDITION                                          │
│    - User pressed 'Q' to quit?                                   │
└─────────────────────────────────────────────────────────────────┘
  ↓
  ├─ YES: CLEANUP & EXIT
  │  └─ Release webcam
  │     └─ Close windows
  │        └─ END
  │
  └─ NO: LOOP (Go to step 1)
```

## Workflow Phases

### Phase 1: Data Collection (Week 2)
```
Manual Gesture Input
    ↓
Capture Landmarks
    ↓
Label with Letter (A-Z)
    ↓
Save to CSV
    ↓
Repeat 250 times per letter
    ↓
Final Dataset: 6,500+ rows
```

### Phase 2: Model Training (Week 3)
```
Load CSV Data
    ↓
Split Train/Test (80/20)
    ↓
Train Random Forest
    ↓
Evaluate on Test Set
    ↓
Generate Confusion Matrix
    ↓
Save Model (.pkl)
```

### Phase 3: Real-Time Inference (Week 4)
```
Load Trained Model
    ↓
Start Webcam Loop
    ↓
For each frame:
  - Detect hand
  - Extract features
  - Predict letter
  - Check stability
  - Update buffer
    ↓
Display Results
```

### Phase 4: UI & Integration (Week 5)
```
Build Streamlit UI
    ↓
Integrate inference pipeline
    ↓
Add TTS module
    ↓
Add control buttons
    ↓
Test end-to-end
```

## State Machine

```
┌──────────────────────────────────────────────────────────────┐
│                    SYSTEM STATE MACHINE                       │
└──────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   IDLE STATE    │
                    │ (Waiting for    │
                    │  hand input)    │
                    └────────┬────────┘
                             │
                    Hand detected?
                             │
                    ┌────────▼────────┐
                    │ DETECTION STATE │
                    │ (Extracting     │
                    │  landmarks)     │
                    └────────┬────────┘
                             │
                    Landmarks valid?
                             │
                    ┌────────▼────────┐
                    │ PREDICTION STATE│
                    │ (Classifying    │
                    │  gesture)       │
                    └────────┬────────┘
                             │
                    Confidence > 0.85?
                             │
                    ┌────────▼────────┐
                    │ STABILITY STATE │
                    │ (Counting       │
                    │  frames)        │
                    └────────┬────────┘
                             │
                    N frames same?
                             │
                    ┌────────▼────────┐
                    │ CONFIRMED STATE │
                    │ (Add to buffer) │
                    └────────┬────────┘
                             │
                    Space gesture?
                             │
                    ┌────────▼────────┐
                    │ WORD COMPLETE   │
                    │ (Trigger TTS)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   IDLE STATE    │
                    │ (Reset buffer)  │
                    └─────────────────┘
```

## Performance Metrics

### Latency Breakdown (per frame)
```
Frame Capture:        ~5ms
Hand Detection:       ~30ms (MediaPipe)
Feature Extraction:   ~2ms
Classification:       ~5ms (Random Forest)
Stability Check:      ~1ms
Display/Output:       ~10ms
─────────────────────────
Total:                ~53ms (well under 100ms target)
```

### Memory Usage
```
Model Size:           ~50MB (Random Forest)
Frame Buffer:         ~10MB (few frames)
Runtime Variables:    ~50MB
─────────────────────────
Total:                ~110MB (well under 500MB target)
```

### Accuracy Metrics
```
Training Accuracy:    ~96%
Test Accuracy:        ~93-95%
Per-Letter Accuracy:  85-99% (varies by letter)
Confusion Rate:       M/N/T most confused (~5-10%)
```
