import json

import psycopg

from config import DATABASE_URL, END_DATE, EXPERIMENT_ID, N_USERS, TARGET_EVENTS


def scalar(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchone()[0]


def validate() -> dict:
    checks: dict[str, bool] = {}

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            users = scalar(cur, "SELECT COUNT(*) FROM users")
            events = scalar(cur, "SELECT COUNT(*) FROM events")
            span = scalar(cur, "SELECT MAX(event_date)-MIN(event_date) FROM events")
            purchases = scalar(cur, "SELECT COUNT(*) FROM events WHERE event_name='purchase'")
            signups = scalar(cur, "SELECT COUNT(*) FROM events WHERE event_name='signup'")

            cur.execute(
                """
                SELECT variant, COUNT(*)
                FROM experiment_assignments
                WHERE experiment_id=%s
                GROUP BY variant
                """,
                (EXPERIMENT_ID,),
            )
            allocation = dict(cur.fetchall())
            total = sum(allocation.values())
            treatment_share = allocation.get("treatment", 0) / total if total else 0

            cur.execute(
                """
                WITH cohort AS (
                    SELECT
                        u.acquisition_channel,
                        u.id,
                        MAX(e.event_date) FILTER (
                            WHERE e.event_name NOT IN ('signup')
                        ) AS last_seen
                    FROM users u
                    LEFT JOIN events e ON e.user_id=u.id
                    WHERE u.signup_date <= %s::date - INTERVAL '60 days'
                    GROUP BY 1,2
                )
                SELECT
                    acquisition_channel,
                    AVG(
                        CASE
                            WHEN last_seen >= %s::date - INTERVAL '30 days' THEN 1.0
                            ELSE 0.0
                        END
                    )
                FROM cohort
                GROUP BY 1
                """,
                (END_DATE, END_DATE),
            )
            retention = dict(cur.fetchall())

            cur.execute(
                """
                WITH exposed AS (
                    SELECT user_id, variant, exposed_at
                    FROM experiment_exposures
                    WHERE experiment_id=%s
                ), converted AS (
                    SELECT DISTINCT x.user_id, x.variant
                    FROM exposed x
                    JOIN events e
                      ON e.user_id=x.user_id
                     AND e.event_name='purchase'
                     AND e.event_time>=x.exposed_at
                     AND e.event_time<x.exposed_at + INTERVAL '14 days'
                )
                SELECT
                    x.variant,
                    COUNT(*)::int AS n,
                    COUNT(c.user_id)::int AS conversions
                FROM exposed x
                LEFT JOIN converted c
                  ON c.user_id=x.user_id AND c.variant=x.variant
                GROUP BY x.variant
                """,
                (EXPERIMENT_ID,),
            )
            exp_counts = {
                row[0]: {"n": row[1], "conversions": row[2]} for row in cur.fetchall()
            }

    control = exp_counts.get("control", {"n": 0, "conversions": 0})
    treatment = exp_counts.get("treatment", {"n": 0, "conversions": 0})
    control_rate = control["conversions"] / control["n"] if control["n"] else 0
    treatment_rate = treatment["conversions"] / treatment["n"] if treatment["n"] else 0
    relative_uplift = (
        treatment_rate / control_rate - 1 if control_rate > 0 else 0
    )

    checks["expected_user_count"] = users == N_USERS
    checks["history_at_least_330_days"] = (span or 0) >= 330
    checks["signup_event_for_most_users"] = signups >= users * 0.95
    checks["purchases_positive"] = purchases > 0
    checks["experiment_50_50_close"] = abs(treatment_share - 0.5) < 0.02
    checks["treatment_uplift_positive"] = relative_uplift > 0.02
    checks["organic_retention_gt_paid_social"] = retention.get(
        "organic", 0
    ) > retention.get("paid_social", 0)
    checks["event_scale_reasonable"] = events >= min(TARGET_EVENTS * 0.90, 100_000)

    result = {
        "ok": all(checks.values()),
        "checks": checks,
        "metrics": {
            "users": users,
            "events": events,
            "target_events": TARGET_EVENTS,
            "target_coverage": round(events / TARGET_EVENTS, 4) if TARGET_EVENTS else 0,
            "history_days": span,
            "purchases": purchases,
            "treatment_share": round(treatment_share, 4),
            "experiment": {
                "control": control,
                "treatment": treatment,
                "control_rate": round(control_rate, 4),
                "treatment_rate": round(treatment_rate, 4),
                "relative_uplift": round(relative_uplift, 4),
            },
            "retention": {key: float(value) for key, value in retention.items()},
        },
    }

    if not result["ok"]:
        raise SystemExit(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
