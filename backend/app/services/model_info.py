import json
from functools import lru_cache
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ML_DIR = BASE_DIR / "ml"
METRICS_PATH = ML_DIR / "model_metrics.json"
FEATURE_IMPORTANCE_PATH = ML_DIR / "feature_importance.json"


@lru_cache(maxsize=1)
def load_model_metrics():
    if not METRICS_PATH.exists():
        return {}
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_feature_importance():
    if not FEATURE_IMPORTANCE_PATH.exists():
        return {
            "available": False,
            "top_scam_indicators": [],
            "top_genuine_indicators": [],
        }
    with open(FEATURE_IMPORTANCE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_model_summary():
    metrics = load_model_metrics()
    importance = load_feature_importance()

    return {
        "model_version": metrics.get("model_version", "v1.0"),
        "best_model": metrics.get("best_model", "Unknown"),
        "vectorizer": metrics.get("vectorizer", "TF-IDF"),
        "validation_f1": metrics.get("deployed_model_metrics", {}).get("validation_f1"),
        "validation_recall": metrics.get("deployed_model_metrics", {}).get("validation_recall"),
        "dataset_size": metrics.get("dataset_size"),
        "top_scam_indicators": importance.get("top_scam_indicators", [])[:8],
        "top_genuine_indicators": importance.get("top_genuine_indicators", [])[:8],
    }