def test_ml_router_imports() -> None:
    from app.api.v1.ml import router

    assert router is not None