# Validation record

Validated locally on 2026-10-20 with Python 3.12, DuckDB 1.4.1, and Playwright 1.51.0 / Chromium 134.

- Full official January 2025 source file downloaded and processed: 3,475,226 rows.
- 3,242,053 rows retained; mutually exclusive exclusions total 233,173.
- Nine Python tests passed, covering cleaning boundaries, nonfinite values, exclusions, duplicate retention, aggregate totals, filter reconciliation, calendar scope, and sensitivity consistency.
- Browser checks passed for all 18 borough/day-type combinations, measure switching, filtered CSV count reconciliation, no JavaScript page errors, and no horizontal page overflow at 390 px.
- Desktop and mobile dashboard layouts inspected using transient QA screenshots. The static analysis preview was rendered separately with Matplotlib from published outputs.
- Power BI Desktop was unavailable; DAX/model instructions have not been executed there. No `.pbix` deliverable is claimed.
- GitHub Actions configuration is supplied. A remote workflow run cannot be claimed until the repository is published and GitHub executes it.

Reproduce the checks using the commands in the README. Local testing does not establish business impact or guarantee all source records are accurate.
