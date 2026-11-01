from pathlib import Path
import sys
import time

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# ==========================================================
# Paths and Backend Imports
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
VALIDATION_PATH = (
    PROJECT_ROOT / "ml" / "datasets" / "processed" / "validation.csv"
)
SVM_PATH = (
    PROJECT_ROOT / "ml" / "saved_models" / "linear_svm.joblib"
)
RESULTS_DIR = PROJECT_ROOT / "research" / "results"

# Allows "app" imports when running this script from project root.
sys.path.insert(0, str(BACKEND_DIR))

from app.detection.rule_detector import detect_rule_based
from app.detection.logistic_detector import detect_logistic
from app.detection.transformer_detector import detect_transformer
from app.risk_engine.hybrid_policy import apply_or_policy


# ==========================================================
# Helpers
# ==========================================================

def timed_call(function, *args):
    start = time.perf_counter()
    result = function(*args)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms


def calculate_metrics(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1],
    ).ravel()

    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(
            y_true, y_pred, pos_label=1, zero_division=0
        ),
        "recall": recall_score(
            y_true, y_pred, pos_label=1, zero_division=0
        ),
        "f1": f1_score(
            y_true, y_pred, pos_label=1, zero_division=0
        ),
        "fpr": fp / (fp + tn) if (fp + tn) else 0.0,
        "fnr": fn / (fn + tp) if (fn + tp) else 0.0,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def main():
    if not VALIDATION_PATH.is_file():
        raise FileNotFoundError(
            f"Validation dataset not found: {VALIDATION_PATH}"
        )

    if not SVM_PATH.is_file():
        raise FileNotFoundError(
            f"Linear SVM model not found: {SVM_PATH}"
        )

    df = pd.read_csv(VALIDATION_PATH)

    if df.empty:
        raise ValueError("Validation dataset is empty.")

    required_columns = {"text", "label"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Validation CSV must have columns: {required_columns}"
        )

    if df[["text", "label"]].isna().any().any():
        raise ValueError("Validation text or label contains missing values.")

    numeric_labels = pd.to_numeric(df["label"], errors="raise")

    if not numeric_labels.isin([0, 1]).all():
        raise ValueError("Expected labels containing only 0 and 1.")

    y_true = numeric_labels.astype(int).tolist()
    prompts = df["text"].astype(str).tolist()

    print("\nLoading Linear SVM pipeline...")
    # Load only trusted joblib artifacts.
    svm_model = joblib.load(SVM_PATH)

    print(f"Validation samples: {len(df)}")
    print("Label counts:")
    print(numeric_labels.value_counts().sort_index().to_string())

    predictions = {
        "Rule-based": [],
        "Logistic Regression": [],
        "Linear SVM": [],
        "DistilBERT": [],
        "Rule + LR (OR)": [],
        "Rule + DistilBERT (OR)": [],
        "Rule + LR + DistilBERT (OR)": [],
    }

    latency = {
        "Rule-based": [],
        "Logistic Regression": [],
        "Linear SVM": [],
        "DistilBERT": [],
    }

    print("\nEvaluating prompts individually...")

    for index, prompt in enumerate(prompts, start=1):
        rule_result, rule_ms = timed_call(detect_rule_based, prompt)
        lr_result, lr_ms = timed_call(detect_logistic, prompt)
        svm_result, svm_ms = timed_call(svm_model.predict, [prompt])
        bert_result, bert_ms = timed_call(detect_transformer, prompt)

        rule_flag = bool(rule_result["attack_detected"])
        lr_flag = bool(lr_result["attack_detected"])
        svm_flag = int(svm_result[0])
        bert_flag = bool(bert_result["attack_detected"])

        triple_policy = apply_or_policy(
            rule_detected=rule_flag,
            logistic_detected=lr_flag,
            transformer_detected=bert_flag,
        )

        predictions["Rule-based"].append(int(rule_flag))
        predictions["Logistic Regression"].append(int(lr_flag))
        predictions["Linear SVM"].append(svm_flag)
        predictions["DistilBERT"].append(int(bert_flag))

        predictions["Rule + LR (OR)"].append(
            int(rule_flag or lr_flag)
        )

        predictions["Rule + DistilBERT (OR)"].append(
            int(rule_flag or bert_flag)
        )

        predictions["Rule + LR + DistilBERT (OR)"].append(
            int(triple_policy["decision"] == "BLOCK")
        )

        latency["Rule-based"].append(rule_ms)
        latency["Logistic Regression"].append(lr_ms)
        latency["Linear SVM"].append(svm_ms)
        latency["DistilBERT"].append(bert_ms)

        if index % 10 == 0 or index == len(prompts):
            print(f"Processed: {index}/{len(prompts)}")

    # ======================================================
    # Metric Results
    # ======================================================

    rows = []

    for name, y_pred in predictions.items():
        row = {"method": name}
        row.update(calculate_metrics(y_true, y_pred))
        rows.append(row)

    results_df = pd.DataFrame(rows)

    print("\n" + "=" * 100)
    print("VALIDATION RESULTS")
    print("=" * 100)
    print(results_df.to_string(index=False, float_format="%.4f"))

    # ======================================================
    # Individual Detector Latency
    # ======================================================

    print("\n" + "=" * 60)
    print("MEAN PER-PROMPT DETECTOR LATENCY (ms)")
    print("=" * 60)

    latency_rows = []

    for name, values in latency.items():
        mean_ms = sum(values) / len(values)

        latency_rows.append({
            "method": name,
            "mean_latency_ms": mean_ms,
        })

        print(f"{name}: {mean_ms:.3f} ms")

    print(
        "\nLatency includes local detector calls only. "
        "It excludes model loading, API, and LLM overhead."
    )

    # ======================================================
    # Save Aggregate Results
    # ======================================================

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    metrics_path = RESULTS_DIR / "hybrid_validation_metrics.csv"
    latency_path = RESULTS_DIR / "hybrid_validation_latency.csv"

    results_df.to_csv(metrics_path, index=False)
    pd.DataFrame(latency_rows).to_csv(latency_path, index=False)

    print(f"\nMetrics saved to: {metrics_path}")
    print(f"Latency saved to: {latency_path}")


if __name__ == "__main__":
    main()