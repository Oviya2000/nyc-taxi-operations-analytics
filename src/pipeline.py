"""Download official TLC inputs, run auditable SQL, and publish portfolio outputs."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request
import duckdb

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'yellow_tripdata_2025-01.parquet': 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet',
    'taxi_zone_lookup.csv': 'https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv',
}

def download_inputs():
    raw = ROOT / 'data/raw'
    raw.mkdir(parents=True, exist_ok=True)
    for name, url in SOURCES.items():
        target = raw / name
        if not target.exists():
            temp = target.with_suffix(target.suffix + '.part')
            print(f'Downloading {name}', flush=True)
            with urllib.request.urlopen(url, timeout=120) as response, temp.open('wb') as output:
                while block := response.read(1024 * 1024):
                    output.write(block)
            temp.replace(target)
    return [{'filename': n, 'url': u, 'bytes': (raw/n).stat().st_size,
             'sha256': hashlib.sha256((raw/n).read_bytes()).hexdigest()} for n,u in SOURCES.items()]

def build(database=':memory:'):
    con = duckdb.connect(database)
    con.execute("SET threads=2")
    raw = ROOT / 'data/raw'
    con.execute('CREATE OR REPLACE TABLE raw_trips AS SELECT * FROM read_parquet(?)', [str(raw/'yellow_tripdata_2025-01.parquet')])
    con.execute('CREATE OR REPLACE TABLE zones AS SELECT * FROM read_csv_auto(?)', [str(raw/'taxi_zone_lookup.csv')])
    con.execute((ROOT/'sql/01_clean.sql').read_text())
    return con

def rows(con, query):
    result = con.execute(query)
    keys = [c[0] for c in result.description]
    return [dict(zip(keys, row)) for row in result.fetchall()]

def publish(con, manifest):
    reports = ROOT/'reports'
    reports.mkdir(exist_ok=True)
    exports = {}
    for queryfile in sorted((ROOT/'sql').glob('0[2-9]_*.sql')):
        name = queryfile.stem[3:]
        query = queryfile.read_text().strip().rstrip(';')
        exports[name] = rows(con, query)
        target = reports/f'{name}.csv'
        # Paths are repository-controlled; parameters cannot bind COPY targets.
        con.execute(f"COPY ({query}) TO '{target.as_posix()}' (HEADER, DELIMITER ',')")
    summary = rows(con, 'SELECT count(*) AS trips, sum(fare_amount) AS fare_revenue, sum(total_amount) AS passenger_charges, avg(duration_minutes) AS avg_duration, avg(trip_distance) AS avg_distance FROM clean_trips')[0]
    audit = rows(con, 'SELECT exclusion_reason, count(*) AS records FROM classified_trips GROUP BY 1 ORDER BY records DESC')
    data = {'period':'January 2025', 'summary': summary, 'audit': audit, 'sources':manifest, 'exports':exports}
    text = json.dumps(data, default=str, separators=(',', ':'), allow_nan=False)
    (reports/'analysis.json').write_text(json.dumps(data, default=str, indent=2, allow_nan=False))
    template = (ROOT/'src/dashboard.html').read_text()
    (ROOT/'dashboard/index.html').write_text(template.replace('__ANALYSIS_DATA__', text))
    (reports/'source_manifest.json').write_text(json.dumps(manifest, indent=2))
    generate_findings(data)
    print(json.dumps({'summary':summary, 'audit':audit},default=str,indent=2))

def generate_findings(data):
    ex = data['exports']
    top = ex['zones'][0]
    hours = sorted(ex['hours'], key=lambda r:r['trips'], reverse=True)
    excluded = sum(r['records'] for r in data['audit'] if r['exclusion_reason'] != 'retained')
    raw = sum(r['records'] for r in data['audit'])
    daily = ex['daily']
    busiest = max(daily,key=lambda r:r['trips'])
    summary = data['summary']
    report = f'''# Findings | January 2025

This retrospective analysis covers the complete official January file, filtered to pickup dates in January and the documented valid-trip cohort. It measures observed yellow-taxi activity, not unmet demand or fleet profitability.

## Results

- **{summary['trips']:,} retained trips** and **${summary['fare_revenue']:,.0f} in recorded base fares**. Base fares exclude tips, taxes, tolls, and surcharges; they are not net income.
- **{top['zone']}** leads pickup zones with **{top['trips']:,} trips**, representing **{top['trip_share_pct']:.2f}%** of the retained cohort. Review the top-zone table before designing a location-specific staffing pilot.
- The busiest pickup hour is **{hours[0]['pickup_hour']:02d}:00–{hours[0]['pickup_hour']:02d}:59**, with **{hours[0]['trips']:,} trips** across the month. Use the dashboard's borough and day-type filters to check whether this pattern holds locally.
- The busiest pickup date is **{busiest['pickup_date']}**, with **{busiest['trips']:,} trips**. A single month's calendar and weather can influence the pattern; do not extrapolate it to the entire year.
- **{excluded:,} of {raw:,} input records ({100*excluded/raw:.2f}%)** were excluded under mutually exclusive, ordered rules. See `quality.csv` for the audit and `docs/methodology.md` for interpretation.

## Recommended next decision

Use the highest-activity zone/hour combinations to select a small dispatch pilot. Compare a treatment area with a comparable control over multiple weeks. Evaluate trips per available vehicle-hour, passenger wait time, and driver earnings after costs. Those outcomes require dispatch, availability, and expense data absent from TLC trip records. This analysis alone cannot establish that shifting vehicles improves results.

## Limitations and sensitivity

The cleaning cohort excludes zero-distance trips, nonpositive fares/charges, durations outside (0, 180] minutes, implausible average speeds above 100 mph, and unknown/non-NYC pickup zones. These are analytical choices, not official TLC validity rules. `sensitivity.csv` compares key totals before and after the optional duration/speed filters. Refunds and adjustments require a separate financial audit. Payment types are kept separate; card tips cannot represent cash tipping. Exact duplicates are retained because TLC provides no unique trip ID that would prove two identical rows are the same trip.

All numeric statements above are generated from the SQL outputs by `src/pipeline.py`. No business impact or hiring outcome is claimed.
'''
    (ROOT/'reports/findings.md').write_text(report)

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--skip-download', action='store_true', help='Use previously downloaded inputs')
    args=parser.parse_args()
    if args.skip_download:
        manifest=[{'filename':n,'url':u,'bytes':(ROOT/'data/raw'/n).stat().st_size,'sha256':hashlib.sha256((ROOT/'data/raw'/n).read_bytes()).hexdigest()} for n,u in SOURCES.items()]
    else:
        manifest=download_inputs()
    con=build()
    publish(con,manifest)
