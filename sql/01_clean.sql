-- Rules are ordered and mutually exclusive: every raw row receives one reason.
CREATE OR REPLACE TABLE classified_trips AS
WITH enriched AS (
    SELECT r.*, z.Zone AS zone, z.Borough AS borough,
        date_diff('second', tpep_pickup_datetime, tpep_dropoff_datetime)/60.0 AS duration_minutes
    FROM raw_trips r LEFT JOIN zones z ON r.PULocationID = z.LocationID
)
SELECT *, CASE
    WHEN tpep_pickup_datetime IS NULL OR tpep_pickup_datetime < TIMESTAMP '2025-01-01'
      OR tpep_pickup_datetime >= TIMESTAMP '2025-02-01' THEN 'outside_pickup_month'
    WHEN tpep_dropoff_datetime IS NULL OR duration_minutes <= 0 THEN 'invalid_duration'
    WHEN trip_distance IS NULL OR NOT isfinite(trip_distance) OR trip_distance <= 0 THEN 'invalid_distance'
    WHEN fare_amount IS NULL OR total_amount IS NULL OR NOT isfinite(fare_amount)
      OR NOT isfinite(total_amount) OR fare_amount <= 0 OR total_amount <= 0 THEN 'nonpositive_or_missing_money'
    WHEN borough IS NULL OR borough NOT IN ('Manhattan','Brooklyn','Queens','Bronx','Staten Island') THEN 'unknown_or_non_nyc_pickup'
    WHEN duration_minutes > 180 THEN 'duration_over_180_minutes'
    WHEN trip_distance / (duration_minutes/60.0) > 100 THEN 'speed_over_100_mph'
    ELSE 'retained' END AS exclusion_reason
FROM enriched;
CREATE OR REPLACE TABLE clean_trips AS
SELECT *, CAST(tpep_pickup_datetime AS DATE) AS pickup_date,
    hour(tpep_pickup_datetime) AS pickup_hour,
    CASE WHEN isodow(tpep_pickup_datetime) IN (6,7) THEN 'Weekend' ELSE 'Weekday' END AS day_type
FROM classified_trips WHERE exclusion_reason = 'retained';
