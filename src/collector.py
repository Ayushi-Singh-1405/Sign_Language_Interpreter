"""
Sign Language Interpreter - Data Collector
Collects hand landmark samples for training
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import pandas as pd
import os
import math

HAND_CONNECTIONS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (0, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (0, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (5, 9),
    (9, 13),
    (13, 17),
]

FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_MCP = [1, 5, 9, 13, 17]
FINGER_PIP = [2, 6, 10, 14, 18]


def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return math.acos(np.clip(cos_angle, -1, 1)) * 180 / math.pi


def calculate_distance(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


class DataCollector:
    def __init__(
        self, model_path="hand_landmarker.task", output_path="data/landmarks.csv"
    ):
        self.model_path = model_path
        self.output_path = output_path
        self.samples = []

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            running_mode=vision.RunningMode.VIDEO,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.frame_idx = 0

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect_for_video(mp_image, self.frame_idx)
        self.frame_idx += 1
        return result

    def get_landmarks(self, result):
        if result.hand_landmarks:
            return result.hand_landmarks[0]
        return None

    def extract_features(self, landmarks):
        if landmarks is None:
            return None

        wrist = landmarks[0]
        wrist_x, wrist_y = wrist.x, wrist.y

        features = []
        for lm in landmarks:
            features.append(lm.x - wrist_x)
            features.append(lm.y - wrist_y)
            features.append(getattr(lm, "z", 0))

        palm_width = calculate_distance(landmarks[0], landmarks[17])
        features.append(palm_width)

        for i in range(5):
            tip = landmarks[FINGER_TIPS[i]]
            mcp = landmarks[FINGER_MCP[i]]
            pip = landmarks[FINGER_PIP[i]]
            features.append(calculate_distance(tip, mcp))
            if i < 4:
                features.append(calculate_angle(mcp, pip, tip))

        for i in range(4):
            tip_curr = landmarks[FINGER_TIPS[i]]
            tip_next = landmarks[FINGER_TIPS[i + 1]]
            features.append(calculate_distance(tip_curr, tip_next))

        thumb_tip = landmarks[4]
        index_mcp = landmarks[5]
        features.append(calculate_distance(thumb_tip, index_mcp))

        finger_curls = []
        for i in range(5):
            tip = landmarks[FINGER_TIPS[i]]
            pip = landmarks[FINGER_PIP[i]]
            curl = calculate_distance(tip, pip)
            finger_curls.append(curl)
        mean_curl = np.mean(finger_curls)
        features.append(mean_curl)
        features.append(np.std(finger_curls))

        return features

    def draw_hand(self, frame, landmarks):
        if landmarks is None:
            return frame

        h, w = frame.shape[:2]

        for i, landmark in enumerate(landmarks):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            color = (0, 255, 0) if i == 0 else (0, 200, 0)
            cv2.circle(frame, (x, y), 6 if i == 0 else 4, color, -1)

        for start, end in HAND_CONNECTIONS:
            start_pt = (int(landmarks[start].x * w), int(landmarks[start].y * h))
            end_pt = (int(landmarks[end].x * w), int(landmarks[end].y * h))
            cv2.line(frame, start_pt, end_pt, (0, 200, 0), 2)

        return frame

    def add_sample(self, features, label):
        features.append(label)
        self.samples.append(features)

    def save_data(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df = pd.DataFrame(self.samples)
        df.to_csv(self.output_path, index=False)
        print(f"Saved {len(self.samples)} samples to {self.output_path}")


def main():
    print("=" * 50)
    print("ASL Data Collector")
    print("=" * 50)
    print("Instructions:")
    print("- Press A-Z to select the letter to collect")
    print("- Press SPACE to capture 50 samples (hold hand steady)")
    print("- Press S to save data and quit")
    print("- Press Q to quit without saving")
    print("=" * 50)

    collector = DataCollector()
    current_letter = "A"

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        result = collector.detect(frame)
        landmarks = collector.get_landmarks(result)
        frame = collector.draw_hand(frame, landmarks)

        cv2.putText(
            frame,
            f"Letter: {current_letter}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            f"Samples: {len(collector.samples)}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            frame,
            "SPACE: Capture 50 | S: Save | Q: Quit",
            (10, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1,
        )

        if landmarks:
            cv2.putText(
                frame,
                "Hand Detected!",
                (frame.shape[1] - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Data Collector", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("s"):
            collector.save_data()
            break
        elif key == 32:
            captured = 0
            for _ in range(50):
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.flip(frame, 1)
                result = collector.detect(frame)
                landmarks = collector.get_landmarks(result)
                features = collector.extract_features(landmarks)
                if features:
                    collector.add_sample(features, current_letter)
                    captured += 1
                    cv2.putText(
                        frame,
                        f"Capturing {captured}/50...",
                        (10, frame.shape[0] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2,
                    )
                cv2.imshow("Data Collector", frame)
                cv2.waitKey(30)
            print(f"Captured {captured} samples for {current_letter}")
        elif 65 <= key <= 90:
            current_letter = chr(key)
            print(f"Selected letter: {current_letter}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
