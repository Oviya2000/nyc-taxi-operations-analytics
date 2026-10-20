SELECT payment_type, count(*) AS trips, sum(fare_amount) AS fare_revenue,
       CASE WHEN payment_type=1 THEN sum(tip_amount)/nullif(sum(fare_amount),0)*100 END AS recorded_card_tip_pct_base_fare
FROM clean_trips GROUP BY 1 ORDER BY 1;
