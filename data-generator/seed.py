import hashlib
import json

import numpy as np
import psycopg
from psycopg.types.json import Jsonb

from config import (
    DATABASE_URL,
    END_DATE,
    EXPERIMENT_ID,
    N_USERS,
    RESET_ANALYTICS_DATA,
    SEED,
    TARGET_EVENTS,
)
from generators.experiments import assign, experiment_row, exposure_time
from generators.sessions import generate_user_events
from generators.users import generate_users

USER_SQL = """
INSERT INTO users (
    id, external_id, signup_date, acquisition_channel,
    device_type, country, baseline_engagement
)
VALUES (
    %(id)s, %(external_id)s, %(signup_date)s, %(acquisition_channel)s,
    %(device_type)s, %(country)s, %(baseline_engagement)s
)
ON CONFLICT (external_id) DO UPDATE SET
    signup_date = EXCLUDED.signup_date,
    acquisition_channel = EXCLUDED.acquisition_channel,
    device_type = EXCLUDED.device_type,
    country = EXCLUDED.country,
    baseline_engagement = EXCLUDED.baseline_engagement
"""

EVENT_SQL = """
INSERT INTO events (
    event_id, user_id, anonymous_id, session_id, event_name,
    event_time, event_date, revenue, properties
)
VALUES (
    %(event_id)s, %(user_id)s, %(anonymous_id)s, %(session_id)s, %(event_name)s,
    %(event_time)s, %(event_date)s, %(revenue)s, %(properties)s
)
ON CONFLICT (event_id) DO NOTHING
"""


def chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def reset_analytics(cur) -> None:
    cur.execute(
        """
        TRUNCATE TABLE
            experiment_exposures,
            experiment_assignments,
            events,
            churn_scores,
            users,
            experiments,
            model_runs
        RESTART IDENTITY CASCADE
        """
    )


def rng_for_user(user_id) -> np.random.Generator:
    digest = hashlib.sha256(f"{SEED}:{user_id}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest[:8], "big"))


def seed() -> dict:
    user_rng = np.random.default_rng(SEED)
    users = generate_users(user_rng)
    event_count = 0

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            if RESET_ANALYTICS_DATA:
                print(json.dumps({"action": "reset_analytics_data"}))
                reset_analytics(cur)
                conn.commit()

            for batch in chunks(users, 2_000):
                cur.executemany(USER_SQL, batch)

            exp = experiment_row()
            cur.execute(
                """
                INSERT INTO experiments (
                    id, key, name, hypothesis, primary_metric,
                    variants, traffic_allocation, status
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (key) DO UPDATE SET
                    name = EXCLUDED.name,
                    hypothesis = EXCLUDED.hypothesis,
                    primary_metric = EXCLUDED.primary_metric,
                    variants = EXCLUDED.variants,
                    traffic_allocation = EXCLUDED.traffic_allocation,
                    status = EXCLUDED.status
                """,
                (
                    exp["id"],
                    exp["key"],
                    exp["name"],
                    exp["hypothesis"],
                    exp["primary_metric"],
                    Jsonb(exp["variants"]),
                    Jsonb(exp["traffic_allocation"]),
                    exp["status"],
                ),
            )
            conn.commit()

            for idx, batch in enumerate(chunks(users, 500)):
                events: list[dict] = []
                assignments: list[tuple] = []
                exposures: list[tuple] = []

                for user in batch:
                    variant = assign(str(user["id"]))
                    assigned = exposure_time(user["signup_date"])
                    assignments.append((EXPERIMENT_ID, user["id"], variant, assigned))
                    exposures.append((EXPERIMENT_ID, user["id"], variant, assigned))
                    events.extend(
                        generate_user_events(
                            user,
                            variant,
                            rng_for_user(user["id"]),
                            END_DATE,
                        )
                    )

                cur.executemany(
                    """
                    INSERT INTO experiment_assignments (
                        experiment_id, user_id, variant, assigned_at
                    )
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT (experiment_id,user_id) DO NOTHING
                    """,
                    assignments,
                )
                cur.executemany(
                    """
                    INSERT INTO experiment_exposures (
                        experiment_id, user_id, variant, exposed_at
                    )
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT (experiment_id,user_id) DO NOTHING
                    """,
                    exposures,
                )

                prepared = [
                    {**event, "properties": Jsonb(event["properties"])} for event in events
                ]
                for event_batch in chunks(prepared, 5_000):
                    cur.executemany(EVENT_SQL, event_batch)

                event_count += len(events)
                conn.commit()

                if (idx + 1) % 10 == 0 or (idx + 1) * 500 >= len(users):
                    print(
                        json.dumps(
                            {
                                "users_processed": min((idx + 1) * 500, len(users)),
                                "events_generated": event_count,
                                "target_events": TARGET_EVENTS,
                            }
                        )
                    )

    return {
        "users": len(users),
        "events_generated": event_count,
        "target_events": TARGET_EVENTS,
        "seed": SEED,
        "reset_analytics_data": RESET_ANALYTICS_DATA,
    }


if __name__ == "__main__":
    print(json.dumps(seed(), indent=2))
