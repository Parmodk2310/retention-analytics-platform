from datetime import date, timedelta

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.ml.labels import churn_label


DEFAULT_LABEL_DAYS = 30
DEFAULT_SNAPSHOTS = 8
DEFAULT_SPACING_DAYS = 30


SNAPSHOT_SQL = text("""
WITH eligible AS (
    SELECT
        id AS user_id,
        acquisition_channel,
        device_type
    FROM users
    WHERE signup_date
        <= CAST(:snapshot_date AS date) - INTERVAL '30 days'
),

features AS (
    SELECT
        u.user_id,
        u.acquisition_channel,
        u.device_type,

        COUNT(DISTINCT e.session_id) FILTER (
            WHERE e.event_name = 'session_start'
              AND e.event_time >=
                  CAST(:snapshot_date AS date) - INTERVAL '90 days'
              AND e.event_time < CAST(:snapshot_date AS date)
        ) AS sessions_90d,

        COUNT(DISTINCT e.session_id) FILTER (
            WHERE e.event_name = 'session_start'
              AND e.event_time >=
                  CAST(:snapshot_date AS date) - INTERVAL '30 days'
              AND e.event_time < CAST(:snapshot_date AS date)
        ) AS sessions_30d,

        COUNT(*) FILTER (
            WHERE e.event_name = 'search'
              AND e.event_time >=
                  CAST(:snapshot_date AS date) - INTERVAL '30 days'
              AND e.event_time < CAST(:snapshot_date AS date)
        ) AS searches_30d,

        COUNT(*) FILTER (
            WHERE e.event_name = 'add_to_cart'
              AND e.event_time >=
                  CAST(:snapshot_date AS date) - INTERVAL '30 days'
              AND e.event_time < CAST(:snapshot_date AS date)
        ) AS carts_30d,

        COUNT(*) FILTER (
            WHERE e.event_name = 'checkout'
              AND e.event_time >=
                  CAST(:snapshot_date AS date) - INTERVAL '30 days'
              AND e.event_time < CAST(:snapshot_date AS date)
        ) AS checkouts_30d,

        COUNT(*) FILTER (
            WHERE e.event_name = 'purchase'
              AND e.event_time >=
                  CAST(:snapshot_date AS date) - INTERVAL '90 days'
              AND e.event_time < CAST(:snapshot_date AS date)
        ) AS purchases_90d,

        COALESCE(
            SUM(e.revenue) FILTER (
                WHERE e.event_name = 'purchase'
                  AND e.event_time >=
                      CAST(:snapshot_date AS date) - INTERVAL '90 days'
                  AND e.event_time < CAST(:snapshot_date AS date)
            ),
            0
        )::float AS revenue_90d,

        GREATEST(
            0,
            COALESCE(
                CAST(:snapshot_date AS date)
                    - MAX(e.event_date) FILTER (
                        WHERE e.event_name IN (
                            'session_start',
                            'purchase'
                        )
                          AND e.event_time
                              < CAST(:snapshot_date AS date)
                    ),
                90
            )
        )::int AS days_since_last_activity

    FROM eligible u
    LEFT JOIN events e
        ON e.user_id = u.user_id

    GROUP BY
        u.user_id,
        u.acquisition_channel,
        u.device_type
),

future AS (
    SELECT
        u.user_id,
        COUNT(e.id)::int AS future_activity

    FROM eligible u
    LEFT JOIN events e
        ON e.user_id = u.user_id
       AND e.event_name IN ('session_start', 'purchase')
       AND e.event_time >= CAST(:snapshot_date AS date)
       AND e.event_time
            < CAST(:snapshot_date AS date)
              + (
                  CAST(:label_days AS integer)
                  * INTERVAL '1 day'
              )

    GROUP BY u.user_id
)

SELECT
    f.*,
    future.future_activity

FROM features f
JOIN future USING (user_id)
""")


EVENT_RANGE_SQL = text("""
SELECT
    MIN(event_date)::date AS min_event_date,
    MAX(event_date)::date AS max_event_date
FROM events
""")


