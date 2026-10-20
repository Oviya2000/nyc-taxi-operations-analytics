SELECT 'Core cohort before duration/speed caps' AS cohort, count(*) AS trips,
       sum(fare_amount) AS fare_revenue
FROM classified_trips
WHERE exclusion_reason IN ('retained','duration_over_180_minutes','speed_over_100_mph')
UNION ALL
SELECT 'Final cohort with duration/speed caps', count(*), sum(fare_amount) FROM clean_trips;
