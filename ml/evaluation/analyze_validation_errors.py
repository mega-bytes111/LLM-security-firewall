from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"

VALIDATION_PATH = (
    PROJECT_ROOT / "ml" / "datasets" / "processed" / "validation.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "research" / "results"

sys.path.insert(0, str(BACKEND_DIR))

from app.detection.rule_detector import detect_rule_based
from app.detection.logistic_detector import detect_logistic
from app.detection.transformer_detector import detect_transformer


def main():
    df = pd.read_csv(VALIDATION_PATH)

    if df.empty:
        raise ValueError("Validation dataset is empty.")

    required = {"text", "label"}
    if not required.issubset(df.columns):
        raise ValueError(f"Required columns missing: {required}")

    if df[["text", "label"]].isna().any().any():
        raise ValueError("Validation text or label contains missing values.")

    numeric_labels = pd.to_numeric(df["label"], errors="raise")
    if not numeric_labels.isin([0, 1]).all():
        raise ValueError("Labels must be 0 or 1.")

    rows = []

    print(f"\nAnalyzing {len(df)} validation samples...")

    for position, (_, record) in enumerate(df.iterrows(), start=1):
        prompt = str(record["text"])
        label = int(numeric_labels.iloc[position - 1])

        rule = detect_rule_based(prompt)
        lr = detect_logistic(prompt)
        bert = detect_transformer(prompt)

        rule_pred = int(rule["attack_detected"])
        lr_pred = int(lr["attack_detected"])
        bert_pred = int(bert["attack_detected"])

        rows.append({
            # CSV row number, excluding the header, starts at 1.
            "sample_number": position,
            "text": prompt,
            "true_label": label,
            "rule_prediction": rule_pred,
            "lr_prediction": lr_pred,
            "distilbert_prediction": bert_pred,
            "lr_malicious_score": lr["malicious_probability"],
            "distilbert_malicious_score": bert["malicious_probability"],
            "triple_or_prediction": int(
                rule_pred or lr_pred or bert_pred
            ),
            "rule_attack_type": rule["attack_type"],
        })

        if position % 10 == 0 or position == len(df):
            print(f"Processed: {position}/{len(df)}")

    analysis = pd.DataFrame(rows)

    lr_errors = analysis[
        analysis["lr_prediction"] != analysis["true_label"]
    ]

    bert_errors = analysis[
        analysis["distilbert_prediction"] != analysis["true_label"]
    ]

    disagreements = analysis[
        (analysis["lr_prediction"] != analysis["distilbert_prediction"])
        | (analysis["rule_prediction"] != analysis["lr_prediction"])
        | (analysis["rule_prediction"] != analysis["distilbert_prediction"])
    ]

    print("\n" + "=" * 60)
    print("VALIDATION ERROR SUMMARY")
    print("=" * 60)

    print(f"LR errors: {len(lr_errors)}")
    print(f"DistilBERT errors: {len(bert_errors)}")
    print(f"Any detector disagreement: {len(disagreements)}")

    print("\nRule coverage beyond model predictions:")
    print(
        "Rule flags while LR does not:",
        int(
            (
                (analysis["rule_prediction"] == 1)
                & (analysis["lr_prediction"] == 0)
            ).sum()
        ),
    )
    print(
        "Rule flags while DistilBERT does not:",
        int(
            (
                (analysis["rule_prediction"] == 1)
                & (analysis["distilbert_prediction"] == 0)
            ).sum()
        ),
    )

    print("\nErrors and disagreements are saved locally for review.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_path = OUTPUT_DIR / "validation_detector_analysis.csv"
    errors_path = OUTPUT_DIR / "validation_model_errors.csv"

    analysis.to_csv(all_path, index=False)

    analysis[
        (analysis["lr_prediction"] != analysis["true_label"])
        | (analysis["distilbert_prediction"] != analysis["true_label"])
    ].to_csv(errors_path, index=False)

    print(f"\nAll predictions saved: {all_path}")
    print(f"Model errors saved: {errors_path}")
    print(
        "\nNote: these files contain dataset prompts. "
        "Keep them local pending license/privacy review."
    )


if __name__ == "__main__":
    main()