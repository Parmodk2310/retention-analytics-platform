import json

import joblib
import numpy as np
import pandas as pd

from app.ml.artifact_store import download_latest
from app.ml.features import FEATURES


def load_model():
    return joblib.load(download_latest("churn_model.joblib"))


def load_metadata() -> dict:
    return json.loads(download_latest("model_metadata.json").read_text(encoding="utf-8"))


def predict_scores(model, frame: pd.DataFrame) -> np.ndarray:
    scores = np.asarray(model.predict_proba(frame[FEATURES])[:, 1], dtype=float)
    if not np.isfinite(scores).all():
        raise RuntimeError("Model produced non-finite churn probabilities")
    return np.clip(scores, 0.0, 1.0)


def risk_band(score: float, metadata: dict) -> str:
    thresholds = metadata["risk_bands"]["thresholds"]
    if score >= float(thresholds["critical"]):
        return "critical"
    if score >= float(thresholds["high"]):
        return "high"
    if score >= float(thresholds["medium"]):
        return "medium"
    return "low"


def risk_band_from_metadata(
    score: float,
    metadata: dict,
) -> str:
    """
    Assign a risk band using thresholds learned from
    validation data during training.
    """

    thresholds = metadata.get("risk_bands", {}).get("thresholds", {})

    required = {
        "critical",
        "high",
        "medium",
    }

    if not required.issubset(thresholds):
        raise RuntimeError("Model metadata is missing risk-band thresholds.")

    critical = float(thresholds["critical"])

    high = float(thresholds["high"])

    medium = float(thresholds["medium"])

    if not (critical >= high >= medium):
        raise RuntimeError("Risk-band thresholds are invalid.")

    if score >= critical:
        return "critical"

    if score >= high:
        return "high"

    if score >= medium:
        return "medium"

    return "low"


def reason_codes(row: pd.Series) -> list[str]:
    pairs = []
    if row.get("days_since_last_activity", 0) >= 20:
        pairs.append("Long inactivity gap")
    if row.get("sessions_30d", 0) <= 1:
        pairs.append("Very low recent session frequency")
    if row.get("carts_30d", 0) > 0 and row.get("checkouts_30d", 0) == 0:
        pairs.append("Recent cart abandonment")
    if row.get("purchases_90d", 0) == 0:
        pairs.append("No purchase in 90 days")
    if row.get("searches_30d", 0) == 0:
        pairs.append("No recent search activity")
    return pairs[:3] or ["Broad engagement decline"]
