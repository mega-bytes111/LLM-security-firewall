from pathlib import Path

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)


# ==========================================================
# Model Path
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "saved_models"
    / "distilbert_detector"
)


# ==========================================================
# Device Configuration
# ==========================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ==========================================================
# Load Tokenizer and Model
# ==========================================================

print("Loading DistilBERT Security Detector...")

tokenizer = AutoTokenizer.from_pretrained(
    str(MODEL_PATH)
)

model = AutoModelForSequenceClassification.from_pretrained(
    str(MODEL_PATH)
)

model.to(DEVICE)
model.eval()

print(f"DistilBERT loaded successfully on {DEVICE}")


# ==========================================================
# Transformer-Based Detection
# ==========================================================

def detect_transformer(prompt: str) -> dict:

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=256
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model(**inputs)

        probabilities = torch.softmax(
            outputs.logits,
            dim=-1
        )

    predicted_class = torch.argmax(
        probabilities,
        dim=-1
    ).item()

    confidence = probabilities[
        0,
        predicted_class
    ].item()

    malicious_probability = probabilities[
        0,
        1
    ].item()

    return {
        "attack_detected": bool(predicted_class == 1),

        "attack_type": (
            "malicious"
            if predicted_class == 1
            else "benign"
        ),

        "confidence": round(confidence, 4),

        "malicious_probability": round(
            malicious_probability,
            4
        ),

        "detection_method": "distilbert"
    }