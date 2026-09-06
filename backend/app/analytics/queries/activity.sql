WITH anchor AS (
    SELECT COALESCE(MAX(event_date), CURRENT_DATE)::date AS as_of_date
    FROM events
),
bounds AS (
    SELECT
        as_of_date,
        (as_of_date - ((:days - 1) * INTERVAL '1 day'))::date AS start_date
    FROM anchor
),
date_spine AS (
    SELECT generate_series(b.start_date, b.as_of_date, INTERVAL '1 day')::date AS date
    FROM bounds b
),
aggregated AS (
    SELECT
        e.event_date AS date,
        COUNT(DISTINCT e.user_id)::int AS active_users,
        COUNT(*) FILTER (WHERE e.event_name = 'session_start')::int AS sessions,
        COALESCE(SUM(e.revenue) FILTER (WHERE e.event_name = 'purchase'), 0)::float AS revenue
    FROM events e
    CROSS JOIN bounds b
    WHERE e.event_date BETWEEN b.start_date AND b.as_of_date
    GROUP BY e.event_date
)
SELECT
    d.date,
    COALESCE(a.active_users, 0)::int AS active_users,
    COALESCE(a.sessions, 0)::int AS sessions,
    COALESCE(a.revenue, 0)::float AS revenue
FROM date_spine d
LEFT JOIN aggregated a USING (date)
ORDER BY d.date;
