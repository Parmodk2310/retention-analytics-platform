from uuid import uuid4

from app.schemas.experiment import ExperimentResults


def result_payload():
    control_rate = 2351 / 24389
    treatment_rate = 2551 / 24403

    return {
        "experiment_id": uuid4(),
        "metric": {
            "key": "purchase_rate_14d",
            "label": "14-day purchase conversion",
            "event_name": "purchase",
            "window_days": 14,
        },
        "variants": [
            {
                "variant": "control",
                "n": 24389,
                "conversions": 2351,
                "conversion_rate": control_rate,
            },
            {
                "variant": "treatment",
                "n": 24403,
                "conversions": 2551,
                "conversion_rate": treatment_rate,
            },
        ],
        "counts": {"control": 24389, "treatment": 24403},
        "conversion_rates": {
            "control": control_rate,
            "treatment": treatment_rate,
        },
        "srm": {
            "alpha": 0.01,
            "total": 48792,
            "observed": {"control": 24389, "treatment": 24403},
            "expected": {"control": 24396.0, "treatment": 24396.0},
            "method": "exact_binomial",
            "tested": True,
            "detected": False,
            "chi_square": 0.004,
            "p_value": 0.953,
            "reason": None,
        },
        "analysis": {
            "control_rate": control_rate,
            "treatment_rate": treatment_rate,
            "absolute_lift": 0.00814,
            "relative_lift": 0.0844,
            "standard_error": 0.00272,
            "z_stat": 2.99,
            "p_value": 0.00278,
            "difference_ci": [0.0028, 0.0135],
            "confidence_level": 0.95,
            "alpha": 0.05,
            "significant": True,
            "effect_size": {
                "risk_difference": 0.00814,
                "relative_lift": 0.0844,
                "risk_ratio": 1.0844,
                "odds_ratio": 1.0943,
                "number_needed": 122.84,
                "number_needed_type": "nnt",
                "direction": "positive",
            },
            "power": {
                "alpha": 0.05,
                "target_power": 0.8,
                "allocation_ratio": 1.00057,
                "control_n": 24389,
                "treatment_n": 24403,
                "target_relative_lift": 0.05,
                "target_absolute_lift": 0.00482,
                "power_at_target_effect": 0.4303,
                "mde_absolute": 0.00762,
                "mde_relative": 0.0790,
                "required_control_n": 60145,
                "required_treatment_n": 60180,
                "adequately_powered_for_target": False,
            },
        },
        "decision": "ship_treatment",
    }


def test_production_experiment_result_contract():
    result = ExperimentResults.model_validate(result_payload())

    assert result.metric.key == "purchase_rate_14d"
    assert result.metric.window_days == 14
    assert len(result.variants) == 2
    assert result.srm.detected is False

    assert result.analysis is not None
    assert result.analysis.significant is True
    assert result.analysis.effect_size.direction == "positive"

    assert result.analysis.power is not None
    assert result.analysis.power.adequately_powered_for_target is False


def test_experiment_result_serializes_cleanly():
    payload = ExperimentResults.model_validate(result_payload()).model_dump(mode="json")

    assert payload["decision"] == "ship_treatment"
    assert payload["metric"]["key"] == "purchase_rate_14d"
    assert payload["variants"][1]["variant"] == "treatment"
