WITH eligible AS (
 SELECT id AS user_id FROM users
 WHERE (:channel IS NULL OR acquisition_channel=:channel)
),
visit AS (
 SELECT e.user_id, MIN(e.event_time) AS at FROM events e JOIN eligible u ON u.user_id=e.user_id
 WHERE e.event_name='page_view' AND e.event_time>=NOW()-(:days*INTERVAL '1 day') GROUP BY e.user_id
),
signup AS (
 SELECT e.user_id, MIN(e.event_time) AS at FROM events e JOIN visit v ON v.user_id=e.user_id
 WHERE e.event_name='signup' AND e.event_time>v.at GROUP BY e.user_id
),
search_stage AS (
 SELECT e.user_id, MIN(e.event_time) AS at FROM events e JOIN signup s ON s.user_id=e.user_id
 WHERE e.event_name='search' AND e.event_time>s.at GROUP BY e.user_id
),
cart AS (
 SELECT e.user_id, MIN(e.event_time) AS at FROM events e JOIN search_stage s ON s.user_id=e.user_id
 WHERE e.event_name='add_to_cart' AND e.event_time>s.at GROUP BY e.user_id
),
checkout AS (
 SELECT e.user_id, MIN(e.event_time) AS at FROM events e JOIN cart c ON c.user_id=e.user_id
 WHERE e.event_name='checkout' AND e.event_time>c.at GROUP BY e.user_id
),
purchase AS (
 SELECT e.user_id, MIN(e.event_time) AS at FROM events e JOIN checkout c ON c.user_id=e.user_id
 WHERE e.event_name='purchase' AND e.event_time>c.at GROUP BY e.user_id
)
SELECT stage, users FROM (
 SELECT 1 ord,'Visit' stage,COUNT(*)::int users FROM visit UNION ALL
 SELECT 2,'Signup',COUNT(*)::int FROM signup UNION ALL
 SELECT 3,'Search',COUNT(*)::int FROM search_stage UNION ALL
 SELECT 4,'Add to Cart',COUNT(*)::int FROM cart UNION ALL
 SELECT 5,'Checkout',COUNT(*)::int FROM checkout UNION ALL
 SELECT 6,'Purchase',COUNT(*)::int FROM purchase
) x ORDER BY ord;
