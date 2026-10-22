from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "datasets" / "raw"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================================
# Load Dataset
# ==========================================================

train_path = RAW_DIR / "deepset_train.csv"
test_path = RAW_DIR / "deepset_test.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

print("=" * 60)
print("ORIGINAL DATASET INFORMATION")
print("=" * 60)

print(f"Training Samples: {len(train_df)}")
print(f"Testing Samples: {len(test_df)}")


# ==========================================================
# Data Cleaning
# ==========================================================

def clean_dataset(df):

    df = df.copy()

    # Remove missing values
    df = df.dropna(subset=["text", "label"])

    # Convert prompt to string
    df["text"] = df["text"].astype(str)

    # Remove empty prompts
    df = df[df["text"].str.strip() != ""]

    # Remove leading/trailing spaces
    df["text"] = df["text"].str.strip()

    # Remove duplicate prompts
    df = df.drop_duplicates(subset=["text"])

    return df


train_df = clean_dataset(train_df)
test_df = clean_dataset(test_df)


# ==========================================================
# Check Train/Test Overlap
# ==========================================================

train_prompts = set(train_df["text"])
test_prompts = set(test_df["text"])

overlap = train_prompts.intersection(test_prompts)

print("\nTrain/Test Overlap:", len(overlap))


# Remove overlapping prompts from training data
# Keep original test set untouched

if overlap:

    train_df = train_df[
        ~train_df["text"].isin(overlap)
    ]

    print("Overlapping samples removed from training set.")


# ==========================================================
# Create Training & Validation Sets
# ==========================================================

train_final, val_df = train_test_split(
    train_df,
    test_size=0.15,
    random_state=42,
    stratify=train_df["label"]
)


# ==========================================================
# Save Processed Datasets
# ==========================================================

train_final.to_csv(
    PROCESSED_DIR / "train.csv",
    index=False
)

val_df.to_csv(
    PROCESSED_DIR / "validation.csv",
    index=False
)

test_df.to_csv(
    PROCESSED_DIR / "test.csv",
    index=False
)


# ==========================================================
# Dataset Statistics
# ==========================================================

print("\n" + "=" * 60)
print("FINAL DATASET DISTRIBUTION")
print("=" * 60)

for name, df in [
    ("Training", train_final),
    ("Validation", val_df),
    ("Testing", test_df)
]:

    print(f"\n{name} Dataset")

    print("Samples:", len(df))

    print("Label Distribution:")
    print(df["label"].value_counts())

print("\nDataset Preparation Completed Successfully!")