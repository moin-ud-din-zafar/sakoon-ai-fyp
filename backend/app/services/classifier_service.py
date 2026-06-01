"""Mental Health Classification service using TF-IDF + LogisticRegression."""

import joblib
from pathlib import Path
from typing import Tuple

from app.utils.preprocess import preprocess_text

# Models are in backend/models/ (same as train_model.py saves)
MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"


class MentalHealthClassifier:
    """Classifies user text into one of 7 MH categories."""

    def __init__(self):
        self._classifier = None
        self._vectorizer = None
        self._load_models()

    def _load_models(self):
        """Load classifier and vectorizer from disk."""
        clf_path = MODELS_DIR / "mh_classifier.joblib"
        vec_path = MODELS_DIR / "tfidf_vectorizer.joblib"
        if not clf_path.exists() or not vec_path.exists():
            raise FileNotFoundError(
                "Models not found. Run: python backend/scripts/train_model.py"
            )
        self._classifier = joblib.load(clf_path)
        self._vectorizer = joblib.load(vec_path)

    def predict(self, text: str) -> Tuple[str, float]:
        """
        Classify text into MH category.

        Returns:
            Tuple of (classification_label, confidence)
        """
        cleaned = preprocess_text(text)
        if not cleaned:
            return "Normal", 0.0

        X = self._vectorizer.transform([cleaned])
        proba = self._classifier.predict_proba(X)[0]
        idx = proba.argmax()
        confidence = float(proba[idx])
        label = self._classifier.classes_[idx]
        return label, confidence

    def predict_proba_dict(self, text: str) -> dict:
        """Return class -> probability mapping (for risk detector)."""
        cleaned = preprocess_text(text)
        if not cleaned:
            return {"Normal": 1.0}

        X = self._vectorizer.transform([cleaned])
        proba = self._classifier.predict_proba(X)[0]
        return dict(zip(self._classifier.classes_, proba.tolist()))
