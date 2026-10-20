SELECT pickup_hour, count(*) AS trips, sum(fare_amount) AS fare_revenue,
       avg(duration_minutes) AS avg_duration
FROM clean_trips GROUP BY 1 ORDER BY 1;
