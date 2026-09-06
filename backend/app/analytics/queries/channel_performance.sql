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
period_events AS (
    SELECT e.user_id, e.event_name, e.revenue
    FROM events e
    CROSS JOIN bounds b
    WHERE e.event_date BETWEEN b.start_date AND b.as_of_date
)
SELECT
    u.acquisition_channel,
    COUNT(DISTINCT p.user_id)::int AS users,
    COUNT(DISTINCT p.user_id) FILTER (WHERE p.event_name = 'purchase')::int AS purchasers,
    COALESCE(SUM(p.revenue) FILTER (WHERE p.event_name = 'purchase'), 0)::float AS revenue
FROM period_events p
JOIN users u ON u.id = p.user_id
GROUP BY u.acquisition_channel
ORDER BY users DESC, u.acquisition_channel;
