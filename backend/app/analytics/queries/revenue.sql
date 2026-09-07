WITH anchor AS (
    SELECT COALESCE(MAX(event_date), CURRENT_DATE)::date AS as_of_date
    FROM events
),
bounds AS (
    SELECT
        (date_trunc('month', as_of_date) - ((:months - 1) * INTERVAL '1 month'))::date AS first_month,
        (as_of_date + INTERVAL '1 day')::timestamp AS end_exclusive
    FROM anchor
)
SELECT
    date_trunc('month', e.event_time AT TIME ZONE 'UTC')::date AS month,
    COALESCE(SUM(e.revenue), 0)::float AS revenue,
    COUNT(DISTINCT e.user_id)::int AS purchasers,
    COUNT(*)::int AS orders
FROM events e
JOIN users u ON u.id = e.user_id
CROSS JOIN bounds b
WHERE e.event_name = 'purchase'
  AND e.event_time >= b.first_month
  AND e.event_time < b.end_exclusive
  AND (
      CAST(:channel AS text) IS NULL
      OR u.acquisition_channel = CAST(:channel AS text)
  )
GROUP BY month
ORDER BY month;
