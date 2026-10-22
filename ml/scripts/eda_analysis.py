from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "datasets" / "processed"

RESULTS_DIR = BASE_DIR.parent / "research" / "results"

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# Load Data
# ==========================================================

train_df = pd.read_csv(PROCESSED_DIR / "train.csv")
val_df = pd.read_csv(PROCESSED_DIR / "validation.csv")
test_df = pd.read_csv(PROCESSED_DIR / "test.csv")

df = pd.concat(
    [train_df, val_df, test_df],
    ignore_index=True
)

df["prompt_length"] = df["text"].astype(str).str.len()

df["label_name"] = df["label"].map({
    0: "Benign",
    1: "Malicious"
})


# ==========================================================
# Plot 1: Class Distribution
# ==========================================================

plt.figure(figsize=(8, 5))

sns.countplot(
    data=df,
    x="label_name",
    hue="label_name",
    palette="Set2",
    legend=False
)

plt.title("Prompt Classification Dataset Distribution")
plt.xlabel("Prompt Category")
plt.ylabel("Number of Samples")

plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "class_distribution.png",
    dpi=300
)

plt.close()


# ==========================================================
# Plot 2: Prompt Length Distribution
# ==========================================================

plt.figure(figsize=(10, 6))

sns.histplot(
    data=df,
    x="prompt_length",
    hue="label_name",
    bins=40,
    kde=True
)

plt.title("Prompt Length Distribution by Class")
plt.xlabel("Prompt Length (Characters)")
plt.ylabel("Frequency")

plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "prompt_length_distribution.png",
    dpi=300
)

plt.close()


# ==========================================================
# Plot 3: Dataset Split Distribution
# ==========================================================

split_counts = {
    "Training": len(train_df),
    "Validation": len(val_df),
    "Testing": len(test_df)
}

plt.figure(figsize=(8, 5))

plt.bar(
    split_counts.keys(),
    split_counts.values(),
    color=["#3498db", "#2ecc71", "#e74c3c"]
)

plt.title("Dataset Split Distribution")
plt.xlabel("Dataset Split")
plt.ylabel("Number of Samples")

plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "dataset_split_distribution.png",
    dpi=300
)

plt.close()


print("EDA Completed Successfully!")

print(f"Graphs saved in: {RESULTS_DIR}")