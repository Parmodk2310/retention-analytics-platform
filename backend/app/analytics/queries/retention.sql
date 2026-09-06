WITH anchor AS (
    SELECT COALESCE(MAX(event_date), CURRENT_DATE)::date AS as_of_date
    FROM events
),
cohort_bounds AS (
    SELECT
        date_trunc('month', as_of_date)::date AS current_month,
        (date_trunc('month', as_of_date) - INTERVAL '1 month')::date AS last_complete_month,
        (
            date_trunc('month', as_of_date)
            - (CAST(:months AS integer) * INTERVAL '1 month')
        )::date AS first_month,
        date_trunc('month', as_of_date)::timestamp AS end_exclusive
    FROM anchor
),
cohorts AS (
    SELECT
        u.id AS user_id,
        date_trunc('month', u.signup_date)::date AS cohort_month,
        u.acquisition_channel
    FROM users u
    CROSS JOIN cohort_bounds b
    WHERE u.signup_date >= b.first_month
      AND u.signup_date < b.current_month
      AND (
          CAST(:channel AS varchar) IS NULL
          OR u.acquisition_channel = CAST(:channel AS varchar)
      )
),
cohort_sizes AS (
    SELECT
        cohort_month,
        acquisition_channel,
        COUNT(*)::int AS cohort_size
    FROM cohorts
    GROUP BY cohort_month, acquisition_channel
),
active_months AS (
    SELECT DISTINCT
        e.user_id,
        date_trunc('month', e.event_time AT TIME ZONE 'UTC')::date AS activity_month
    FROM events e
    JOIN cohorts c ON c.user_id = e.user_id
    CROSS JOIN cohort_bounds b
    WHERE e.event_name IN ('session_start', 'purchase')
      AND e.event_time < b.end_exclusive
),
period_grid AS (
    SELECT
        s.cohort_month,
        s.acquisition_channel,
        s.cohort_size,
        p.period_month
    FROM cohort_sizes s
    CROSS JOIN cohort_bounds b
    CROSS JOIN LATERAL generate_series(
        0,
        LEAST(
            CAST(:months AS integer) - 1,
            (
                (EXTRACT(YEAR FROM b.last_complete_month) - EXTRACT(YEAR FROM s.cohort_month)) * 12
                + EXTRACT(MONTH FROM b.last_complete_month)
                - EXTRACT(MONTH FROM s.cohort_month)
            )::int
        )
    ) AS p(period_month)
),
retained AS (
    SELECT
        c.cohort_month,
        c.acquisition_channel,
        (
            (EXTRACT(YEAR FROM a.activity_month) - EXTRACT(YEAR FROM c.cohort_month)) * 12
            + EXTRACT(MONTH FROM a.activity_month)
            - EXTRACT(MONTH FROM c.cohort_month)
        )::int AS period_month,
        COUNT(DISTINCT c.user_id)::int AS retained_users
    FROM cohorts c
    JOIN active_months a
      ON a.user_id = c.user_id
     AND a.activity_month >= c.cohort_month
    GROUP BY c.cohort_month, c.acquisition_channel, period_month
)
SELECT
    g.cohort_month,
    g.acquisition_channel,
    g.period_month,
    CASE
        WHEN g.period_month = 0 THEN g.cohort_size
        ELSE COALESCE(r.retained_users, 0)
    END::int AS retained_users,
    g.cohort_size,
    CASE
        WHEN g.period_month = 0 THEN 1.0
        ELSE ROUND(
            COALESCE(r.retained_users, 0)::numeric / NULLIF(g.cohort_size, 0),
            4
        )::float
    END AS retention_rate
FROM period_grid g
LEFT JOIN retained r
  ON r.cohort_month = g.cohort_month
 AND r.acquisition_channel = g.acquisition_channel
 AND r.period_month = g.period_month
ORDER BY g.cohort_month, g.acquisition_channel, g.period_month;
