import subprocess
import sys
import tempfile
import unittest
import sys
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


import plot_models  # noqa: E402
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

    def test_intent_filter_text_report_is_reachable(self):
        with tempfile.TemporaryDirectory() as td:
            session = Path(td) / "session.jsonl"
            subprocess.run(
                [sys.executable, str(SCRIPTS / "make_benchmark.py"),
                 "--out", str(session), "--force"],
                check=True, capture_output=True, text=True,
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "intent_filter.py"), str(session)],
                check=True, capture_output=True, text=True,
            )
        self.assertIn("## session.jsonl", result.stdout)
        self.assertIn("events:", result.stdout)
        self.assertIn("|t_start_s|", result.stdout)

    def test_plot_models_help_does_not_require_optional_plotting_stack(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "plot_models.py"), "--help"],
            check=True, capture_output=True, text=True,
        )
        self.assertIn("--session", result.stdout)
        self.assertIn("--only", result.stdout)

    def test_confusion_plot_propagates_evaluator_failure(self):
        failure = subprocess.CompletedProcess(
            args=["evaluate_session.py"], returncode=1,
            stdout="", stderr="manifest fehlt: missing.manifest.jsonl",
        )
        with patch.object(plot_models.subprocess, "run", return_value=failure):
            with self.assertRaisesRegex(SystemExit, "manifest fehlt"):
                plot_models.fig_confusion(Path("missing.jsonl"), Path("out.png"))


if __name__ == "__main__":
    unittest.main()