def observed_event_date_range(
    engine: Engine,
) -> tuple[date, date]:
    """Return the observed event-history boundaries."""

    with engine.connect() as conn:
        row = conn.execute(EVENT_RANGE_SQL).mappings().one()

    min_event_date = row["min_event_date"]
    max_event_date = row["max_event_date"]

    if min_event_date is None or max_event_date is None:
        raise RuntimeError("Cannot build ML snapshots without event history.")

    return min_event_date, max_event_date


def latest_safe_snapshot_date(
    max_event_date: date,
    label_days: int = DEFAULT_LABEL_DAYS,
) -> date:
    """Return latest snapshot with a complete future label window."""

    if label_days < 1:
        raise ValueError("label_days must be at least 1")

    return max_event_date - timedelta(days=label_days)


def latest_complete_snapshot_date(
    engine: Engine,
    label_days: int = DEFAULT_LABEL_DAYS,
) -> date:
    """Resolve latest safe snapshot directly from event history."""

    _, max_event_date = observed_event_date_range(engine)

    return latest_safe_snapshot_date(
        max_event_date=max_event_date,
        label_days=label_days,
    )


def build_snapshot(
    engine: Engine,
    snapshot_date: date,
    label_days: int = DEFAULT_LABEL_DAYS,
) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            SNAPSHOT_SQL,
            conn,
            params={
                "snapshot_date": snapshot_date,
                "label_days": label_days,
            },
        )

    df["snapshot_date"] = pd.Timestamp(snapshot_date)

    if label_days > 0:
        df["churned"] = df["future_activity"].map(churn_label).astype(int)

    return df


def build_training_dataset(
    engine: Engine,
    end_date: date | None = None,
    snapshots: int = DEFAULT_SNAPSHOTS,
    spacing_days: int = DEFAULT_SPACING_DAYS,
    label_days: int = DEFAULT_LABEL_DAYS,
) -> pd.DataFrame:
    if snapshots < 3:
        raise ValueError("At least three snapshots are required.")

    if spacing_days < 1:
        raise ValueError("spacing_days must be at least 1.")

    if label_days < 1:
        raise ValueError("label_days must be at least 1.")

    min_event_date, max_event_date = observed_event_date_range(engine)

    latest_safe = latest_safe_snapshot_date(
        max_event_date=max_event_date,
        label_days=label_days,
    )

    if end_date is None:
        end = latest_safe
    else:
        if end_date > latest_safe:
            raise ValueError(
                f"end_date {end_date} has an incomplete "
                f"future label window; latest safe "
                f"snapshot is {latest_safe}."
            )

        end = end_date

    frames: list[pd.DataFrame] = []

    for i in range(snapshots):
        snapshot_date = end - timedelta(days=i * spacing_days)

        if snapshot_date < min_event_date:
            continue

        frame = build_snapshot(
            engine=engine,
            snapshot_date=snapshot_date,
            label_days=label_days,
        )

        if not frame.empty:
            frames.append(frame)

    if len(frames) < 3:
        raise RuntimeError("Fewer than three usable ML snapshots were generated.")

    dataset = pd.concat(
        frames,
        ignore_index=True,
    )

    return dataset.sort_values(
        ["snapshot_date", "user_id"],
        kind="stable",
    ).reset_index(drop=True)


def latest_scoring_snapshot_date(
    engine: Engine,
) -> date:
    """
    Return the first day after the newest observed
    event date.

    Features use events strictly before this date,
    allowing the scorer to consume all observed data.
    """

    _, max_event_date = observed_event_date_range(engine)

    if max_event_date is None:
        raise RuntimeError("Cannot score without observed events.")

    return max_event_date + timedelta(days=1)


def build_feature_snapshot(
    engine: Engine,
    snapshot_date: date | None = None,
) -> pd.DataFrame:
    """
    Build a feature-only snapshot for production
    inference.

    No churn label or future outcome is returned.
    """

    scoring_date = snapshot_date or latest_scoring_snapshot_date(engine)

    frame = build_snapshot(
        engine,
        snapshot_date=scoring_date,
        label_days=0,
    )

    return frame.drop(
        columns=[
            "future_activity",
            "churned",
        ],
        errors="ignore",
    )
