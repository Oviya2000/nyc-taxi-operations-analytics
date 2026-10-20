# Understand the project before presenting it

This is a study guide, not a claim about work you personally completed. Run the pipeline, change at least one analytical choice, and inspect the results before using the project in interviews.

## Explain the business question

The hypothetical stakeholder is a taxi fleet operations manager. The goal is to identify observed pickup patterns and select a dispatch experiment. The records cannot identify passengers unable to find a taxi, vehicle availability, or net profit.

## Be ready to answer

1. **Why DuckDB?** It queries Parquet locally with SQL and avoids a database-server setup for this one-month, read-heavy analytical workload. Reviewers can inspect the same SQL that generates the dashboard.
2. **Why left join the zone lookup?** It preserves raw rows long enough to audit unmatched zone identifiers instead of silently dropping them through an inner join.
3. **Why not remove exact duplicates?** The data does not provide a unique trip ID for this analysis. Identical fields alone do not prove a duplicate transaction.
4. **Why ordered exclusion reasons?** Every input row has one reason, so audit categories add to the full input count. Counts are first-failure counts, not counts of every data issue.
5. **Why weighted averages?** An average of borough/hour averages gives small groups too much weight. The cube carries sums and counts so the dashboard recalculates ratios correctly after filtering.
6. **What did the sensitivity check establish?** It quantifies how the duration/speed caps affect trip and fare totals. It does not prove those caps identify all erroneous records.
7. **Why avoid cash/card tip comparisons?** The source records credit-card tips but not cash tips. A recorded zero cash tip is not evidence that no tip was paid.
8. **How would you measure business impact?** Run a controlled pilot with available-vehicle hours, wait times, and costs. Evaluate outcomes rather than assuming a high-volume zone is undersupplied.
9. **What would you extend?** Compare several months, normalize day-type counts by days observed, investigate refund/adjustment records, and add operational availability data.

## A useful hands-on exercise

Change the 180-minute cap to 120 in the cleaning SQL. Rebuild, compare the quality/sensitivity outputs, and explain whether your conclusions change. Then restore the documented policy or update the methodology to match your chosen final definition.

## Honest résumé scope

After you have independently run and understood the work, describe the components you can explain: analysis of official trip records, SQL-based metrics, transparent cleaning, dashboard filters, and reconciliation tests. Do not claim revenue growth, reduced wait times, deployed Power BI reports, or sole unaided authorship without evidence.
