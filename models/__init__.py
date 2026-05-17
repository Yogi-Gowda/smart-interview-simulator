"""
Smart Interview Simulator — Models Package
==========================================
Exposes ML predict functions for use by the backend.

Usage:
    from models.predictor import predict_topic, predict_answer_quality, predict_difficulty
    from models import predict_topic, predict_answer_quality, predict_difficulty
"""

from models.predictor import (
    predict_topic,
    predict_answer_quality,
    predict_difficulty,
    get_model_status,
)

__all__ = [
    "predict_topic",
    "predict_answer_quality",
    "predict_difficulty",
    "get_model_status",
]
