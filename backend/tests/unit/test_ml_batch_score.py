import pytest

from app.ml.predict import (
    risk_band_from_metadata,
)


def metadata() -> dict:
    return {
        "risk_bands": {
            "thresholds": {
                "critical": 0.90,
                "high": 0.80,
                "medium": 0.60,
            }
        }
    }


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.95, "critical"),
        (0.90, "critical"),
        (0.85, "high"),
        (0.80, "high"),
        (0.70, "medium"),
        (0.60, "medium"),
        (0.59, "low"),
    ],
)
def test_metadata_risk_band(
    score: float,
    expected: str,
) -> None:
    assert (
        risk_band_from_metadata(
            score,
            metadata(),
        )
        == expected
    )


def test_metadata_risk_band_requires_thresholds() -> None:
    with pytest.raises(
        RuntimeError,
        match="risk-band thresholds",
    ):
        risk_band_from_metadata(
            0.8,
            {},
        )
