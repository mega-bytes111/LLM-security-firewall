from pathlib import Path

import joblib


# ==========================================================
# Model Path
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "saved_models"
    / "logistic_regression.joblib"
)


# ==========================================================
# Load Trained Pipeline
# ==========================================================

if not MODEL_PATH.is_file():
    raise FileNotFoundError(
        f"Logistic Regression model not found: {MODEL_PATH}"
    )

print("Loading Logistic Regression Security Detector...")

# Only load model files that you trust.
model = joblib.load(MODEL_PATH)

# Confirm that the saved pipeline supports binary prediction
# and exposes the expected class labels.
if not hasattr(model, "predict_proba") or not hasattr(model, "classes_"):
    raise ValueError(
        "The saved model must support predict_proba and expose classes_."
    )

classes = list(model.classes_)

if set(classes) != {0, 1}:
    raise ValueError(
        f"Expected model classes 0 and 1, but found: {classes}"
    )

print(f"Logistic Regression loaded successfully. Classes: {classes}")


# ==========================================================
# Logistic Regression Detection
# ==========================================================

def detect_logistic(prompt: str) -> dict:
    """
    Run the complete TF-IDF + Logistic Regression pipeline.

    Label mapping:
        0 = benign
        1 = malicious
    """

    predicted_class = int(model.predict([prompt])[0])

    probabilities = model.predict_proba([prompt])[0]

    # Find indexes by class label rather than assuming their order.
    benign_index = classes.index(0)
    malicious_index = classes.index(1)

    benign_score = float(probabilities[benign_index])
    malicious_score = float(probabilities[malicious_index])

    confidence = (
        malicious_score if predicted_class == 1 else benign_score
    )

    return {
        "attack_detected": bool(predicted_class == 1),
        "attack_type": (
            "malicious" if predicted_class == 1 else "benign"
        ),
        "confidence": round(confidence, 4),
        "malicious_probability": round(malicious_score, 4),
        "detection_method": "logistic_regression",
    }