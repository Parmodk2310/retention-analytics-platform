import pandas as pd
import pytest

from app.ml.explain import (
    shap_reason_codes,
)
from types import SimpleNamespace


from app.ml.explain import (
    base_pipeline,
    clean_feature_name,
)


def test_clean_feature_name() -> None:
    assert clean_feature_name("num__sessions_30d") == "sessions_30d"

    assert clean_feature_name("cat__device_type_mobile") == "device_type_mobile"


def test_base_pipeline_unwraps_calibrated_model() -> None:
    base = object()

    calibrated = SimpleNamespace(base_model=base)

    assert base_pipeline(calibrated) is base


def test_base_pipeline_accepts_plain_model() -> None:
    model = object()

    assert base_pipeline(model) is model


def test_shap_reason_codes_rejects_empty_top_n() -> None:
    with pytest.raises(
        ValueError,
        match="top_n must be",
    ):
        shap_reason_codes(
            model=object(),
            frame=pd.DataFrame(
                {
                    "sessions_90d": [1],
                    "sessions_30d": [1],
                    "searches_30d": [0],
                    "carts_30d": [0],
                    "checkouts_30d": [0],
                    "purchases_90d": [0],
                    "revenue_90d": [0.0],
                    "days_since_last_activity": [5],
                    "acquisition_channel": ["organic"],
                    "device_type": ["mobile"],
                }
            ),
            top_n=0,
        )
