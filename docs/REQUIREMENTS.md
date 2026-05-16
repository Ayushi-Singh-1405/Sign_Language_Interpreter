# Requirements

## Functional Requirements

### FR1: Hand Detection
- System shall detect hand(s) in real-time from webcam feed
- System shall extract 21 hand landmarks (keypoints) per detected hand
- System shall handle single hand detection with confidence threshold ≥0.7

### FR2: Gesture Recognition
- System shall recognize all 26 ASL alphabets (A-Z)
- System shall classify gestures with accuracy ≥93%
- System shall provide confidence scores for predictions

### FR3: Real-Time Processing
- System shall process video at 30 FPS minimum
- System shall maintain latency <100ms per frame
- System shall work on standard laptop CPU without GPU

### FR4: Text Output
- System shall buffer recognized letters into words
- System shall support space gesture to confirm words
- System shall support delete/backspace gesture to remove characters
- System shall display recognized text on screen

### FR5: Text-to-Speech
- System shall convert recognized text to speech
- System shall support offline TTS (pyttsx3)
- System shall speak complete words when space gesture is detected

### FR6: User Interface
- System shall display live webcam feed with hand skeleton overlay
- System shall show current prediction and confidence score
- System shall display word buffer in real-time
- System shall provide clear, intuitive controls

## Non-Functional Requirements

### NFR1: Performance
- **Accuracy**: ≥93% on test dataset
- **Latency**: <100ms per frame inference
- **Throughput**: 30 FPS minimum
- **Memory**: <500MB RAM usage

### NFR2: Compatibility
- **OS**: Linux, Windows, macOS
- **Python**: 3.8+
- **Hardware**: Standard laptop with webcam (no GPU required)

### NFR3: Usability
- **Learning Curve**: Intuitive for non-technical users
- **Setup Time**: <5 minutes for installation
- **Accessibility**: Clear visual feedback and audio output

### NFR4: Reliability
- **Robustness**: Works across different lighting conditions
- **Stability**: Handles variable hand sizes and positions
- **Error Handling**: Graceful degradation when hand not detected

### NFR5: Maintainability
- **Code Quality**: Well-documented, modular code
- **Testing**: Unit tests for core components
- **Deployment**: Easy to package and distribute

## Data Requirements

### DR1: Training Data
- **Size**: 6,500+ labeled samples (250 per letter × 26 letters)
- **Format**: CSV with 42 features (21 landmarks × 2 coordinates) + label
- **Source**: Custom collection + Kaggle ASL Alphabet dataset

### DR2: Model Requirements
- **Type**: Random Forest Classifier (primary) or LSTM (advanced)
- **Input**: Normalized hand landmark coordinates
- **Output**: Predicted letter (A-Z) with confidence score

## Technical Stack

### Core Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| Python | 3.8+ | Programming language |
| MediaPipe | 0.8+ | Hand detection & landmark extraction |
| OpenCV | 4.5+ | Video capture & frame processing |
| scikit-learn | 1.0+ | Random Forest classifier |
| NumPy | 1.20+ | Numerical computations |
| Pandas | 1.3+ | Data handling |
| TensorFlow | 2.8+ | LSTM (optional, advanced) |
| Streamlit | 1.10+ | Web UI |
| pyttsx3 | 2.90+ | Text-to-speech |

### Development Tools
- Git for version control
- Jupyter Notebook for experimentation
- Matplotlib/Seaborn for visualization
- pytest for unit testing

## System Architecture

### Components

1. **Video Capture Module**
   - Captures frames from webcam at 30 FPS
   - Handles frame preprocessing (resize, flip)

2. **Hand Detection Module**
   - Uses MediaPipe Hands for landmark detection
   - Extracts 21 keypoints per hand
   - Filters detections by confidence threshold

3. **Feature Extraction Module**
   - Normalizes landmark coordinates
   - Subtracts wrist position for invariance
   - Generates feature vectors (42 dimensions)

4. **Classification Module**
   - Loads trained ML model
   - Predicts letter from feature vector
   - Returns prediction + confidence score

5. **Stability Module**
   - Implements frame-based stability check
   - Requires N consecutive frames of same prediction
   - Prevents jitter and false positives

6. **Text Processing Module**
   - Buffers recognized letters
   - Handles space and delete gestures
   - Manages word formation

7. **Output Module**
   - Displays text on screen
   - Triggers text-to-speech
   - Provides visual feedback

## Constraints

- **Single Hand**: System detects only one hand at a time
- **Lighting**: Requires adequate lighting (>200 lux)
- **Distance**: Hand must be 30-100cm from camera
- **Background**: Works best with non-cluttered backgrounds
- **Gesture Duration**: Each gesture must be held for 15+ frames

## Success Criteria

- [ ] Achieves ≥93% accuracy on test set
- [ ] Processes video at 30 FPS
- [ ] Latency <100ms per frame
- [ ] Works on standard laptop CPU
- [ ] Intuitive UI with clear feedback
- [ ] Handles all 26 ASL alphabets
- [ ] Text-to-speech functional
- [ ] Comprehensive documentation
- [ ] Demo video recorded
- [ ] Viva presentation ready

## Future Enhancements

1. **Word-Level Recognition**: LSTM on video sequences
2. **Multi-Hand Support**: Detect both hands simultaneously
3. **Mobile Deployment**: Flutter/React Native app
4. **Multi-Language TTS**: Support for Hindi, Telugu, Tamil
5. **Two-Way Communication**: Avatar animation for hearing→deaf
6. **Cloud Deployment**: AWS/GCP for scalability
7. **Accessibility Features**: High contrast mode, adjustable text size
