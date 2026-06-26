from functools import lru_cache
from pathlib import Path
from typing import Dict

import joblib


BASE_DIR = Path(__file__).resolve().parents[1]
ML_DIR = BASE_DIR / "ml"
MODEL_PATH = ML_DIR / "model.pkl"


@lru_cache(maxsize=1)
def load_model():
    """
    Loads the trained ML pipeline only once.
    model.pkl contains:
    TF-IDF Vectorizer + Best Classifier
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"ML model not found at: {MODEL_PATH}")

    return joblib.load(MODEL_PATH)


def predict_scam_probability(job_text: str, recruiter_message: str) -> Dict:
    """
    Predicts whether a job opportunity is likely genuine or scam.

    label:
    0 = genuine
    1 = scam
    """

    combined_text = f"{job_text or ''} {recruiter_message or ''}".strip()

    if not combined_text:
        return {
            "ml_prediction": "Insufficient Data",
            "scam_probability": 0.0,
            "model_confidence": 0.0,
        }

    model = load_model()

    prediction = int(model.predict([combined_text])[0])

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([combined_text])[0]
        genuine_probability = float(probabilities[0]) * 100
        scam_probability = float(probabilities[1]) * 100
        confidence = max(genuine_probability, scam_probability)
    else:
        scam_probability = 100.0 if prediction == 1 else 0.0
        confidence = 100.0

    return {
        "ml_prediction": "Likely Scam" if prediction == 1 else "Likely Genuine",
        "scam_probability": round(scam_probability, 2),
        "model_confidence": round(confidence, 2),
    }