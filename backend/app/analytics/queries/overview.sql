WITH bounds AS (SELECT (CURRENT_DATE - (:days * INTERVAL '1 day'))::date AS start_date, CURRENT_DATE AS end_date),
activity AS (
 SELECT COUNT(DISTINCT user_id) FILTER (WHERE event_date=CURRENT_DATE) AS dau,
        COUNT(DISTINCT user_id) FILTER (WHERE event_date>=CURRENT_DATE-INTERVAL '6 days') AS wau,
        COUNT(DISTINCT user_id) FILTER (WHERE event_date>=CURRENT_DATE-INTERVAL '29 days') AS mau,
        COALESCE(SUM(revenue) FILTER (WHERE event_name='purchase'),0) AS revenue,
        COUNT(DISTINCT user_id) FILTER (WHERE event_name='purchase') AS purchasers
 FROM events,bounds WHERE event_date BETWEEN bounds.start_date AND bounds.end_date),
new_users AS (SELECT COUNT(*) AS value FROM users,bounds WHERE signup_date BETWEEN bounds.start_date AND bounds.end_date)
SELECT dau,wau,mau,CASE WHEN mau=0 THEN 0 ELSE ROUND(dau::numeric/mau,4) END AS stickiness,
       revenue::float,purchasers,CASE WHEN purchasers=0 THEN 0 ELSE ROUND(revenue::numeric/purchasers,2)::float END AS arpu,
       new_users.value AS new_users
FROM activity CROSS JOIN new_users;
