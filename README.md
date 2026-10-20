# Power BI build guide

The working deliverable is `dashboard/index.html`. This folder contains Power BI-ready CSVs/measure definitions **via the reports folder**, not a finished `.pbix` file. Power BI Desktop was not available in the build environment; the following manual steps have not been executed there.

1. Open Power BI Desktop → Get data → Text/CSV → import `reports/cube.csv` as **TripsCube**. Import `reports/zone_segments.csv` as **ZoneSegments** and `reports/quality.csv` as **Quality**.
2. Set `pickup_date` to Date, `pickup_hour` and `trips` to Whole Number, and monetary/quantity sums to Decimal Number. Set `location_id` to Whole Number. Keep leading-zero labels as text if you create them.
3. Create a borough dimension from distinct borough values and a day-type dimension from distinct day_type values. Add one-to-many, single-direction relationships from each dimension to both TripsCube and ZoneSegments. No fact-to-fact relationship is needed.
4. Add the measures in `measures.dax` one at a time to TripsCube. Add two ZoneSegments measures: `Zone Trips = SUM(ZoneSegments[trips])` and `Zone Base Fares = SUM(ZoneSegments[fare_revenue])`.
5. Add borough and day-type slicers using the dimension columns. Add cards for trips, base fares, average fare and duration. Add a daily line chart using TripsCube[pickup_date] and Recorded Trips; an hourly column chart using pickup_hour; and a top-10 zone bar chart using ZoneSegments[zone] and Zone Trips.
6. Add an unfiltered audit page from Quality. Do not relate Quality to the fact tables. Add the source attribution and cohort/metric notes from `docs/methodology.md`.
7. Reconcile the unfiltered cards with `reports/analysis.json`. Check each borough/day combination against the HTML dashboard. Format currency as USD, durations as minutes, and counts as whole numbers.

A date slicer cannot filter ZoneSegments because that export does not include dates. The default design intentionally uses only borough and day type. Extend the export grain and model first if you want consistent date filtering across all visuals.
