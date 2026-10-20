# Findings | January 2025

This retrospective analysis covers the complete official January file, filtered to pickup dates in January and the documented valid-trip cohort. It measures observed yellow-taxi activity, not unmet demand or fleet profitability.

## Results

- **3,242,053 retained trips** and **$59,019,659 in recorded base fares**. Base fares exclude tips, taxes, tolls, and surcharges; they are not net income.
- **Midtown Center** leads pickup zones with **161,227 trips**, representing **4.97%** of the retained cohort. Review the top-zone table before designing a location-specific staffing pilot.
- The busiest pickup hour is **18:00–18:59**, with **235,753 trips** across the month. Use the dashboard's borough and day-type filters to check whether this pattern holds locally.
- The busiest pickup date is **2025-01-25**, with **128,717 trips**. A single month's calendar and weather can influence the pattern; do not extrapolate it to the entire year.
- **233,173 of 3,475,226 input records (6.71%)** were excluded under mutually exclusive, ordered rules. See `quality.csv` for the audit and `docs/methodology.md` for interpretation.

## Recommended next decision

Use the highest-activity zone/hour combinations to select a small dispatch pilot. Compare a treatment area with a comparable control over multiple weeks. Evaluate trips per available vehicle-hour, passenger wait time, and driver earnings after costs. Those outcomes require dispatch, availability, and expense data absent from TLC trip records. This analysis alone cannot establish that shifting vehicles improves results.

## Limitations and sensitivity

The cleaning cohort excludes zero-distance trips, nonpositive fares/charges, durations outside (0, 180] minutes, implausible average speeds above 100 mph, and unknown/non-NYC pickup zones. These are analytical choices, not official TLC validity rules. `sensitivity.csv` compares key totals before and after the optional duration/speed filters. Refunds and adjustments require a separate financial audit. Payment types are kept separate; card tips cannot represent cash tipping. Exact duplicates are retained because TLC provides no unique trip ID that would prove two identical rows are the same trip.

All numeric statements above are generated from the SQL outputs by `src/pipeline.py`. No business impact or hiring outcome is claimed.
