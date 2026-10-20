SELECT PULocationID AS location_id, zone, borough, count(*) AS trips,
       sum(fare_amount) AS fare_revenue, avg(fare_amount) AS avg_fare,
       100.0 * count(*) / sum(count(*)) OVER () AS trip_share_pct,
       dense_rank() OVER (ORDER BY count(*) DESC) AS activity_rank
FROM clean_trips GROUP BY 1,2,3 ORDER BY trips DESC, location_id;
