"""
Exploratory Data Analysis for Combined Data.csv.
Run from project root: python backend/scripts/explore_dataset.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd

DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "Dataset" / "Combined Data.csv"


def main():
    df = pd.read_csv(DATASET_PATH)
    # Handle unnamed index column if present
    if df.columns[0].startswith("Unnamed") or df.columns[0] == "":
        df = df.iloc[:, 1:]  # Skip index column

    # Use statement, status
    assert "statement" in df.columns and "status" in df.columns, "Expected statement, status columns"

    print("=== Dataset Summary ===")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print()

    print("=== Class Distribution ===")
    counts = df["status"].value_counts()
    for cls, cnt in counts.items():
        pct = cnt / len(df) * 100
        print(f"  {cls}: {cnt} ({pct:.1f}%)")
    print()

    print("=== Sample Statements (first 3) ===")
    for i, row in df.head(3).iterrows():
        print(f"  [{row['status']}] {row['statement'][:80]}...")
    print()

    print("=== Missing Values ===")
    print(df.isnull().sum())
    print()

    # Suggest stratification
    print("=== Stratified Split (80/20) ===")
    from sklearn.model_selection import train_test_split
    X = df["statement"]
    y = df["status"]
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    print(f"Train: {len(X_train)}, Val: {len(X_val)}")


if __name__ == "__main__":
    main()
