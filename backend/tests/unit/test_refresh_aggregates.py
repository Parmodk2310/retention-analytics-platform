from unittest.mock import MagicMock

from app.jobs import refresh_aggregates


def test_refresh_statistics_analyzes_core_tables(monkeypatch) -> None:
    connection = MagicMock()
    transaction = MagicMock()
    transaction.__enter__.return_value = connection

    engine = MagicMock()
    engine.begin.return_value = transaction

    monkeypatch.setattr(
        refresh_aggregates,
        "create_engine",
        lambda *args, **kwargs: engine,
    )

    refresh_aggregates.refresh_statistics()

    statements = [str(call.args[0]) for call in connection.execute.call_args_list]

    assert statements == [
        "ANALYZE users",
        "ANALYZE events",
    ]


def test_refresh_preserves_scheduled_job_entry_point(monkeypatch) -> None:
    called = False

    def fake_refresh_statistics() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(
        refresh_aggregates,
        "refresh_statistics",
        fake_refresh_statistics,
    )

    refresh_aggregates.refresh()

    assert called is True
