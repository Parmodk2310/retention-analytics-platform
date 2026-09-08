from app.api.v1.churn import router


def test_churn_routes_are_registered() -> None:
    paths = {route.path for route in router.routes}

    assert "/churn/scores" in paths
    assert "/churn/scores/{user_id}" in paths
    assert "/churn/summary" in paths
    assert "/churn/model-health" in paths


def test_churn_router_requires_auth() -> None:
    assert router.dependencies
