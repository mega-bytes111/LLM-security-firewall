from pathlib import Path
import json
import time

import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


# ==========================================================
# Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "datasets" / "processed"

MODEL_DIR = BASE_DIR / "saved_models"

RESULTS_DIR = BASE_DIR.parent / "research" / "results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Load Validation Data
# ==========================================================

validation_df = pd.read_csv(
    DATA_DIR / "validation.csv"
)

X_val = validation_df["text"]
y_val = validation_df["label"]


# ==========================================================
# Models
# ==========================================================

models = {
    "logistic_regression": MODEL_DIR / "logistic_regression.joblib",
    "linear_svm": MODEL_DIR / "linear_svm.joblib"
}


# ==========================================================
# Evaluate Models
# ==========================================================

for model_name, model_path in models.items():

    print("\n" + "=" * 65)
    print(f"EVALUATING: {model_name.upper()}")
    print("=" * 65)

    model = joblib.load(model_path)

    # Warm-up prediction
    model.predict([X_val.iloc[0]])

    predictions = []
    latencies = []

    for prompt in X_val:

        start_time = time.perf_counter()

        prediction = model.predict([prompt])[0]

        end_time = time.perf_counter()

        predictions.append(prediction)

        latencies.append(
            (end_time - start_time) * 1000
        )

    # Confusion Matrix
    cm = confusion_matrix(
        y_val,
        predictions,
        labels=[0, 1]
    )

    tn, fp, fn, tp = cm.ravel()

    # Advanced Metrics
    accuracy = accuracy_score(y_val, predictions)

    precision = precision_score(
        y_val,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_val,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_val,
        predictions,
        zero_division=0
    )

    fpr = fp / (fp + tn) if (fp + tn) else 0

    fnr = fn / (fn + tp) if (fn + tp) else 0

    specificity = tn / (tn + fp) if (tn + fp) else 0

    avg_latency = sum(latencies) / len(latencies)

    # Save Results
    results = {
        "model": model_name,
        "dataset": "validation",
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "specificity": specificity,
        "average_latency_ms": avg_latency,
        "confusion_matrix": cm.tolist()
    }

    output_path = (
        RESULTS_DIR / f"{model_name}_advanced_results.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print("\nMetrics:")
    print(json.dumps(results, indent=4))

    # Confusion Matrix Visualization
    plt.figure(figsize=(7, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Benign", "Malicious"],
        yticklabels=["Benign", "Malicious"]
    )

    plt.title(f"Confusion Matrix - {model_name}")

    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")

    plt.tight_layout()

    plt.savefig(
        RESULTS_DIR / f"{model_name}_confusion_matrix.png",
        dpi=300
    )

    plt.close()

    # Error Analysis
    error_df = validation_df.copy()

    error_df["predicted_label"] = predictions

    error_df = error_df[
        error_df["label"] != error_df["predicted_label"]
    ]

    error_df.to_csv(
        RESULTS_DIR / f"{model_name}_errors.csv",
        index=False
    )

    print(f"\nErrors Found: {len(error_df)}")

print("\nAdvanced Evaluation Completed Successfully!")