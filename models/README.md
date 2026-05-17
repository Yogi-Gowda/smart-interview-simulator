# Models — Smart Interview Simulator

This directory contains three trained scikit-learn ML models and the training/inference code.

## Models

| File | Purpose | Algorithm | Classes |
|------|---------|-----------|---------|
| `topic_classifier.joblib` | Classify the topic of a user's answer | TF-IDF + Logistic Regression | programming, web_development, database, data_science, software_testing, oop, algorithms, operating_system, general |
| `answer_quality_classifier.joblib` | Rate the quality of a user's answer | TF-IDF + Logistic Regression | poor, average, good |
| `difficulty_predictor.joblib` | Predict question difficulty | TF-IDF + Logistic Regression | easy, medium, hard |

## Files

| File | Description |
|------|-------------|
| `train_model.py` | Trains all 3 models and saves `.joblib` files |
| `predictor.py` | Loads models and exposes `predict_*()` functions |
| `__init__.py` | Package exports |

## How to Retrain

```bash
# From the project root directory
python models/train_model.py
```

This will:
1. Train all 3 pipelines using cross-validation
2. Print accuracy metrics for each model
3. Save `.joblib` files into this directory

## How to Use in Backend

```python
from models.predictor import predict_topic, predict_answer_quality, predict_difficulty

topic   = predict_topic("A variable stores data in memory.")
quality = predict_answer_quality("Inheritance allows code reuse between classes.")
level   = predict_difficulty("What is the CAP theorem?")
```

## Model Training Data

- **Topic Classifier**: 170 synthetic examples across 9 categories
- **Answer Quality Classifier**: 45 synthetic examples (poor/average/good)
- **Difficulty Predictor**: 85+ synthetic + real examples from `dataset/questions.json`

## Recommended Formats

`.joblib` (scikit-learn standard) — already used here.
