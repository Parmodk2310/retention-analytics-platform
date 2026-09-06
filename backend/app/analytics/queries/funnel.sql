WITH anchor AS (
    SELECT COALESCE(MAX(event_date), CURRENT_DATE)::date AS as_of_date
    FROM events
),
bounds AS (
    SELECT
        (as_of_date - ((:days - 1) * INTERVAL '1 day'))::date AS start_date,
        (as_of_date + INTERVAL '1 day')::timestamp AS end_exclusive
    FROM anchor
),
eligible AS (
    SELECT id AS user_id
    FROM users
    WHERE (CAST(:channel AS varchar) IS NULL OR acquisition_channel = CAST(:channel AS varchar))
),
visit AS (
    SELECT e.user_id, MIN(e.event_time) AS at
    FROM events e
    JOIN eligible u ON u.user_id = e.user_id
    CROSS JOIN bounds b
    WHERE e.event_name = 'page_view'
      AND e.event_time >= b.start_date
      AND e.event_time < b.end_exclusive
    GROUP BY e.user_id
),
signup AS (
    SELECT e.user_id, MIN(e.event_time) AS at
    FROM events e
    JOIN visit v ON v.user_id = e.user_id
    CROSS JOIN bounds b
    WHERE e.event_name = 'signup'
      AND e.event_time > v.at
      AND e.event_time < b.end_exclusive
    GROUP BY e.user_id
),
search_stage AS (
    SELECT e.user_id, MIN(e.event_time) AS at
    FROM events e
    JOIN signup s ON s.user_id = e.user_id
    CROSS JOIN bounds b
    WHERE e.event_name = 'search'
      AND e.event_time > s.at
      AND e.event_time < b.end_exclusive
    GROUP BY e.user_id
),
cart AS (
    SELECT e.user_id, MIN(e.event_time) AS at
    FROM events e
    JOIN search_stage s ON s.user_id = e.user_id
    CROSS JOIN bounds b
    WHERE e.event_name = 'add_to_cart'
      AND e.event_time > s.at
      AND e.event_time < b.end_exclusive
    GROUP BY e.user_id
),
checkout AS (
    SELECT e.user_id, MIN(e.event_time) AS at
    FROM events e
    JOIN cart c ON c.user_id = e.user_id
    CROSS JOIN bounds b
    WHERE e.event_name = 'checkout'
      AND e.event_time > c.at
      AND e.event_time < b.end_exclusive
    GROUP BY e.user_id
),
purchase AS (
    SELECT e.user_id, MIN(e.event_time) AS at
    FROM events e
    JOIN checkout c ON c.user_id = e.user_id
    CROSS JOIN bounds b
    WHERE e.event_name = 'purchase'
      AND e.event_time > c.at
      AND e.event_time < b.end_exclusive
    GROUP BY e.user_id
)
SELECT stage, users
FROM (
    SELECT 1 AS ord, 'Visit' AS stage, COUNT(*)::int AS users FROM visit
    UNION ALL SELECT 2, 'Signup', COUNT(*)::int FROM signup
    UNION ALL SELECT 3, 'Search', COUNT(*)::int FROM search_stage
    UNION ALL SELECT 4, 'Add to Cart', COUNT(*)::int FROM cart
    UNION ALL SELECT 5, 'Checkout', COUNT(*)::int FROM checkout
    UNION ALL SELECT 6, 'Purchase', COUNT(*)::int FROM purchase
) x
ORDER BY ord;
