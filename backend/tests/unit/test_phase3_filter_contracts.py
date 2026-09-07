from pathlib import Path

QUERY_DIR = Path(__file__).parents[2] / "app" / "analytics" / "queries"


def _sql(name: str) -> str:
    return (QUERY_DIR / f"{name}.sql").read_text(encoding="utf-8")


def test_overview_channel_filter_is_typed_for_asyncpg() -> None:
    sql = _sql("overview")
    assert "CAST(:channel AS text)" in sql
    assert "u.acquisition_channel" in sql


def test_activity_channel_filter_is_typed_for_asyncpg() -> None:
    sql = _sql("activity")
    assert "CAST(:channel AS text)" in sql
    assert "JOIN users u" in sql


def test_revenue_channel_filter_is_typed_for_asyncpg() -> None:
    sql = _sql("revenue")
    assert "CAST(:channel AS text)" in sql
    assert "JOIN users u" in sql


def test_all_channel_retention_is_aggregated_before_frontend_rendering() -> None:
    sql = _sql("retention")
    assert "WHEN CAST(:channel AS text) IS NULL THEN NULL" in sql
    assert "IS NOT DISTINCT FROM" in sql
