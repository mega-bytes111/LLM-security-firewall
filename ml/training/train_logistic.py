from pathlib import Path
import json

import pandas as pd
import joblib

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "datasets" / "processed"
MODEL_DIR = BASE_DIR / "saved_models"

RESULTS_DIR = BASE_DIR.parent / "research" / "results"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Load Datasets
# ==========================================================

print("\nLoading Datasets...")

train_df = pd.read_csv(DATA_DIR / "train.csv")
val_df = pd.read_csv(DATA_DIR / "validation.csv")

X_train = train_df["text"]
y_train = train_df["label"]

X_val = val_df["text"]
y_val = val_df["label"]

print(f"Training Samples: {len(X_train)}")
print(f"Validation Samples: {len(X_val)}")


# ==========================================================
# Create Logistic Regression Pipeline
# ==========================================================

model = Pipeline([
    (
        "tfidf",
        TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),
            lowercase=True,
            sublinear_tf=True
        )
    ),

    (
        "classifier",
        LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        )
    )
])


# ==========================================================
# Model Training
# ==========================================================

print("\nTraining Logistic Regression Model...")

model.fit(X_train, y_train)

print("Training Completed!")


# ==========================================================
# Validation Predictions
# ==========================================================

y_pred = model.predict(X_val)


# ==========================================================
# Evaluation Metrics
# ==========================================================

metrics = {
    "model": "Logistic Regression",
    "dataset": "validation",
    "accuracy": accuracy_score(y_val, y_pred),
    "precision": precision_score(y_val, y_pred, zero_division=0),
    "recall": recall_score(y_val, y_pred, zero_division=0),
    "f1_score": f1_score(y_val, y_pred, zero_division=0),
    "confusion_matrix": confusion_matrix(
        y_val, y_pred, labels=[0, 1]
    ).tolist()
}


print("\n" + "=" * 60)
print("LOGISTIC REGRESSION VALIDATION RESULTS")
print("=" * 60)

print(classification_report(
    y_val,
    y_pred,
    labels=[0, 1],
    target_names=["Benign", "Malicious"],
    zero_division=0
))

print("\nConfusion Matrix:")
print(metrics["confusion_matrix"])


# ==========================================================
# Save Model
# ==========================================================

model_path = MODEL_DIR / "logistic_regression.joblib"

joblib.dump(model, model_path)

print(f"\nModel Saved: {model_path}")


# ==========================================================
# Save Evaluation Results
# ==========================================================

results_path = RESULTS_DIR / "logistic_results.json"

with open(results_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4)

print(f"Results Saved: {results_path}")