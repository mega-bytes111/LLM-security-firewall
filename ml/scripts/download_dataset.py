from pathlib import Path
import pandas as pd

from datasets import load_dataset


# ==========================================================
# Project Paths
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = BASE_DIR / "datasets" / "raw"

RAW_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# Download Dataset
# ==========================================================

print("Downloading Prompt Injection Dataset...")

dataset = load_dataset(
    "deepset/prompt-injections"
)


# ==========================================================
# Dataset Inspection
# ==========================================================

print("\nDataset Information:")
print(dataset)

for split_name in dataset.keys():

    print(f"\nProcessing Split: {split_name}")

    df = dataset[split_name].to_pandas()

    print("\nDataset Shape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\nMissing Values:")
    print(df.isnull().sum())

    # Save original dataset split
    output_path = RAW_DATA_DIR / f"deepset_{split_name}.csv"

    df.to_csv(
        output_path,
        index=False
    )

    print(f"\nSaved to: {output_path}")

print("\nDataset Download Completed Successfully!")