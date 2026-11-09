"""SQL Crack v1.0.5 (Beta) local HTTP smoke tests. Run: python -m unittest discover -s tests -v"""
import importlib.util
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('sql_crack_server', ROOT / 'server.py')
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class SmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        app.DATA = Path(cls.temp.name)
        app.DUMPS = app.DATA / 'dumps'
        app.LOG_FILE = app.DATA / 'events.jsonl'
        app.setup()
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.port = cls.http.server_port
        cls.root = f'http://127.0.0.1:{cls.port}'
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join(timeout=3)
        cls.temp.cleanup()

    def get(self, route, headers=None):
        req = urllib.request.Request(self.root + route, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                return res.status, res.read(), dict(res.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(e.headers)

    def post(self, route, data, ctype='application/json', headers=None):
        req = urllib.request.Request(self.root + route, data=json.dumps(data).encode(),
                                     headers={'Content-Type': ctype, **(headers or {})}, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=5) as res:
                return res.status, json.load(res)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_01_health(self):
        code, body, _ = self.get('/api/health')
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)['version'], 'v1.0.5 (Beta)')

    def test_02_static_files(self):
        for name in ('/', '/index.html', '/style.css', '/app.js', '/assets/sql-crack-logo.png'):
            code, data, _ = self.get(name)
            self.assertEqual(code, 200, name)
            self.assertGreater(len(data), 0)

    def test_03_path_traversal_blocked(self):
        code, _, _ = self.get('/data/events.jsonl')
        self.assertEqual(code, 404)
        code, _, _ = self.get('/assets/../server.py')
        self.assertEqual(code, 404)

    def test_04_missing_content_type(self):
        code, data = self.post('/api/run', {'target':'demo-app','scenario':'baseline'},'text/plain')
        self.assertEqual(code, 415)
        self.assertFalse(data['ok'])

    def test_05_origin_guard(self):
        code, data = self.post('/api/run', {'target':'demo-app','scenario':'baseline'},headers={'Origin':'http://example.com'})
        self.assertEqual(code, 403)

    def test_06_validation(self):
        code, data = self.post('/api/run', {'target':'https://example.com','scenario':'baseline'})
        self.assertEqual(code, 400)
        self.assertFalse(data['ok'])

    def test_07_run_persistence(self):
        code, data = self.post('/api/run', {'target':'demo-app','scenario':'baseline','input':'hello'})
        self.assertEqual(code, 200)
        self.assertTrue(data['ok'])
        code, body, _ = self.get('/api/state')
        self.assertEqual(code, 200)
        self.assertGreaterEqual(len(json.loads(body)['logs']), 1)
        self.assertNotIn('"hello"', app.LOG_FILE.read_text(encoding='utf-8'))

    def test_08_dump_lifecycle(self):
        code, data = self.post('/api/run', {'target':'training-box','scenario':'dump','input':''})
        self.assertEqual(code, 200)
        name = data['dump']
        self.assertTrue(name.endswith('.sql'))
        code, body, _ = self.get('/api/dump?name=' + name)
        self.assertEqual(code, 200)
        self.assertIn(b'SIMULATION ONLY', body)
        code, data = self.post('/api/dumps/delete', {'name':name})
        self.assertEqual(code, 200)
        code, body, _ = self.get('/api/dump?name='+name)
        self.assertEqual(code, 404)

    def test_09_invalid_dump_name(self):
        code, body, _ = self.get('/api/dump?name=..%2Fserver.py')
        self.assertEqual(code, 400)

    def test_10_export(self):
        code, body, headers = self.get('/api/export?format=json')
        self.assertEqual(code, 200)
        self.assertEqual(json.loads(body)['version'], 'v1.0.5 (Beta)')
        code, body, headers = self.get('/api/export?format=csv')
        self.assertEqual(code, 200)
        self.assertIn(b'input_length', body)

    def test_12_safe_probe_self(self):
        code, result = self.post('/api/safe-probe', {
            'url': self.root + '/api/health', 'count': 2, 'confirmed': True
        })
        self.assertEqual(code, 200, result)
        self.assertEqual(len(result['report']['checks']), 2)
        self.assertNotEqual(result['report']['checks'][0]['param'], result['report']['checks'][1]['param'])
        self.assertTrue(all(x['status'] == 200 for x in result['report']['checks']))
        code, raw, _ = self.get('/api/state')
        self.assertTrue(any(x.get('scenario_key') == 'safe-probe' for x in json.loads(raw)['logs']))

    def test_13_safe_probe_denied_without_consent(self):
        code, result = self.post('/api/safe-probe', {'url':self.root+'/api/health', 'count':1, 'confirmed':False})
        self.assertEqual(code, 400)
        self.assertFalse(result['ok'])

    def test_14_safe_probe_denied_out_of_scope(self):
        code, result = self.post('/api/safe-probe', {'url':'https://example.com/', 'count':1, 'confirmed':True})
        self.assertEqual(code, 400)
        self.assertFalse(result['ok'])

    def test_15_safe_probe_limits(self):
        for count in (0, 4, -1, True, '3'):
            code, _ = self.post('/api/safe-probe', {'url':self.root+'/api/health', 'count':count, 'confirmed':True})
            self.assertEqual(code, 400)

    def test_16_monitor(self):
        code, raw, _ = self.get('/api/monitor')
        self.assertEqual(code, 200)
        monitor = json.loads(raw)['monitor']
        self.assertTrue(monitor['online'])
        self.assertGreaterEqual(monitor['requests_total'], 1)
        self.assertGreaterEqual(monitor['uptime_seconds'], 0)
        self.assertIsInstance(monitor['average_local_ms'], (int,float))

    def test_17_reports(self):
        code, raw, _ = self.get('/api/reports')
        self.assertEqual(code, 200)
        report = json.loads(raw)['report']
        self.assertEqual(report['window_hours'], 24)
        self.assertIn('previous',report)
        self.assertIn('current',report)
        self.assertIn('event_delta',report)

    def test_18_safety_blocked_attempt(self):
        code, rejected = self.post('/api/safe-probe', {
            'url': 'https://invalid-allowlist.example/health', 'count': 1, 'confirmed': True
        })
        self.assertEqual(code, 400)
        code, raw, _ = self.get('/api/safety')
        self.assertEqual(code, 200)
        safety = json.loads(raw)['safety']
        self.assertGreaterEqual(safety['blocked_last_hour'], 1)
        self.assertEqual(safety['status'], 'UYARI')
        self.assertTrue(safety['scope_valid'])
        self.assertIn('remaining',safety['rate_limit'])

    def test_19_safe_probe_aggregate_stats(self):
        code, result = self.post('/api/safe-probe', {
            'url': self.root + '/api/health', 'count': 1, 'confirmed': True
        })
        self.assertEqual(code, 200, result)
        stats = result['event']['probe_stats']
        self.assertEqual(stats['requests'], 1)
        self.assertEqual(stats['successes'], 1)
        self.assertEqual(stats['failures'], 0)
        self.assertGreaterEqual(stats['avg_ms'], 0)
        code, raw, _ = self.get('/api/reports')
        self.assertGreaterEqual(json.loads(raw)['report']['current']['checks'], 1)

    def test_20_frontend_panels(self):
        code, raw, _ = self.get('/index.html')
        self.assertEqual(code, 200)
        page = raw.decode('utf-8')
        for feature in ('id="monitor"', 'id="reports"', 'id="safety"', '32 Özellik'):
            self.assertIn(feature,page)

    def test_11_clear(self):
        code, data = self.post('/api/clear', {})
        self.assertEqual(code, 200)
        code, body, _ = self.get('/api/state')
        self.assertEqual(json.loads(body)['logs'], [])

    def test_21_malformed_historical_logs(self):
        # Corrupted/legacy fields must not take down reports or the main UI.
        import datetime
        t = datetime.datetime.now(datetime.timezone.utc).isoformat()
        with app.LOCK:
            with app.LOG_FILE.open('a', encoding='utf-8') as fp:
                fp.write('this is not json\n')
                fp.write(json.dumps({'time': t, 'scenario_key':'safe-probe',
                    'scenario':['unexpected','type'], 'level':'INFO',
                    'probe_stats':{'requests': 'bad', 'successes': None, 'avg_ms': 'NaN'}}) + '\n')
                fp.write(json.dumps({'time': t, 'scenario_key':'safe-probe',
                    'scenario': None, 'probe_stats': ['not-a-dict']}) + '\n')
        for route in ('/api/state','/api/reports','/api/safety'):
            code, data, _ = self.get(route)
            self.assertEqual(code, 200, (route,data[:150]))
            self.assertTrue(json.loads(data)['ok'])

    def test_22_dump_cleanup_after_log_failure(self):
        before = {x['name'] for x in app.dump_listing()}
        with patch.object(app, 'append_log', side_effect=PermissionError('readonly')):
            code, body = self.post('/api/run', {'target':'demo-app','scenario':'dump','input':''})
        self.assertEqual(code, 500)
        self.assertFalse(body['ok'])
        after = {x['name'] for x in app.dump_listing()}
        self.assertEqual(after, before)

    def test_23_clear_permission_failure(self):
        with patch.object(Path, 'write_text', side_effect=PermissionError('readonly')):
            code, body = self.post('/api/clear', {})
        self.assertEqual(code, 500)
        self.assertFalse(body['ok'])

    def test_24_dump_delete_permission_failure(self):
        filename = app.generate_dump()
        try:
            with patch.object(Path, 'unlink', side_effect=PermissionError('readonly')):
                code, body = self.post('/api/dumps/delete', {'name':filename})
            self.assertEqual(code, 500)
            self.assertFalse(body['ok'])
        finally:
            (app.DUMPS / filename).unlink(missing_ok=True)

    def test_25_malformed_fields_reported_without_crash(self):
        from insights import build_report
        import datetime
        stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        r = build_report([{'time':stamp, 'scenario':'Safe', 'scenario_key':'safe-probe',
                          'probe_stats':{'requests':2, 'successes':99,
                                         'failures':999, 'avg_ms':float('nan')}}])
        self.assertEqual(r['current']['checks'],2)
        self.assertEqual(r['current']['successful_checks'],2)
        self.assertEqual(r['current']['failed_checks'],0)
        self.assertEqual(r['current']['avg_probe_ms'],0)

    def test_26_log_read_errors_return_json(self):
        for route in ('/api/state', '/api/reports', '/api/safety', '/api/export?format=json'):
            with self.subTest(route=route):
                with patch.object(app, 'read_logs', side_effect=PermissionError('denied')):
                    code, raw, _ = self.get(route)
                self.assertEqual(code, 500)
                self.assertFalse(json.loads(raw)['ok'])

    def test_27_static_read_errors_return_json(self):
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('denied')):
            code, raw, _ = self.get('/index.html')
        self.assertEqual(code, 500)
        self.assertFalse(json.loads(raw)['ok'])

    def test_28_server_version_header(self):
        code, raw, headers = self.get('/api/health')
        self.assertEqual(code, 200)
        self.assertIn('SQLCrack/v1.0.5 (Beta)', headers.get('Server', ''))

if __name__ == '__main__':
    unittest.main()
