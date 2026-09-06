SELECT date_trunc('month',event_time AT TIME ZONE 'UTC')::date AS month,
       COALESCE(SUM(revenue),0)::float AS revenue,
       COUNT(DISTINCT user_id) FILTER (WHERE event_name='purchase') AS purchasers,
       COUNT(*) FILTER (WHERE event_name='purchase') AS orders
FROM events WHERE event_name='purchase' AND event_time>=NOW()-(:months*INTERVAL '1 month')
GROUP BY 1 ORDER BY 1;
