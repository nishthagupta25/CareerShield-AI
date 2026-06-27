import json
from pathlib import Path

import joblib
import pandas as pd
from datetime import datetime
import platform
import sklearn
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "fake_job_dataset.csv"
MODEL_PATH = BASE_DIR / "model.pkl"
METRICS_PATH = BASE_DIR / "model_metrics.json"
FEATURE_IMPORTANCE_PATH = BASE_DIR / "feature_importance.json"

def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("Dataset must contain 'text' and 'label' columns.")

    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str)
    df["label"] = df["label"].astype(int)
    df = df.drop_duplicates(subset=["text"])

    return df


def build_models():
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        ),
        "Naive Bayes": MultinomialNB(),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(class_weight="balanced", random_state=42)
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            class_weight="balanced",
        ),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
    }


def make_pipeline(model):
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    max_features=1500,
                    ngram_range=(1, 2),
                    min_df=2,
                ),
            ),
            ("model", model),
        ]
    )

def extract_feature_importance(pipeline, top_n: int = 20):
    """
    Extract top TF-IDF terms influencing scam/genuine prediction.

    Works best for linear models like Logistic Regression, Linear SVM.
    For non-linear models, returns an empty explanation.
    """
    try:
        vectorizer = pipeline.named_steps["tfidf"]
        model = pipeline.named_steps["model"]

        feature_names = vectorizer.get_feature_names_out()

        # CalibratedClassifierCV wraps the estimator.
        if hasattr(model, "base_estimator"):
            estimator = model.base_estimator
        elif hasattr(model, "estimator"):
            estimator = model.estimator
        else:
            estimator = model

        if not hasattr(estimator, "coef_"):
            return {
                "available": False,
                "reason": "Feature coefficients are not available for this model type.",
                "top_scam_indicators": [],
                "top_genuine_indicators": [],
            }

        coefficients = estimator.coef_[0]

        scam_indices = coefficients.argsort()[-top_n:][::-1]
        genuine_indices = coefficients.argsort()[:top_n]

        top_scam = [
            {
                "term": str(feature_names[i]),
                "weight": round(float(coefficients[i]), 4),
            }
            for i in scam_indices
        ]

        top_genuine = [
            {
                "term": str(feature_names[i]),
                "weight": round(float(coefficients[i]), 4),
            }
            for i in genuine_indices
        ]

        return {
            "available": True,
            "method": "TF-IDF coefficient analysis",
            "top_scam_indicators": top_scam,
            "top_genuine_indicators": top_genuine,
        }

    except Exception as e:
        return {
            "available": False,
            "reason": str(e),
            "top_scam_indicators": [],
            "top_genuine_indicators": [],
        }
def main():
    print("=" * 70)
    print("CareerShield AI - Robust ML Scam Classifier Training")
    print("=" * 70)

    df = load_dataset()

    print(f"\nLoaded dataset: {len(df)} samples")
    print("Class distribution:")
    print(df["label"].value_counts().to_dict())

    X = df["text"]
    y = df["label"]

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    models = build_models()

    all_results = {}
    best_name = None
    best_pipeline = None
    best_selection_score = (-1, -1, -1)

    print("\nCross-validation results:\n")

    for name, model in models.items():
        pipeline = make_pipeline(model)

        scores = cross_validate(
            pipeline,
            X,
            y,
            cv=cv,
            scoring=["accuracy", "precision", "recall", "f1"],
            return_train_score=True,
            error_score="raise",
        )

        train_f1 = scores["train_f1"].mean()
        val_accuracy = scores["test_accuracy"].mean()
        val_precision = scores["test_precision"].mean()
        val_recall = scores["test_recall"].mean()
        val_f1 = scores["test_f1"].mean()
        overfit_gap = train_f1 - val_f1

        all_results[name] = {
            "train_f1": round(float(train_f1), 4),
            "validation_accuracy": round(float(val_accuracy), 4),
            "validation_precision": round(float(val_precision), 4),
            "validation_recall": round(float(val_recall), 4),
            "validation_f1": round(float(val_f1), 4),
            "overfit_gap_train_f1_minus_val_f1": round(float(overfit_gap), 4),
        }

        print(f"Model: {name}")
        print(f"  Train F1: {train_f1:.4f}")
        print(f"  Validation Accuracy: {val_accuracy:.4f}")
        print(f"  Validation Precision: {val_precision:.4f}")
        print(f"  Validation Recall: {val_recall:.4f}")
        print(f"  Validation F1: {val_f1:.4f}")
        print(f"  Overfit Gap: {overfit_gap:.4f}")

        if overfit_gap > 0.12:
            print("  Warning: Possible overfitting")

        print()

        selection_score = (val_f1, val_recall, val_accuracy)

        if selection_score > best_selection_score:
            best_selection_score = selection_score
            best_name = name
            best_pipeline = pipeline

    print("=" * 70)
    print(f"Best Model Selected: {best_name}")
    print("=" * 70)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    best_pipeline.fit(X_train, y_train)
    preds = best_pipeline.predict(X_test)

    print("\nFinal Holdout Classification Report:")
    print(classification_report(y_test, preds, target_names=["Genuine", "Scam"]))

    print("Final Holdout Confusion Matrix:")
    print(confusion_matrix(y_test, preds))

    joblib.dump(best_pipeline, MODEL_PATH)
    feature_importance = extract_feature_importance(best_pipeline)

    with open(FEATURE_IMPORTANCE_PATH, "w", encoding="utf-8") as f:
      json.dump(feature_importance, f, indent=4)

    best_metrics = all_results[best_name]

    metrics = {
    "project": "CareerShield AI",
    "model_version": "v1.0",
    "best_model": best_name,
    "model_type": "Text Classification",
    "task": "Recruitment Scam Detection",
    "vectorizer": "TF-IDF",
    "selection_metric": "Validation F1, then validation recall, then validation accuracy",
    "dataset_size": int(len(df)),
    "class_distribution": {
        "genuine": int((df["label"] == 0).sum()),
        "scam": int((df["label"] == 1).sum()),
    },
    "cross_validation": {
        "strategy": "StratifiedKFold",
        "folds": 5,
        "shuffle": True,
        "random_state": 42,
    },
    "deployed_model_metrics": best_metrics,
    "all_model_results": all_results,
    "training_environment": {
        "python_version": platform.python_version(),
        "sklearn_version": sklearn.__version__,
    },
    "training_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "notes": [
        "Cross-validation is used to reduce dependence on one random train-test split.",
        "Overfit gap compares training F1 and validation F1.",
        "For scam detection, recall and F1 are prioritized over accuracy.",
        "The saved model.pkl contains the full TF-IDF + classifier pipeline.",
        "This is a baseline supervised ML classifier and can be improved with larger real-world datasets.",
    ],
   }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    print(f"\nSaved best pipeline to: {MODEL_PATH}")
    print(f"Saved metrics to: {METRICS_PATH}")
    print(f"Saved feature importance to: {FEATURE_IMPORTANCE_PATH}")
    print("\nTraining complete.")


if __name__ == "__main__":
    main()