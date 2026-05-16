"""
Dataset Processor
Processes ASL images and extracts hand landmarks for training
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import pandas as pd
import os
from pathlib import Path
import time

DATA_PATH = "data/archive(1)/asl_alphabet_train/asl_alphabet_train"
OUTPUT_PATH = "data/landmarks.csv"
SAMPLES_PER_CLASS = 200

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


class LandmarkExtractor:
    def __init__(self, model_path="hand_landmarker.task"):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            running_mode=vision.RunningMode.IMAGE,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def extract(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            return None

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)

        if result.hand_landmarks:
            return result.hand_landmarks[0]
        return None

    def features_from_landmarks(self, landmarks):
        if landmarks is None:
            return None

        wrist_x = landmarks[0].x
        wrist_y = landmarks[0].y

        features = []
        for lm in landmarks:
            features.append(lm.x - wrist_x)
            features.append(lm.y - wrist_y)
            features.append(getattr(lm, "z", 0))

        return np.array(features)


def process_dataset():
    print("Initializing landmark extractor...")
    extractor = LandmarkExtractor()

    classes = sorted(
        [d for d in os.listdir(DATA_PATH) if os.path.isdir(os.path.join(DATA_PATH, d))]
    )
    print(f"Found {len(classes)} classes: {classes}")

    all_features = []
    all_labels = []

    total_processed = 0
    total_skipped = 0

    for class_name in classes:
        class_path = os.path.join(DATA_PATH, class_name)
        images = sorted(
            [f for f in os.listdir(class_path) if f.endswith((".jpg", ".png", ".jpeg"))]
        )

        sampled = images[:SAMPLES_PER_CLASS]
        print(f"\nProcessing {class_name}: {len(sampled)} images...")

        class_features = []
        class_skipped = 0

        for i, img_name in enumerate(sampled):
            img_path = os.path.join(class_path, img_name)
            landmarks = extractor.extract(img_path)
            features = extractor.features_from_landmarks(landmarks)

            if features is not None:
                class_features.append(features)
                total_processed += 1
            else:
                class_skipped += 1
                total_skipped += 1

            if (i + 1) % 100 == 0:
                print(
                    f"  {i + 1}/{len(sampled)} - Detected: {len(class_features)}, Skipped: {class_skipped}"
                )

        if class_features:
            class_arr = np.array(class_features)
            all_features.append(class_arr)
            all_labels.extend([class_name] * len(class_features))

        print(f"  Completed: {len(class_features)} detected, {class_skipped} no-hand")

    X = np.vstack(all_features)
    y = np.array(all_labels)

    print(f"\nTotal: {len(X)} samples, {len(y)} labels")
    print(f"Skipped: {total_skipped} images (no hand detected)")
    print(f"Feature shape: {X.shape}")

    df = pd.DataFrame(X)
    df["label"] = y

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to {OUTPUT_PATH}")

    return X, y


if __name__ == "__main__":
    print("=" * 50)
    print("ASL Dataset Processor")
    print("=" * 50)

    start_time = time.time()
    X, y = process_dataset()
    elapsed = time.time() - start_time

    print(f"\nCompleted in {elapsed:.1f} seconds")
    print(f"Samples: {len(X)}")
    print(f"Classes: {len(np.unique(y))}")
