from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "datasets" / "raw"
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"


def load_csv(path):
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    df = pd.read_csv(path)

    required = {"text", "label"}
    if not required.issubset(df.columns):
        raise ValueError(f"{path.name} must contain columns: {required}")

    return df


def reproduce_cleaning(df):
    """Mirror cleaning in prepare_dataset.py without writing files."""
    df = df.copy()
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)
    df = df[df["text"].str.strip() != ""]
    df["text"] = df["text"].str.strip()
    df = df.drop_duplicates(subset=["text"])
    return df


def conflicting_text_count(df):
    """Count non-empty normalized texts with more than one label."""
    clean = df.dropna(subset=["text", "label"]).copy()
    clean["text"] = clean["text"].astype(str).str.strip()
    clean = clean[clean["text"] != ""]

    labels_per_text = clean.groupby("text")["label"].nunique()
    return int((labels_per_text > 1).sum())


def main():
    raw_train = load_csv(RAW_DIR / "deepset_train.csv")
    raw_test = load_csv(RAW_DIR / "deepset_test.csv")

    train = load_csv(PROCESSED_DIR / "train.csv")
    validation = load_csv(PROCESSED_DIR / "validation.csv")
    test = load_csv(PROCESSED_DIR / "test.csv")

    cleaned_raw_test = reproduce_cleaning(raw_test)

    print("\n" + "=" * 60)
    print("DATASET AUDIT — COUNTS")
    print("=" * 60)

    print(f"Raw train:             {len(raw_train)}")
    print(f"Raw test:              {len(raw_test)}")
    print(f"Processed train:       {len(train)}")
    print(f"Processed validation:  {len(validation)}")
    print(f"Processed test:        {len(test)}")
    print(f"Raw test after cleaning: {len(cleaned_raw_test)}")

    # Compare text and label including row order, after resetting index.
    expected = cleaned_raw_test[["text", "label"]].reset_index(drop=True)
    actual = test[["text", "label"]].reset_index(drop=True)

    print(
        "\nProcessed test matches reproduced cleaning "
        "(text, label and row order):",
        expected.equals(actual),
    )

    print("\nConflicting labels for identical stripped text:")
    print(f"Raw train: {conflicting_text_count(raw_train)}")
    print(f"Raw test:  {conflicting_text_count(raw_test)}")

    train_texts = set(train["text"].astype(str))
    validation_texts = set(validation["text"].astype(str))
    test_texts = set(test["text"].astype(str))

    print("\nExact text overlap between processed splits:")
    print(f"Train / validation: {len(train_texts & validation_texts)}")
    print(f"Train / test:       {len(train_texts & test_texts)}")
    print(f"Validation / test:  {len(validation_texts & test_texts)}")

    print(
        "\nNote: exact-text checks do not detect paraphrases, "
        "translations, or near-duplicates."
    )


if __name__ == "__main__":
    main()