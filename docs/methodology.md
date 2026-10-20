# Methodology and metric contract

## Scope and stakeholder

A hypothetical yellow-taxi fleet operations manager wants to understand recorded activity by pickup zone, hour, and day type. The dataset is the **complete January 2025 yellow-taxi Parquet file**, not a sample, plus the official zone lookup. There is no vehicle identifier, dispatch capacity, rejected request, expense ledger, or experiment assignment in this analysis. Results describe trips, not driver performance or causal opportunity.

## Inputs and provenance

- Publisher: NYC Taxi & Limousine Commission (TLC).
- Landing page: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- Dictionary: https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf
- Exact source URLs, byte counts, and SHA-256 checksums: `reports/source_manifest.json`.
- Pickup/dropoff timestamps are interpreted as the source's local wall-clock timestamps; no timezone conversion is introduced.
- Raw bytes are deliberately excluded from Git. The deterministic downloader preserves the official format and writes downloads atomically. Delete local raw files to explicitly refresh a source; source files may be revised by the publisher.

## Cleaning and audit

`sql/01_clean.sql` left-joins pickup LocationID to the zone dimension and assigns each raw row exactly one exclusion reason, in this order:

1. Missing pickup timestamp or pickup outside January 2025.
2. Missing dropoff timestamp or nonpositive duration.
3. Missing, nonfinite, or nonpositive distance.
4. Missing, nonfinite, or nonpositive base fare or total charge.
5. Missing zone match, or pickup borough outside the five NYC boroughs.
6. Duration above 180 minutes.
7. Implied average speed above 100 mph.
8. Otherwise retained.

Duration is measured in seconds and divided by 60. A trip may end in February if it starts in January and passes the other rules. Each exclusion count represents the first failed rule, not all issues on that record. Missing passenger counts are not exclusion criteria because they do not prevent the defined metrics. Nonpositive charges are removed for this activity cohort; a financial audit would need to reconcile refunds and adjustments separately.

The duration and speed limits are transparent analyst-selected plausibility caps, not TLC rules. The sensitivity export compares the eligible core cohort with and without these two caps. Zero-distance trips, including potentially legitimate flat-fare or meter-adjustment records, are excluded explicitly. Exact duplicates are retained: absent a unique trip ID, matching fields do not prove duplication. Unknown/non-NYC pickup records are excluded even if their dropoff is in NYC.

## Metric definitions

| Metric | Definition | Interpretation |
|---|---|---|
| Recorded trips | Count of retained rows | Completed recorded activity; not total demand |
| Base fare revenue | Sum of `fare_amount` | Metered/base fares; not profit or net driver earnings |
| Passenger charges | Sum of `total_amount` | Recorded charges; not a reconciled cash-inclusive revenue ledger |
| Average base fare | Base fare revenue / trips | Trip-weighted average |
| Average duration | Sum of duration minutes / trips | Trip-weighted average |
| Trip share | Zone trips / all filtered trips | Denominator respects borough and day-type selection |
| 7-day rolling trips | SQL average of current and six preceding daily rows | First six dates have shorter windows |
| Card tip percentage | Sum card tips / sum card base fares × 100 | Restricted to payment type 1; not cash tipping |
| Day type | Saturday/Sunday = weekend | Holidays on weekdays remain weekdays |

Daily aggregates cover all 31 pickup dates in the source cohort. The dashboard leaves gaps for unselected day types rather than plotting them as zero activity. Hourly totals sum across the selected days and do not normalize for the number of weekdays versus weekend days. Use daily averages if comparing intensity across day types.

## Reproducibility and checks

The pipeline runs locally with pinned DuckDB, writes all CSVs, embeds the same results into the HTML dashboard, and generates the findings from actual query results. Raw data is needed to rebuild; the dashboard and committed CSVs work without a database or server. Tests cover cleaning boundaries, nonfinite values, ordered exclusions, duplicate policy, aggregate reconciliation, borough/day filter reconciliation, calendar scope, and sensitivity consistency. No fabricated records are mixed into published outputs. Unit-test fixtures are synthetic and isolated from the pipeline.

## Decision limitations

High observed volume does not imply an undersupplied location. Airport and Manhattan activity can reflect regulation, existing supply, or trip mix. There is no counterfactual to estimate the effect of moving taxis. Recommendations are hypotheses for a controlled operational pilot. January-only results may be seasonal and should be validated against additional months before committing resources.
