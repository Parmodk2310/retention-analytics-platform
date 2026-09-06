from app.services.funnel_service import add_funnel_rates


def test_funnel_stage_rates() -> None:
    result = add_funnel_rates(
        [
            {"stage": "Visit", "users": 100},
            {"stage": "Signup", "users": 80},
            {"stage": "Search", "users": 60},
            {"stage": "Add to Cart", "users": 30},
            {"stage": "Checkout", "users": 20},
            {"stage": "Purchase", "users": 10},
        ]
    )

    assert [row["stage"] for row in result] == [
        "Visit",
        "Signup",
        "Search",
        "Add to Cart",
        "Checkout",
        "Purchase",
    ]
    assert result[0]["conversion_from_previous"] == 1.0
    assert result[1]["conversion_from_previous"] == 0.8
    assert result[1]["dropoff_from_previous"] == 0.2
    assert result[-1]["conversion_from_previous"] == 0.5


def test_funnel_handles_zero_previous_stage() -> None:
    result = add_funnel_rates(
        [
            {"stage": "Visit", "users": 0},
            {"stage": "Signup", "users": 0},
        ]
    )
    assert result[1]["conversion_from_previous"] == 0.0
    assert result[1]["dropoff_from_previous"] == 1.0
