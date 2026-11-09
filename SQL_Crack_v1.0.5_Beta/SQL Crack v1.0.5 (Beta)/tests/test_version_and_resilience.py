"""Metadata / project version consistency tests."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
VERSION = "v1.0.5 (Beta)"

class VersionConsistencyTests(unittest.TestCase):
    def test_all_source_version_tokens(self):
        extensions = (".py", ".js", ".html", ".css", ".md", ".txt", ".bat", ".json")
        for file in ROOT.rglob("*"):
            if file.is_file() and file.suffix in extensions:
                data = file.read_text(encoding="utf-8-sig")
                for match in re.finditer(r"(?<![\w.])v?\d+\.\d+\.\d+(?![\w.])", data):
                    with self.subTest(file=file.name, value=match.group()):
                        self.assertEqual(match.group() + data[match.end():match.end()+7], VERSION)
    def test_visible_version(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(VERSION, html)
        self.assertIn(VERSION, readme)
        self.assertEqual((ROOT / 'SQL Crack Start.bat').is_file(), True)
        self.assertEqual(ROOT.name, 'SQL Crack v1.0.5 (Beta)')

if __name__ == '__main__':
    unittest.main()
