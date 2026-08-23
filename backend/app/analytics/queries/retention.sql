-- analytics/queries/retention.sql
WITH user_cohorts AS (
    SELECT 
        user_id,
        DATE_TRUNC('month', signup_date)::date AS cohort_month,
        acquisition_channel
    FROM dim_users
),
user_activity AS (
    SELECT 
        e.user_id,
        DATE_TRUNC('month', e.event_date)::date AS activity_month
    FROM fact_events e
    WHERE e.event_type IN ('session_start', 'purchase')
    GROUP BY e.user_id, DATE_TRUNC('month', e.event_date)
),
cohort_sizes AS (
    SELECT cohort_month, COUNT(DISTINCT user_id) AS cohort_size
    FROM user_cohorts
    GROUP BY cohort_month
),
retention AS (
    SELECT 
        uc.cohort_month,
        uc.acquisition_channel,
        PERIOD_DIFF(
            EXTRACT(YEAR FROM ua.activity_month)::int, 
            EXTRACT(YEAR FROM uc.cohort_month)::int
        ) * 12 + 
        EXTRACT(MONTH FROM ua.activity_month)::int - 
        EXTRACT(MONTH FROM uc.cohort_month)::int AS period_month,
        COUNT(DISTINCT uc.user_id) AS retained_users
    FROM user_cohorts uc
    LEFT JOIN user_activity ua ON uc.user_id = ua.user_id
    WHERE ua.activity_month >= uc.cohort_month
    GROUP BY 1, 2, 3
)
SELECT 
    r.cohort_month,
    r.acquisition_channel,
    r.period_month,
    r.retained_users,
    cs.cohort_size,
    ROUND(r.retained_users::numeric / cs.cohort_size, 4) AS retention_rate
FROM retention r
JOIN cohort_sizes cs ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.period_month;