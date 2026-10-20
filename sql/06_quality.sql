SELECT exclusion_reason, count(*) AS records,
       100.0*count(*)/sum(count(*)) OVER () AS pct_input
FROM classified_trips GROUP BY 1 ORDER BY records DESC;
