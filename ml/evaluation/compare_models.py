from pathlib import Path
import json

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==========================================================
# Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RESULTS_DIR = BASE_DIR.parent / "research" / "results"


# ==========================================================
# Load Results
# ==========================================================

with open(
    RESULTS_DIR / "logistic_results.json",
    "r",
    encoding="utf-8"
) as f:
    logistic_results = json.load(f)


with open(
    RESULTS_DIR / "svm_results.json",
    "r",
    encoding="utf-8"
) as f:
    svm_results = json.load(f)


# ==========================================================
# Create Comparison DataFrame
# ==========================================================

results = [logistic_results, svm_results]

comparison_df = pd.DataFrame(results)

metrics = [
    "accuracy",
    "precision",
    "recall",
    "f1_score"
]


print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

print(
    comparison_df[
        ["model"] + metrics
    ].to_string(index=False)
)


# ==========================================================
# Save Comparison CSV
# ==========================================================

comparison_df[
    ["model"] + metrics
].to_csv(
    RESULTS_DIR / "ml_model_comparison.csv",
    index=False
)


# ==========================================================
# Plot Model Comparison
# ==========================================================

plot_df = comparison_df.melt(
    id_vars="model",
    value_vars=metrics,
    var_name="Metric",
    value_name="Score"
)


plt.figure(figsize=(10, 6))

sns.barplot(
    data=plot_df,
    x="Metric",
    y="Score",
    hue="model"
)

plt.ylim(0, 1)

plt.title(
    "Machine Learning Model Performance Comparison"
)

plt.xlabel("Evaluation Metric")
plt.ylabel("Score")

plt.legend(title="Model")

plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "ml_model_comparison.png",
    dpi=300
)

plt.close()


print("\nComparison graph saved successfully!")