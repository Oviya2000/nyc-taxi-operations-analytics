"""Boundary and reconciliation checks. No network required for unit tests."""
from pathlib import Path
import json
import unittest
import duckdb

ROOT=Path(__file__).resolve().parents[1]

class CleaningTests(unittest.TestCase):
    def setUp(self):
        self.con=duckdb.connect()
        self.con.execute('CREATE TABLE zones(LocationID INTEGER, Zone VARCHAR, Borough VARCHAR)')
        self.con.execute("INSERT INTO zones VALUES (1,'Example','Manhattan'), (2,'Unknown','Unknown')")
        self.con.execute('''CREATE TABLE raw_trips(tpep_pickup_datetime TIMESTAMP,
            tpep_dropoff_datetime TIMESTAMP, trip_distance DOUBLE, fare_amount DOUBLE,
            total_amount DOUBLE, PULocationID INTEGER)''')

    def tearDown(self):
        self.con.close()

    def add(self, pickup='2025-01-04 12:00:00', dropoff='2025-01-04 12:30:00', distance=5, fare=20, total=25, zone=1):
        self.con.execute('INSERT INTO raw_trips VALUES (?, ?, ?, ?, ?, ?)',[pickup,dropoff,distance,fare,total,zone])

    def clean(self):
        self.con.execute((ROOT/'sql/01_clean.sql').read_text())
        return self.con.execute('SELECT exclusion_reason FROM classified_trips').fetchall()

    def test_duplicate_rows_retained_and_weekend_derived(self):
        self.add(); self.add()
        self.clean()
        self.assertEqual(self.con.execute('SELECT count(*), min(day_type) FROM clean_trips').fetchone(),(2,'Weekend'))

    def test_month_boundary_and_null_pickup(self):
        self.add(pickup=None);self.add(pickup='2025-02-01 00:00:00')
        self.assertEqual(self.clean(),[('outside_pickup_month',)]*2)

    def test_invalid_duration(self):
        self.add(dropoff=None);self.add(dropoff='2025-01-04 11:59:59')
        self.assertEqual(self.clean(),[('invalid_duration',)]*2)

    def test_nonfinite_distance_and_money(self):
        self.add(distance=float('nan'));self.add(distance=float('inf'));self.add(fare=float('inf'));self.add(total=None)
        self.assertEqual(self.clean(),[('invalid_distance',),('invalid_distance',),('nonpositive_or_missing_money',),('nonpositive_or_missing_money',)])

    def test_ordered_rules_and_unknown_zone(self):
        self.add(distance=0,fare=-1);self.add(zone=999);self.add(zone=2)
        self.assertEqual(self.clean(),[('invalid_distance',),('unknown_or_non_nyc_pickup',),('unknown_or_non_nyc_pickup',)])

    def test_duration_and_speed_boundaries(self):
        self.add(dropoff='2025-01-04 15:00:00')
        self.add(dropoff='2025-01-04 15:00:01')
        self.add(distance=50);self.add(distance=50.01)
        self.assertEqual(self.clean(),[('retained',),('duration_over_180_minutes',),('retained',),('speed_over_100_mph',)])

class PublishedOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/'reports/analysis.json'
        if not path.exists():
            raise unittest.SkipTest('Run pipeline to enable published-output reconciliation')
        cls.data=json.loads(path.read_text())

    def test_all_aggregates_reconcile(self):
        d=self.data;s=d['summary']
        for name in ['daily','zones','hours','cube','payments','zone_segments']:
            with self.subTest(export=name):
                self.assertEqual(sum(r['trips'] for r in d['exports'][name]),s['trips'])
                self.assertAlmostEqual(sum(r['fare_revenue'] for r in d['exports'][name]),s['fare_revenue'],places=2)
        self.assertEqual(next(r['records'] for r in d['audit'] if r['exclusion_reason']=='retained'),s['trips'])

    def test_each_filter_combination_reconciles_zone_and_cube(self):
        ex=self.data['exports']
        for borough in {r['borough'] for r in ex['cube']}:
            for day in ['Weekday','Weekend']:
                selected=lambda r:r['borough']==borough and r['day_type']==day
                self.assertEqual(sum(r['trips'] for r in ex['cube'] if selected(r)),sum(r['trips'] for r in ex['zone_segments'] if selected(r)))
                self.assertAlmostEqual(sum(r['fare_revenue'] for r in ex['cube'] if selected(r)),sum(r['fare_revenue'] for r in ex['zone_segments'] if selected(r)),places=2)

    def test_share_dates_and_sensitivity(self):
        ex=self.data['exports']
        self.assertAlmostEqual(sum(r['trip_share_pct'] for r in ex['zones']),100,places=6)
        self.assertEqual(len(ex['daily']),31)
        self.assertTrue(all(r['pickup_date'].startswith('2025-01-') for r in ex['daily']))
        core,final=ex['sensitivity']
        self.assertGreaterEqual(core['trips'], final['trips'])
        self.assertEqual(final['trips'], self.data['summary']['trips'])

if __name__=='__main__':
    unittest.main()
