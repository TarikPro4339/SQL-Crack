"""Launcher smoke checks."""
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class IntroTests(unittest.TestCase):
    def test_intro_fast(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'Start.py'), '--fast', '--intro-only'], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('SQL CRACK', proc.stdout)
        self.assertIn('ACCESS GRANTED (DEMO)', proc.stdout)
        self.assertIn('v1.0.1', proc.stdout)

    def test_no_animation(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'Start.py'), '--no-animation', '--intro-only', '--fast'], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(proc.returncode, 0, proc.stderr)

if __name__ == '__main__':
    unittest.main()
