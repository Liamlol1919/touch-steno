import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


class TestEvaluatorCli(unittest.TestCase):
    def test_text_report_includes_axis_and_diagonal_metrics(self):
        with tempfile.TemporaryDirectory() as td:
            session = Path(td) / "session.jsonl"
            subprocess.run(
                [sys.executable, str(SCRIPTS / "make_benchmark.py"),
                 "--out", str(session), "--force"],
                check=True, capture_output=True, text=True,
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "evaluate_session.py"), str(session)],
                check=True, capture_output=True, text=True,
            )
        self.assertIn("axis 1.0", result.stdout)
        self.assertIn("diagonal 1.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
