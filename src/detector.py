"""
Sign Language Interpreter - Hand Detector Module
MediaPipe hand detection with landmark extraction
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
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
FINGER_DIP = [3, 7, 11, 15, 19]


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


class HandDetector:
    def __init__(self, model_path="hand_landmarker.task"):
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

        return np.array(features)

    @staticmethod
    def draw_hand(frame, landmarks, connections=HAND_CONNECTIONS):
        if landmarks is None:
            return frame

        h, w = frame.shape[:2]

        for i, landmark in enumerate(landmarks):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            color = (0, 255, 0) if i == 0 else (0, 200, 0)
            cv2.circle(frame, (x, y), 6 if i == 0 else 4, color, -1)

        for start, end in connections:
            start_pt = (int(landmarks[start].x * w), int(landmarks[start].y * h))
            end_pt = (int(landmarks[end].x * w), int(landmarks[end].y * h))
            cv2.line(frame, start_pt, end_pt, (0, 200, 0), 2)

        return frame


def extract_features_from_csv_row(row, detector):
    landmarks = []
    for i in range(21):
        x = row[i * 3]
        y = row[i * 3 + 1]
        z = row[i * 3 + 2]
        landmarks.append(type("LM", (), {"x": x, "y": y, "z": z})())

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

    return np.array(features)


def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        result = detector.detect(frame)
        landmarks = detector.get_landmarks(result)
        frame = detector.draw_hand(frame, landmarks)

        cv2.imshow("Hand Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
