def test_churn_service_contract_imports() -> None:
    from app.services.churn_service import (
        churn_summary,
        latest_model,
        latest_scores,
        latest_user_score,
    )

    assert callable(churn_summary)
    assert callable(latest_model)
    assert callable(latest_scores)
    assert callable(latest_user_score)
