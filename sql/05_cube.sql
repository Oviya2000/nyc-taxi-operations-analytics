-- Additive measures support weighted recalculation under dashboard filters.
SELECT pickup_date, pickup_hour, day_type, borough, count(*) AS trips,
       sum(fare_amount) AS fare_revenue, sum(total_amount) AS passenger_charges,
       sum(duration_minutes) AS duration_minutes, sum(trip_distance) AS distance_miles
FROM clean_trips GROUP BY 1,2,3,4 ORDER BY 1,2,4;
