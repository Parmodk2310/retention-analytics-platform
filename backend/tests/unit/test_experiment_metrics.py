from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.experiments.metrics import binary_conversion_counts


def make_db(rows):
    mock = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value.all.return_value = rows
    mock.execute.return_value = result
    return cast(AsyncSession, mock), mock


@pytest.mark.asyncio
async def test_binary_metric_query_is_exposure_and_maturity_safe():
    db, mock = make_db(
        [
            {
                "variant": "control",
                "n": 100,
                "conversions": 10,
            }
        ]
    )

    result = await binary_conversion_counts(
        db,
        "11111111-1111-4111-8111-111111111111",
        "purchase",
        14,
    )

    assert result["control"] == {
        "n": 100,
        "conversions": 10,
    }

    statement, params = mock.execute.await_args.args
    sql = str(statement)

    assert "e.event_time >= x.exposed_at" in sql
    assert "w.as_of_time" in sql
    assert "x.exposed_at" in sql
    assert params["event"] == "purchase"
    assert params["window_days"] == 14


@pytest.mark.asyncio
@pytest.mark.parametrize("window_days", [0, -1, 366])
async def test_invalid_metric_window_is_rejected(window_days):
    db, _ = make_db([])

    with pytest.raises(ValueError):
        await binary_conversion_counts(
            db,
            "11111111-1111-4111-8111-111111111111",
            "purchase",
            window_days,
        )


@pytest.mark.asyncio
async def test_empty_conversion_event_is_rejected():
    db, _ = make_db([])

    with pytest.raises(ValueError):
        await binary_conversion_counts(
            db,
            "11111111-1111-4111-8111-111111111111",
            "",
            14,
        )
