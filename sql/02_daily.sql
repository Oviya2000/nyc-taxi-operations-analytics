WITH daily AS (
 SELECT pickup_date, count(*) AS trips, sum(fare_amount) AS fare_revenue,
        sum(total_amount) AS passenger_charges, avg(duration_minutes) AS avg_duration
 FROM clean_trips GROUP BY 1
)
SELECT *, trips - lag(trips) OVER (ORDER BY pickup_date) AS trips_change,
       avg(trips) OVER (ORDER BY pickup_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_7_day_trips
FROM daily ORDER BY pickup_date;
