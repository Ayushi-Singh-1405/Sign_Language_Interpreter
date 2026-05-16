"""
Sign Language Interpreter - Flask Backend
Serves HTML UI and processes hand detection via API
"""

import cv2
import numpy as np
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import io
import threading
import queue
import os
import tempfile

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from src.detector import HandDetector
from src.classifier import ASLClassifier

app = Flask(__name__, template_folder=".", static_folder=".")
CORS(app)

detector = None
classifier = None
frame_queue = queue.Queue(maxsize=2)
result_queue = queue.Queue(maxsize=2)
processing = False


def get_detector():
    global detector
    if detector is None:
        detector = HandDetector()
    return detector


def get_classifier():
    global classifier
    if classifier is None:
        classifier = ASLClassifier()
        classifier.load_model()
    return classifier


class DetectionProcessor:
    def __init__(self):
        self.detector = get_detector()
        self.classifier = get_classifier()
        self.current_result = {
            "letter": "-",
            "confidence": 0.0,
            "landmarks": [],
            "detected": False,
        }
        self.lock = threading.Lock()
        self.running = False

    def process_loop(self):
        global processing
        while self.running:
            try:
                frame = frame_queue.get(timeout=0.1)
                result = self.detector.detect(frame)
                landmarks = self.detector.get_landmarks(result)

                with self.lock:
                    if landmarks:
                        self.current_result["detected"] = True
                        self.current_result["landmarks"] = [
                            {"x": lm.x, "y": lm.y, "z": getattr(lm, "z", 0)}
                            for lm in landmarks
                        ]
                        features = self.detector.extract_features(landmarks)
                        self.current_result["features"] = (
                            features.tolist() if features is not None else []
                        )

                        if features is not None:
                            letter, confidence = self.classifier.predict(features)
                            if letter:
                                self.current_result["letter"] = letter
                                self.current_result["confidence"] = float(confidence)
                            else:
                                self.current_result["letter"] = "-"
                                self.current_result["confidence"] = 0.0
                    else:
                        self.current_result["detected"] = False
                        self.current_result["landmarks"] = []
                        self.current_result["features"] = []
                        self.current_result["letter"] = "-"
                        self.current_result["confidence"] = 0.0

                if not result_queue.full():
                    with self.lock:
                        result_queue.put(self.current_result.copy())

            except queue.Empty:
                continue

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.process_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def get_result(self):
        with self.lock:
            return self.current_result.copy()


processor = DetectionProcessor()


@app.route("/")
def index():
    return send_from_directory("src", "index.html")


@app.route("/api/detect", methods=["POST"])
def detect():
    global processor, processing

    if not processing:
        processor.start()
        processing = True

    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    try:
        image_data = (
            data["image"].split(",")[1] if "," in data["image"] else data["image"]
        )
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "Invalid image"}), 400

        if frame_queue.full():
            try:
                frame_queue.get_nowait()
            except queue.Empty:
                pass
        frame_queue.put(frame)

        if not result_queue.empty():
            result = result_queue.get()
            return jsonify(result)

        return jsonify({"detected": False, "letter": "-", "confidence": 0.0})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stop", methods=["POST"])
def stop():
    global processor, processing
    processor.stop()
    processing = False
    return jsonify({"status": "stopped"})


@app.route("/api/annotate", methods=["POST"])
def annotate():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image provided"}), 400

    try:
        image_data = (
            data["image"].split(",")[1] if "," in data["image"] else data["image"]
        )
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({"error": "Invalid image"}), 400

        det = get_detector()
        result = det.detect(frame)
        landmarks = det.get_landmarks(result)

        annotated = det.draw_hand(frame, landmarks)

        _, buffer = cv2.imencode(".jpg", annotated)
        jpg_as_text = base64.b64encode(buffer).decode()

        letter = "-"
        confidence = 0.0
        if landmarks:
            features = det.extract_features(landmarks)
            clf = get_classifier()
            if features is not None:
                letter, confidence = clf.predict(features)
                letter = letter if letter else "-"
                confidence = float(confidence) if confidence else 0.0

                h, w = annotated.shape[:2]
                cv2.putText(
                    annotated,
                    f"{letter} {confidence * 100:.0f}%",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 255, 0),
                    3,
                )

        _, buffer = cv2.imencode(".jpg", annotated)
        jpg_as_text = base64.b64encode(buffer).decode()

        return jsonify(
            {
                "annotated_image": f"data:image/jpeg;base64,{jpg_as_text}",
                "detected": landmarks is not None,
                "letter": letter,
                "confidence": confidence,
            }
        )

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500


@app.route("/api/speak", methods=["POST"])
def speak():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data["text"]
        if not text:
            return jsonify({"error": "Empty text"}), 400

        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            return jsonify({"status": "spoken", "text": text})
        except Exception as tts_err:
            print(f"TTS Error: {tts_err}")
            return jsonify({"error": str(tts_err)}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting Sign Language Interpreter...")
    print("Open http://localhost:5000 in your browser")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
