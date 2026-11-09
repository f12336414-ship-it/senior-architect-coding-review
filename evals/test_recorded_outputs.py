"""Replay saved Agent code against the original contracts, not response keywords.

This verifies the recorded artifacts only; it does not run or grade a new model.
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).parent


class RecordedOutputTests(unittest.TestCase):
    def check_scenario(self, name):
        original = ROOT / "scenarios" / name
        recorded = ROOT / "results" / "2026-11-09" / name
        self.assertTrue(original.is_dir(), f"missing original scenario: {original}")
        self.assertTrue(recorded.is_dir(), f"missing recorded output: {recorded}")
        self.assertTrue(list(original.glob("test_*.py")), "original acceptance tests required")
        with tempfile.TemporaryDirectory(prefix="architect-replay-") as directory:
            destination = Path(directory)
            for source in original.glob("*.py"):
                shutil.copyfile(source, destination / source.name)
            for source in recorded.glob("*.py"):
                if source.name.startswith("test_"):
                    self.assertFalse((destination / source.name).exists(),
                                     "recorded outputs must not replace original acceptance tests")
                shutil.copyfile(source, destination / source.name)
            result = subprocess.run(
                [sys.executable, "-X", "utf8", "-B", "-m", "unittest", "discover",
                 "-s", ".", "-p", "test_*.py", "-v"],
                cwd=destination, capture_output=True, text=True, encoding="utf-8", timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_local_write(self):
        self.check_scenario("local-write")

    def test_csv_export(self):
        self.check_scenario("csv-export")

    def test_shared_rules(self):
        self.check_scenario("shared-rules")


if __name__ == "__main__":
    unittest.main()
