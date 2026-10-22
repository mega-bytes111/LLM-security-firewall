from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DATA_DIR = BASE_DIR / "datasets" / "raw"


def inspect_dataset():

    csv_files = list(
        RAW_DATA_DIR.glob("deepset_*.csv")
    )

    if not csv_files:
        print("No dataset files found.")
        print("Please run download_dataset.py first.")
        return

    for file_path in csv_files:

        print("\n" + "=" * 60)
        print(f"DATASET: {file_path.name}")
        print("=" * 60)

        df = pd.read_csv(file_path)

        print("\nTotal Rows:")
        print(len(df))

        print("\nColumns:")
        print(df.columns.tolist())

        print("\nDataset Information:")
        df.info()

        print("\nMissing Values:")
        print(df.isnull().sum())

        print("\nDuplicate Rows:")
        print(df.duplicated().sum())

        if "label" in df.columns:

            print("\nLabel Distribution:")
            print(
                df["label"].value_counts(
                    dropna=False
                )
            )

            print("\nLabel Percentage:")
            print(
                df["label"].value_counts(
                    normalize=True
                ) * 100
            )

        if "text" in df.columns:

            print("\nPrompt Length Statistics:")

            prompt_lengths = (
                df["text"]
                .fillna("")
                .astype(str)
                .str.len()
            )

            print(prompt_lengths.describe())


if __name__ == "__main__":
    inspect_dataset()