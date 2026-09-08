from pathlib import Path
import re

QUERY_DIR = Path(__file__).parents[2] / "app" / "analytics" / "queries"


def read_query(name: str) -> str:
    return (QUERY_DIR / f"{name}.sql").read_text(encoding="utf-8").lower()


def normalize_sql(sql: str) -> str:
    """Normalize SQL for formatting-insensitive contract assertions."""
    return re.sub(r"\s+", " ", sql).strip().lower()


def test_activity_has_exact_window_and_date_spine() -> None:
    sql = read_query("activity")
    assert "generate_series" in sql
    assert "between b.start_date and b.as_of_date" in sql


def test_funnel_is_ordered_and_bounded() -> None:
    sql = read_query("funnel")
    assert "e.event_time > v.at" in sql
    assert "e.event_time > s.at" in sql
    assert "e.event_time > c.at" in sql
    assert "e.event_time < b.end_exclusive" in sql


def test_retention_month_zero_is_explicit() -> None:
    sql = normalize_sql(read_query("retention"))
    assert "when g.period_month = 0 then g.cohort_size" in sql
    assert "when g.period_month = 0 then 1.0" in sql


def test_optional_channel_bind_is_explicitly_typed_for_asyncpg() -> None:
    for query_name in ("funnel", "retention"):
        sql = normalize_sql(read_query(query_name))
        assert "cast(:channel as varchar)" in sql


def test_retention_months_bind_is_explicitly_typed_for_asyncpg() -> None:
    sql = normalize_sql(read_query("retention"))
    assert "cast(:months as integer)" in sql


def test_retention_excludes_incomplete_current_month() -> None:
    sql = normalize_sql(read_query("retention"))
    assert "last_complete_month" in sql
    assert "date_trunc('month', as_of_date)::timestamp as end_exclusive" in sql
    assert "u.signup_date < b.current_month" in sql
    assert "e.event_time < b.end_exclusive" in sql
