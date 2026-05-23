"""
Train Mental Health Classification model on Combined Data.csv.
Saves mh_classifier.joblib and tfidf_vectorizer.joblib to backend/models/.

Run from project root: python backend/scripts/train_model.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score, confusion_matrix

from app.utils.preprocess import preprocess_text

DATASET_PATH = Path(__file__).resolve().parent.parent.parent / "Dataset" / "Combined Data.csv"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def load_and_prepare_data():
    """Load CSV, drop NaNs, preprocess statements."""
    df = pd.read_csv(DATASET_PATH)

    # Handle index column if present
    if df.columns[0].startswith("Unnamed") or df.columns[0] == "":
        df = df.iloc[:, 1:]

    df = df.dropna(subset=["statement", "status"])
    df["statement_cleaned"] = df["statement"].astype(str).apply(preprocess_text)
    df = df[df["statement_cleaned"].str.len() > 0]

    return df["statement_cleaned"], df["status"]


def main():
    print("Loading and preprocessing data...")
    X, y = load_and_prepare_data()

    print(f"Total samples: {len(X)}")
    print(f"Classes: {y.unique().tolist()}")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print("Training TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=15000,
        sublinear_tf=True,
        min_df=2,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_val_vec = vectorizer.transform(X_val)

    print("Training LogisticRegression classifier...")
    classifier = LogisticRegression(
        class_weight="balanced",
        max_iter=2000,
        random_state=42,
    )
    classifier.fit(X_train_vec, y_train)

    y_pred = classifier.predict(X_val_vec)
    f1 = f1_score(y_val, y_pred, average="macro")
    print(f"\nF1-macro: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_val, y_pred))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_val, y_pred, labels=classifier.classes_))

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(classifier, MODELS_DIR / "mh_classifier.joblib")
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    print(f"\nModels saved to {MODELS_DIR}")


if __name__ == "__main__":
    main()
