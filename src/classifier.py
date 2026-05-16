"""
Sign Language Interpreter - Classifier Module
Loads trained model and predicts ASL letters
"""

import joblib
import numpy as np

CLASSES = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


class ASLClassifier:
    def __init__(self, model_path="models/sign_classifier.pkl"):
        self.model = None
        self.model_path = model_path
        self.loaded = False

    def load_model(self):
        try:
            self.model = joblib.load(self.model_path)
            self.loaded = True
            print(f"Model loaded from {self.model_path}")
        except FileNotFoundError:
            print(f"Model not found at {self.model_path}")
            print("Run train.py first to train the model")
            self.loaded = False

    def predict(self, features):
        if not self.loaded or self.model is None:
            return None, 0.0

        if features is None:
            return None, 0.0

        features = np.array(features).reshape(1, -1)
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence = max(probabilities)

        return prediction, confidence

    def get_top_predictions(self, features, n=3):
        if not self.loaded or self.model is None:
            return []

        if features is None:
            return []

        features = np.array(features).reshape(1, -1)
        probabilities = self.model.predict_proba(features)[0]

        top_indices = np.argsort(probabilities)[-n:][::-1]
        return [(CLASSES[i], probabilities[i]) for i in top_indices]


def main():
    classifier = ASLClassifier()
    classifier.load_model()

    if classifier.loaded:
        print("Classifier ready!")
        print(f"Classes: {CLASSES}")
    else:
        print("Classifier not ready - model file missing")


if __name__ == "__main__":
    main()
