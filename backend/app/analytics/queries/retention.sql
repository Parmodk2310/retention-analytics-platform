WITH cohorts AS (
 SELECT id AS user_id, date_trunc('month',signup_date::timestamp AT TIME ZONE 'UTC')::date AS cohort_month, acquisition_channel
 FROM users
 WHERE signup_date>=CURRENT_DATE-(:months*INTERVAL '1 month') AND (:channel IS NULL OR acquisition_channel=:channel)
),
cohort_sizes AS (SELECT cohort_month,acquisition_channel,COUNT(*)::int cohort_size FROM cohorts GROUP BY 1,2),
active_months AS (
 SELECT DISTINCT e.user_id,date_trunc('month',e.event_time AT TIME ZONE 'UTC')::date AS activity_month
 FROM events e JOIN cohorts c ON c.user_id=e.user_id WHERE e.event_name IN ('session_start','purchase')
),
retained AS (
 SELECT c.cohort_month,c.acquisition_channel,
        ((EXTRACT(YEAR FROM a.activity_month)-EXTRACT(YEAR FROM c.cohort_month))*12 + EXTRACT(MONTH FROM a.activity_month)-EXTRACT(MONTH FROM c.cohort_month))::int AS period_month,
        COUNT(DISTINCT c.user_id)::int retained_users
 FROM cohorts c JOIN active_months a ON a.user_id=c.user_id AND a.activity_month>=c.cohort_month
 GROUP BY 1,2,3
)
SELECT r.cohort_month,r.acquisition_channel,r.period_month,r.retained_users,s.cohort_size,
       ROUND(r.retained_users::numeric/NULLIF(s.cohort_size,0),4)::float AS retention_rate
FROM retained r JOIN cohort_sizes s USING(cohort_month,acquisition_channel)
WHERE r.period_month BETWEEN 0 AND :months
ORDER BY r.cohort_month,r.acquisition_channel,r.period_month;
