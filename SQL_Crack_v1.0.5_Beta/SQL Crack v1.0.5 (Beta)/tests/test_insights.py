"""Standalone unit tests for read-only reporting and safety logic."""
import unittest
from datetime import datetime, timedelta, timezone
from insights import build_report, build_safety


class InsightTests(unittest.TestCase):
    def test_compare_24_hour_windows(self):
        t = datetime(2026,11,8,12,0,tzinfo=timezone.utc)
        def record(h, name, severity="INFO"):
            return {"time":(t-timedelta(hours=h)).isoformat(),"scenario":name,"level":severity}
        report = build_report([record(3,"baseline"),record(7,"quote","WARNING"),record(32,"baseline")], at=t)
        self.assertEqual(report['current']['events'], 2)
        self.assertEqual(report['previous']['events'], 1)
        self.assertEqual(report['event_delta'], 1)
        self.assertEqual(report['current']['warnings'], 1)

    def test_weighted_latency_and_success_rate(self):
        t = datetime.now(timezone.utc).isoformat()
        logs = [
            {"time":t,"scenario_key":"safe-probe","scenario":"HTTP","probe_stats":{"requests":2,"successes":2,"failures":0,"avg_ms":20}},
            {"time":t,"scenario_key":"safe-probe","scenario":"HTTP","probe_stats":{"requests":1,"successes":0,"failures":1,"avg_ms":80}}
        ]
        s = build_report(logs)['current']
        self.assertEqual(s['checks'], 3)
        self.assertEqual(s['successful_checks'], 2)
        self.assertEqual(s['success_percent'], 66.7)
        self.assertEqual(s['avg_probe_ms'],40)

    def test_alert_after_two_consecutive_failures(self):
        logs = [{"scenario_key":"safe-probe","probe_stats":{"requests":1,"successes":0,"failures":1}} for _ in range(2)]
        s = build_safety(logs,0,{"remaining":5,"used":1,"limit_per_minute":6},{"valid":True,"approved_count":0})
        self.assertEqual(s['status'],'UYARI')
        self.assertEqual(s['consecutive_failed_probes'],2)

    def test_safety_no_alerts(self):
        s = build_safety([],0,{"remaining":6,"used":0,"limit_per_minute":6},{"valid":True,"approved_count":0})
        self.assertEqual(s['status'],'KORUNUYOR')
        self.assertEqual(s['alerts'],[])


if __name__ == '__main__':
    unittest.main()
