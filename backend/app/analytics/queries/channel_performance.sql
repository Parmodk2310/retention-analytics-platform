SELECT u.acquisition_channel,COUNT(DISTINCT u.id)::int AS users,
       COUNT(DISTINCT e.user_id) FILTER (WHERE e.event_name='purchase')::int AS purchasers,
       COALESCE(SUM(e.revenue) FILTER (WHERE e.event_name='purchase'),0)::float AS revenue
FROM users u LEFT JOIN events e ON e.user_id=u.id AND e.event_time>=NOW()-(:days*INTERVAL '1 day')
GROUP BY 1 ORDER BY users DESC;
