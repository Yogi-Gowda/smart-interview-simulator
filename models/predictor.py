"""
Smart Interview Simulator — ML Model Predictor
================================================
Loads the trained .joblib models and exposes simple predict functions.

Available functions:
    predict_topic(answer_text)        → str  e.g. "programming"
    predict_answer_quality(text)      → str  "poor" | "average" | "good"
    predict_difficulty(question_text) → str  "easy" | "medium" | "hard"
    get_model_status()                → dict  {model_name: loaded/not_loaded}
"""

import os
import joblib
from typing import Optional

_MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Model file names ──────────────────────────────────────────
_TOPIC_MODEL_FILE      = "topic_classifier.joblib"
_QUALITY_MODEL_FILE    = "answer_quality_classifier.joblib"
_DIFFICULTY_MODEL_FILE = "difficulty_predictor.joblib"

# ── Lazy-loaded model singletons ─────────────────────────────
_topic_model      = None
_quality_model    = None
_difficulty_model = None
_models_loaded    = False


def _load_all_models():
    """Load all three models once and cache them."""
    global _topic_model, _quality_model, _difficulty_model, _models_loaded

    if _models_loaded:
        return

    def _load(filename: str):
        path = os.path.join(_MODEL_DIR, filename)
        if os.path.exists(path):
            try:
                return joblib.load(path)
            except Exception as e:
                print(f"[predictor] Warning: could not load {filename}: {e}")
        return None

    _topic_model      = _load(_TOPIC_MODEL_FILE)
    _quality_model    = _load(_QUALITY_MODEL_FILE)
    _difficulty_model = _load(_DIFFICULTY_MODEL_FILE)
    _models_loaded    = True

    loaded = [n for n, m in [
        ("topic_classifier", _topic_model),
        ("answer_quality_classifier", _quality_model),
        ("difficulty_predictor", _difficulty_model),
    ] if m is not None]

    print(f"[predictor] Loaded models: {loaded if loaded else 'none'}")


# ── Public API ───────────────────────────────────────────────

def predict_topic(answer_text: str) -> Optional[str]:
    """
    Classify the topic of a user's answer.

    Returns a topic string such as 'programming', 'web_development',
    'database', 'data_science', 'software_testing', 'oop',
    'algorithms', 'operating_system', or 'general'.
    Returns None if the model is unavailable.
    """
    _load_all_models()
    if _topic_model is None or not answer_text or not answer_text.strip():
        return None
    try:
        return str(_topic_model.predict([answer_text.strip()])[0])
    except Exception as e:
        print(f"[predictor] predict_topic error: {e}")
        return None


def predict_answer_quality(answer_text: str) -> Optional[str]:
    """
    Classify the quality of a user's answer.

    Returns 'poor', 'average', or 'good'.
    Returns None if the model is unavailable.
    """
    _load_all_models()
    if _quality_model is None or not answer_text or not answer_text.strip():
        return None
    try:
        return str(_quality_model.predict([answer_text.strip()])[0])
    except Exception as e:
        print(f"[predictor] predict_answer_quality error: {e}")
        return None


def predict_difficulty(question_text: str) -> Optional[str]:
    """
    Predict the difficulty of a question.

    Returns 'easy', 'medium', or 'hard'.
    Returns None if the model is unavailable.
    """
    _load_all_models()
    if _difficulty_model is None or not question_text or not question_text.strip():
        return None
    try:
        return str(_difficulty_model.predict([question_text.strip()])[0])
    except Exception as e:
        print(f"[predictor] predict_difficulty error: {e}")
        return None


def get_model_status() -> dict:
    """Return a status dict showing which models are loaded."""
    _load_all_models()
    return {
        "topic_classifier":          _topic_model is not None,
        "answer_quality_classifier": _quality_model is not None,
        "difficulty_predictor":      _difficulty_model is not None,
    }


# ── Quick self-test ───────────────────────────────────────────
if __name__ == "__main__":
    print("=== ML Predictor — Self Test ===\n")

    status = get_model_status()
    print("Model Status:")
    for name, loaded in status.items():
        icon = "✅" if loaded else "❌ (run train_model.py first)"
        print(f"  {name}: {icon}")

    print("\n--- Topic Classifier ---")
    samples = [
        "A variable stores data in memory using a name.",
        "React is a JavaScript library for building user interfaces.",
        "Primary key uniquely identifies each record in a table.",
        "Neural networks learn from labeled training data.",
        "Unit testing verifies individual components work correctly.",
        "Encapsulation hides internal object state from outside.",
        "Binary search halves the search space at every step.",
        "A deadlock occurs when processes wait for each other's resources.",
        "I don't know the answer.",
    ]
    for s in samples:
        t = predict_topic(s)
        print(f"  [{t}] {s[:60]}")

    print("\n--- Answer Quality Classifier ---")
    quality_samples = [
        ("Inheritance allows a subclass to reuse the properties and methods of a parent class, enabling code reuse and hierarchy.", "expected: good"),
        ("Inheritance is when one class gets properties from another class.", "expected: average"),
        ("It's a programming thing.", "expected: poor"),
    ]
    for text, note in quality_samples:
        q = predict_answer_quality(text)
        print(f"  [{q}] ({note}) {text[:55]}")

    print("\n--- Difficulty Predictor ---")
    difficulty_samples = [
        ("What is a variable?", "expected: easy"),
        ("Explain the difference between REST and SOAP APIs.", "expected: medium"),
        ("Explain the CAP theorem in distributed systems.", "expected: hard"),
    ]
    for text, note in difficulty_samples:
        d = predict_difficulty(text)
        print(f"  [{d}] ({note}) {text}")

    print("\n=== Self Test Complete ===")
