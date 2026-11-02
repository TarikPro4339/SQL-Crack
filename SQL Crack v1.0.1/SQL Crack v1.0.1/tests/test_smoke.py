"""SQL Crack v1.0.1 local HTTP smoke tests. Run: python -m unittest discover -s tests -v"""
import importlib.util
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

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
        self.assertEqual(json.loads(body)['version'], 'v1.0.1')

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
        self.assertEqual(json.loads(body)['version'], 'v1.0.1')
        code, body, headers = self.get('/api/export?format=csv')
        self.assertEqual(code, 200)
        self.assertIn(b'input_length', body)

    def test_11_clear(self):
        code, data = self.post('/api/clear', {})
        self.assertEqual(code, 200)
        code, body, _ = self.get('/api/state')
        self.assertEqual(json.loads(body)['logs'], [])

if __name__ == '__main__':
    unittest.main()
