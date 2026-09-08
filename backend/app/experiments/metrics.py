from datetime import datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

MAX_WINDOW_DAYS = 365


def _validate_binary_metric(event_name: str, window_days: int) -> None:
    if not event_name.strip():
        raise ValueError("conversion event is required")

    if not 1 <= window_days <= MAX_WINDOW_DAYS:
        raise ValueError(f"window_days must be between 1 and {MAX_WINDOW_DAYS}")


async def binary_conversion_counts(
    db: AsyncSession,
    experiment_id: str,
    conversion_event: str,
    window_days: int,
    as_of: datetime | None = None,
) -> dict[str, dict[str, int]]:
    _validate_binary_metric(conversion_event, window_days)

    sql = text("""
        WITH watermark AS (
            SELECT COALESCE(
                CAST(:as_of AS timestamptz),
                MAX(event_time)
            ) AS as_of_time
            FROM events
        ),
        exposed AS (
            SELECT
                x.user_id,
                x.variant,
                x.exposed_at
            FROM experiment_exposures x
            CROSS JOIN watermark w
            WHERE x.experiment_id = CAST(:experiment_id AS uuid)
              AND w.as_of_time IS NOT NULL
              AND x.exposed_at
                    + (CAST(:window_days AS integer) * INTERVAL '1 day')
                  <= w.as_of_time
        ),
        converted AS (
            SELECT DISTINCT
                x.user_id,
                x.variant
            FROM exposed x
            JOIN events e
              ON e.user_id = x.user_id
             AND e.event_name = :event
             AND e.event_time >= x.exposed_at
             AND e.event_time
                   < x.exposed_at
                     + (CAST(:window_days AS integer) * INTERVAL '1 day')
        )
        SELECT
            x.variant,
            COUNT(*)::int AS n,
            COUNT(c.user_id)::int AS conversions
        FROM exposed x
        LEFT JOIN converted c
          ON c.user_id = x.user_id
         AND c.variant = x.variant
        GROUP BY x.variant
    """)

    rows = (
        (
            await db.execute(
                sql,
                {
                    "experiment_id": experiment_id,
                    "event": conversion_event,
                    "window_days": window_days,
                    "as_of": as_of,
                },
            )
        )
        .mappings()
        .all()
    )

    return {
        row["variant"]: {
            "n": row["n"],
            "conversions": row["conversions"],
        }
        for row in rows
    }
