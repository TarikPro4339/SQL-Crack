from pathlib import Path
import unittest
import server

ROOT = Path(__file__).resolve().parents[1]
class BetaLabelTests(unittest.TestCase):
    def test_release_version_metadata(self):
        self.assertEqual(server.VERSION, "v1.0.5 (Beta)")
        self.assertEqual(server.RELEASE_CHANNEL, "Beta")
        self.assertEqual(server.DISPLAY_VERSION, "v1.0.5 (Beta)")
    def test_user_facing_label(self):
        for file in ("index.html", "app.js", "Start.py", "SQL Crack Start.bat", "README.md"):
            with self.subTest(file=file):
                self.assertIn("v1.0.5 (Beta)", (ROOT / file).read_text(encoding="utf-8-sig"))
    def test_intro_is_beta(self):
        text = (ROOT / "Start.py").read_text(encoding="utf-8")
        self.assertIn("[BETA-BUILD]", text)
        self.assertNotIn("[STABLE-BUILD]", text)
