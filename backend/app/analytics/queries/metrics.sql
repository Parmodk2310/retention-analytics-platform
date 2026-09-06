WITH anchor AS (
    SELECT COALESCE(MAX(event_date), CURRENT_DATE)::date AS as_of_date
    FROM events
),
period_bounds AS (
    SELECT
        as_of_date,
        (as_of_date - ((:days - 1) * INTERVAL '1 day'))::date AS start_date
    FROM anchor
),
engagement AS (
    SELECT
        COUNT(DISTINCT e.user_id) FILTER (
            WHERE e.event_date = b.as_of_date
        )::int AS dau,
        COUNT(DISTINCT e.user_id) FILTER (
            WHERE e.event_date BETWEEN (b.as_of_date - INTERVAL '6 days')::date AND b.as_of_date
        )::int AS wau,
        COUNT(DISTINCT e.user_id) FILTER (
            WHERE e.event_date BETWEEN (b.as_of_date - INTERVAL '29 days')::date AND b.as_of_date
        )::int AS mau
    FROM events e
    CROSS JOIN period_bounds b
    WHERE e.event_date BETWEEN (b.as_of_date - INTERVAL '29 days')::date AND b.as_of_date
),
period_commerce AS (
    SELECT
        COALESCE(SUM(e.revenue) FILTER (WHERE e.event_name = 'purchase'), 0)::float AS revenue,
        COUNT(DISTINCT e.user_id) FILTER (WHERE e.event_name = 'purchase')::int AS purchasers
    FROM events e
    CROSS JOIN period_bounds b
    WHERE e.event_date BETWEEN b.start_date AND b.as_of_date
),
new_users AS (
    SELECT COUNT(*)::int AS value
    FROM users u
    CROSS JOIN period_bounds b
    WHERE u.signup_date BETWEEN b.start_date AND b.as_of_date
)
SELECT
    b.as_of_date,
    g.dau,
    g.wau,
    g.mau,
    CASE
        WHEN g.mau = 0 THEN 0.0
        ELSE ROUND(g.dau::numeric / g.mau, 4)::float
    END AS stickiness,
    c.revenue,
    c.purchasers,
    CASE
        WHEN c.purchasers = 0 THEN 0.0
        ELSE ROUND(c.revenue::numeric / c.purchasers, 2)::float
    END AS arpu,
    n.value AS new_users
FROM period_bounds b
CROSS JOIN engagement g
CROSS JOIN period_commerce c
CROSS JOIN new_users n;
