from datetime import date

import pandas as pd
import pytest

from app.ml.dataset import SNAPSHOT_SQL, latest_safe_snapshot_date
from app.ml.split import temporal_train_validation_test_split


def normalize_sql(sql: str) -> str:
    return " ".join(sql.lower().split())


def test_features_are_strictly_pre_snapshot() -> None:
    sql = normalize_sql(str(SNAPSHOT_SQL))

    assert "e.event_time < cast(:snapshot_date as date)" in sql


def test_label_window_starts_at_snapshot() -> None:
    sql = normalize_sql(str(SNAPSHOT_SQL))

    assert "e.event_time >= cast(:snapshot_date as date)" in sql

    assert "e.event_time < cast(:snapshot_date as date)" in sql

    assert "cast(:label_days as integer)" in sql

    assert "interval '1 day'" in sql


def test_latest_safe_snapshot_reserves_label_window() -> None:
    assert latest_safe_snapshot_date(
        date(2026, 9, 7),
        label_days=30,
    ) == date(2026, 8, 8)


def test_latest_safe_snapshot_rejects_invalid_label_window() -> None:
    with pytest.raises(ValueError):
        latest_safe_snapshot_date(
            date(2026, 9, 7),
            label_days=0,
        )


def test_temporal_split_preserves_chronology() -> None:
    dates = pd.date_range(
        "2026-01-01",
        periods=8,
        freq="30D",
    )

    rows = []

    for snapshot_date in dates:
        for user_number in range(5):
            rows.append(
                {
                    "user_id": f"user-{user_number}",
                    "snapshot_date": snapshot_date,
                    "churned": user_number % 2,
                }
            )

    df = pd.DataFrame(rows)

    splits = temporal_train_validation_test_split(df)

    assert splits.train["snapshot_date"].nunique() == 5
    assert splits.validation["snapshot_date"].nunique() == 1
    assert splits.test["snapshot_date"].nunique() == 2

    assert splits.train["snapshot_date"].max() < splits.validation["snapshot_date"].min()

    assert splits.validation["snapshot_date"].max() < splits.test["snapshot_date"].min()


def test_temporal_split_never_shares_snapshot_dates() -> None:
    dates = pd.date_range(
        "2026-01-01",
        periods=8,
        freq="30D",
    )

    df = pd.DataFrame(
        {
            "user_id": [f"user-{i}" for i in range(8)],
            "snapshot_date": dates,
            "churned": [0, 1, 0, 1, 0, 1, 0, 1],
        }
    )

    splits = temporal_train_validation_test_split(df)

    train_dates = set(splits.train["snapshot_date"])
    validation_dates = set(splits.validation["snapshot_date"])
    test_dates = set(splits.test["snapshot_date"])

    assert train_dates.isdisjoint(validation_dates)
    assert train_dates.isdisjoint(test_dates)
    assert validation_dates.isdisjoint(test_dates)
