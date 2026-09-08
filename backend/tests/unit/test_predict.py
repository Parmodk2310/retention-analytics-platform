import numpy as np
import pandas as pd

from app.ml.predict import predict_scores, risk_band


class Model:
    def predict_proba(self, frame):
        scores = np.asarray(frame["sessions_90d"], dtype=float)
        return np.column_stack([1 - scores, scores])


def test_predict_scores_are_probabilities():
    frame = pd.DataFrame({
        "sessions_90d": [0.2, 0.8], "sessions_30d": [0, 0], "searches_30d": [0, 0],
        "carts_30d": [0, 0], "checkouts_30d": [0, 0], "purchases_90d": [0, 0],
        "revenue_90d": [0, 0], "days_since_last_activity": [0, 0],
        "acquisition_channel": ["organic", "organic"], "device_type": ["web", "web"],
    })
    assert predict_scores(Model(), frame).tolist() == [0.2, 0.8]


def test_risk_band_uses_metadata_thresholds():
    metadata = {"risk_bands": {"thresholds": {"critical": 0.9, "high": 0.7, "medium": 0.4}}}
    assert risk_band(0.95, metadata) == "critical"
    assert risk_band(0.75, metadata) == "high"
    assert risk_band(0.5, metadata) == "medium"
    assert risk_band(0.1, metadata) == "low"
