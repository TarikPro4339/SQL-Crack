"""Regression: every v1.0.5 (Beta) instance includes the Beta suffix."""
from pathlib import Path
import re
import unittest
import server

ROOT = Path(__file__).resolve().parents[1]
class BetaEverywhereTests(unittest.TestCase):
    def test_exact_version_everywhere(self):
        self.assertEqual(server.VERSION, 'v1.0.5 (Beta)')
        self.assertEqual(server.DISPLAY_VERSION, 'v1.0.5 (Beta)')
        self.assertEqual(server.Handler.server_version, 'SQLCrack/v1.0.5 (Beta)')
        self.assertEqual(ROOT.name, 'SQL Crack v1.0.5 (Beta)')
        for path in ROOT.rglob('*'):
            if path.is_dir() or '__pycache__' in path.parts:
                continue
            self.assertNotRegex(path.name, r'v1\.0\.5(?! \(Beta\))')
            if path.suffix.lower() in {'.md', '.txt', '.py', '.js', '.html', '.css', '.json', '.bat'}:
                content=path.read_text(encoding='utf-8-sig')
                self.assertNotRegex(content, r'v1\.0\.5(?! \(Beta\))', str(path))
