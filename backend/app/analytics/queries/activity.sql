SELECT event_date AS date, COUNT(DISTINCT user_id) AS active_users,
       COUNT(*) FILTER (WHERE event_name='session_start') AS sessions,
       COALESCE(SUM(revenue) FILTER (WHERE event_name='purchase'),0)::float AS revenue
FROM events
WHERE event_date >= CURRENT_DATE - (:days * INTERVAL '1 day')
GROUP BY event_date ORDER BY event_date;
