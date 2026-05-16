# Sign Language Interpreter

Real-time ASL (American Sign Language) gesture recognition system that translates hand gestures into text and speech in real-time.

## Overview

This project bridges communication between deaf and hearing individuals by recognizing 26 ASL alphabets (A-Z) using computer vision and machine learning. The system processes video at 30 FPS with 93-96% accuracy on a standard laptop CPU.

## Key Features

- Real-time letter recognition (A-Z)
- Word builder with space/delete gestures
- Text-to-speech output
- Live webcam display with hand skeleton overlay
- Confidence score display
- Modern web UI (HTML/CSS/JS + Flask backend)

## Quick Stats

| Metric | Value |
|--------|-------|
| ASL Alphabets | 26 (A-Z) |
| Hand Landmarks | 21 per hand |
| Target Accuracy | ≥93% |
| Processing Speed | 30 FPS |
| Latency | <100ms per frame |
| Hardware Required | Standard laptop (no GPU) |
| Development Time | 6 weeks |

## Technology Stack

- **Language**: Python 3.8+
- **Hand Detection**: MediaPipe 0.8+
- **Video Processing**: OpenCV 4.5+
- **ML Classifier**: scikit-learn 1.0+
- **Backend**: Flask 2.0+
- **Web UI**: HTML5/CSS3/JavaScript
- **Text-to-Speech**: pyttsx3 2.90+
- **Data Processing**: NumPy, Pandas

## Project Structure

```
sign_language_interpreter/
├── .gitignore
├── README.md
├── requirements.txt
├── hand_landmarker.task           # MediaPipe hand detection model
├── server.py                      # Flask backend server
│
├── docs/
│   ├── DOCUMENTATION_SUMMARY.md
│   ├── ERROR_LOG.md
│   ├── INDEX.md
│   ├── PROBLEM_STATEMENT.md
│   ├── PROJECT_DOCUMENTATION.md
│   ├── REQUIREMENTS.md
│   ├── SYSTEM_ARCHITECTURE.md
│   └── WORKFLOW.md
│
├── src/
│   ├── __init__.py
│   ├── detector.py                # Hand detection module
│   ├── classifier.py              # Letter classification module
│   ├── collector.py              # Data collection module
│   ├── train.py                  # Model training script
│   ├── app.py                    # Legacy Streamlit app
│   ├── streamlit_app.py           # Streamlit UI
│   └── index.html                 # Modern HTML UI
│
├── data/                          # Dataset (not pushed to git)
│   └── asl-alphabet/              # Extracted ASL alphabet images
│
└── venv/                         # Virtual environment (not pushed)
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Webcam
- 500MB free disk space

### Installation

1. Clone the repository:
```bash
git clone https://gitlab.com/ayushisingh10c/sign_language_interpreter.git
cd sign_language_interpreter
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

**Flask Backend (Modern UI):**
```bash
python server.py
```
Access at `http://localhost:5000`

**Streamlit (Legacy UI):**
```bash
streamlit run src/streamlit_app.py
```
Access at `http://localhost:8501`

## Development Roadmap

### Phase 1: Environment Setup (Week 1)
- Install Python and dependencies
- Set up MediaPipe hand detection
- Deliverable: Live webcam with hand skeleton

### Phase 2: Data Collection (Week 2)
- Collect 250 samples per letter (A-Z)
- Normalize and validate data
- Deliverable: 6,500+ labeled samples (CSV)

### Phase 3: Model Training (Week 3)
- Train Random Forest classifier
- Evaluate on test set
- Deliverable: Trained classifier (.pkl)

### Phase 4: Real-Time Inference (Week 4)
- Integrate model into webcam loop
- Implement stability check
- Deliverable: Live sign-to-text system

### Phase 5: UI & Integration (Week 5)
- Build Streamlit interface
- Integrate text-to-speech
- Deliverable: Full web application

### Phase 6: Polish & Documentation (Week 6)
- Record demo video
- Write project report
- Deliverable: Complete project package

## System Architecture

### High-Level Flow

```
Webcam Feed (30 FPS)
    ↓
Hand Detection (MediaPipe - 21 landmarks)
    ↓
Feature Extraction (Normalize coordinates)
    ↓
ML Classifier (Random Forest)
    ↓
Stability Check (15+ frames)
    ↓
Text Output + Text-to-Speech
```

### Key Components

1. **Video Capture Module**: Captures frames from webcam
2. **Hand Detection Module**: Extracts 21 hand landmarks using MediaPipe
3. **Feature Extraction Module**: Normalizes landmarks into feature vectors
4. **Classification Module**: Predicts letter using Random Forest
5. **Stability Module**: Reduces jitter with frame-based validation
6. **Text Processing Module**: Buffers letters into words
7. **Output Module**: Displays text and generates speech


## Datasets

- **ASL Alphabet (Kaggle)**: 87,000 images for baseline training
- **Custom Collection**: 6,500+ landmark samples for your specific conditions
- **WLASL**: 21,083 videos for advanced word-level recognition
- **MS-ASL**: 25,000 videos for large-scale training

## Usage

### Basic Usage

1. Run the application:
```bash
streamlit run app.py
```

2. Position your hand in front of the webcam
3. Perform ASL gestures
4. Recognized letters appear in real-time
5. Use space gesture to confirm words
6. Use delete gesture to remove characters

### Keyboard Shortcuts

- `Q`: Quit application
- `C`: Clear text buffer
- `S`: Copy to clipboard

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Similar letter shapes (M/N/T) | Collect more data for confusing letters |
| Lighting variations | Normalize features, test in different conditions |
| Hand size variations | Normalize by hand size during feature extraction |
| Jitter in predictions | Implement stability check (15+ frame threshold) |
| Latency | Use Random Forest instead of deep learning |

## Testing

### Unit Tests
```bash
pytest tests/
```

### Performance Tests
- FPS measurement
- Latency profiling
- Memory usage monitoring

## Deployment

### Local Deployment
```bash
python app.py
```

### Web Deployment
```bash
streamlit run app.py
```

### Docker Deployment
```bash
docker build -t sign-interpreter .
docker run -p 8501:8501 sign-interpreter
```

## Further Enhancements

- Word-level recognition using LSTM
- Multi-hand support
- Mobile app (Flutter/React Native)
- Multi-language text-to-speech
- Avatar animation for hearing to deaf communication
- Cloud deployment (AWS/GCP)
- Accessibility features (high contrast, adjustable text size)

## Documentation

Complete documentation is available:

- **[INDEX.md](INDEX.md)** - Documentation index and navigation
- **[PROBLEM_STATEMENT.md](PROBLEM_STATEMENT.md)** - Problem definition and solution
- **[REQUIREMENTS.md](REQUIREMENTS.md)** - Functional and non-functional requirements
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - System design and architecture
- **[WORKFLOW.md](WORKFLOW.md)** - Implementation workflows and processes
- **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)** - Complete project reference
- **[DOCUMENTATION_SUMMARY.md](DOCUMENTATION_SUMMARY.md)** - Documentation overview


## License

This project is open-source and available under the MIT License.

## Acknowledgments

- MediaPipe for hand detection framework
- OpenCV for video processing
- scikit-learn for machine learning
- Streamlit for web UI framework
- ASL community for inspiration and datasets

- Documentation: See [INDEX.md](INDEX.md)

## Project Status

Status: In Development
Version: 1.0
Last Updated: April 16, 2026

---

**Real-time ASL gesture recognition for accessible communication**
