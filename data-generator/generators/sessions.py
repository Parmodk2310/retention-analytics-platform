import uuid
from datetime import UTC, datetime, time, timedelta

import numpy as np

from config import ACTIVITY_SCALE, EVENT_NAMESPACE, SESSION_NAMESPACE
from generators.funnel import session_events
from generators.lifecycle import active_probability, sessions_for_active_day
from generators.revenue import purchase_amount


def generate_user_events(
    user: dict,
    variant: str,
    rng: np.random.Generator,
    end_date,
) -> list[dict]:
    rows: list[dict] = []
    uid = user["id"]
    signup = user["signup_date"]
    anonymous_id = f"anon_{str(uid).replace('-', '')[:16]}"

    signup_at = datetime.combine(signup, time(hour=10), tzinfo=UTC)
    rows.append(
        _event(
            uid,
            anonymous_id,
            None,
            "page_view",
            signup_at - timedelta(minutes=2),
            0,
            {"surface": "landing", "channel": user["acquisition_channel"]},
        )
    )
    rows.append(
        _event(
            uid,
            anonymous_id,
            None,
            "signup",
            signup_at,
            0,
            {"channel": user["acquisition_channel"]},
        )
    )

    day = signup
    session_ordinal = 0

    # Generate across the complete lifecycle. The previous per-user event cap
    # made high-engagement users hit their cap early, which biased last-seen
    # retention downward for organic users.
    while day <= end_date:
        age = (day - signup).days
        weekend = day.weekday() >= 5
        activity_probability = min(
            0.95,
            active_probability(
                user["acquisition_channel"], user["baseline_engagement"], age
            )
            * ACTIVITY_SCALE,
        )

        if rng.random() < activity_probability:
            sessions = sessions_for_active_day(rng, user["baseline_engagement"], weekend)
            for _ in range(sessions):
                session_ordinal += 1
                session_id = uuid.uuid5(
                    SESSION_NAMESPACE,
                    f"{uid}:{day.isoformat()}:{session_ordinal}",
                ).hex[:24]

                minute = int(rng.integers(0, 24 * 60))
                base = datetime.combine(day, time.min, tzinfo=UTC) + timedelta(minutes=minute)
                stages = session_events(
                    rng,
                    user["baseline_engagement"],
                    variant,
                    age <= 14,
                )

                offset = 0
                for stage in stages:
                    offset += int(rng.integers(10, 120))
                    at = base + timedelta(seconds=offset)
                    # A late-night session may cross midnight. Keep the synthetic
                    # dataset strictly bounded by GENERATOR_END_DATE.
                    if at.date() > end_date:
                        break
                    revenue = purchase_amount(rng) if stage == "purchase" else 0
                    rows.append(
                        _event(
                            uid,
                            anonymous_id,
                            session_id,
                            stage,
                            at,
                            revenue,
                            {
                                "device": user["device_type"],
                                "channel": user["acquisition_channel"],
                                "country": user["country"],
                                "experiment_variant": variant,
                            },
                        )
                    )

        day += timedelta(days=int(rng.integers(1, 5)))

    return rows


def _event(
    uid,
    anonymous_id: str,
    session_id: str | None,
    name: str,
    at: datetime,
    revenue: float,
    properties: dict,
) -> dict:
    identity = f"{uid}:{session_id or 'acquisition'}:{name}:{at.isoformat()}"
    event_id = uuid.uuid5(EVENT_NAMESPACE, identity)
    return {
        "event_id": event_id,
        "user_id": uid,
        "anonymous_id": anonymous_id,
        "session_id": session_id,
        "event_name": name,
        "event_time": at,
        "event_date": at.date(),
        "revenue": revenue,
        "properties": properties,
    }
