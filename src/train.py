"""
Sign Language Interpreter - Model Trainer
Trains Random Forest classifier on landmark data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.detector import (
    extract_features_from_csv_row,
    FINGER_TIPS,
    FINGER_MCP,
    FINGER_PIP,
)


def train_model(
    data_path="data/landmarks.csv", model_path="models/sign_classifier.pkl"
):
    print("Loading data...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples")
    print(f"Classes: {df['label'].nunique()}")
    print(f"Class distribution:\n{df['label'].value_counts().sort_index()}")

    num_cols = len(df.columns) - 1
    print(f"\nDetected {num_cols} feature columns")

    print("\nExtracting enhanced features...")
    X = []
    y = []
    for idx, row in df.iterrows():
        label = row["label"]
        feature_values = [row[str(i)] for i in range(num_cols)]
        features = extract_features_from_csv_row(feature_values, None)
        if features is not None:
            X.append(features)
            y.append(label)

    X = np.array(X)
    y = np.array(y)
    print(f"Feature dimensions: {X.shape}")

    print("\nSplitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    print("\nTraining Random Forest...")
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=20,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    print("\nEvaluating on training set...")
    train_accuracy = model.score(X_train, y_train)
    print(f"Training accuracy: {train_accuracy:.2%}")

    print("\nEvaluating on test set...")
    test_accuracy = model.score(X_test, y_test)
    print(f"Test accuracy: {test_accuracy:.2%}")

    print("\nDetailed Classification Report:")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix (first few classes):")
    cm = confusion_matrix(y_test, y_pred)
    print(f"Shape: {cm.shape}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    print(f"\nModel saved to {model_path}")

    return model, test_accuracy


def main():
    print("=" * 50)
    print("ASL Model Trainer")
    print("=" * 50)

    data_path = "data/landmarks.csv"
    model_path = "models/sign_classifier.pkl"

    if not os.path.exists(data_path):
        print(f"Error: Data file not found at {data_path}")
        print("Run collector.py first to collect training data")
        return

    model, accuracy = train_model(data_path, model_path)

    print("\n" + "=" * 50)
    print("Training Complete!")
    print(f"Model saved to: {model_path}")
    print(f"Test accuracy: {accuracy:.2%}")
    print("=" * 50)


if __name__ == "__main__":
    main()
