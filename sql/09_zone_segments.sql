SELECT PULocationID AS location_id, zone, borough, day_type, pickup_hour,
       count(*) AS trips, sum(fare_amount) AS fare_revenue
FROM clean_trips GROUP BY 1,2,3,4,5 ORDER BY trips DESC,location_id,day_type,pickup_hour;
