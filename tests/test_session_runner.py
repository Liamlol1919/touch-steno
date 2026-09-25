import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import session_runner  # noqa: E402


class TestSessionRunner(unittest.TestCase):
    def test_dry_run_without_tablet_prints_bimanual_plan(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            argv = [
                "session_runner.py", "--dry-run", "--quick", "--out", str(root),
                "--json", str(root / "report.json"), "--session-id", "dry-run",
                "--dominant-hand", "unknown",
            ]
            previous = session_runner.DRY_RUN
            try:
                with patch.object(session_runner, "have_tablet", return_value=None), \
                     patch.object(sys, "argv", argv):
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        result = session_runner.main()
                report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            finally:
                session_runner.DRY_RUN = previous
        self.assertEqual(result, 0)
        self.assertIsNone(report["tablet"])
        self.assertEqual(report["failed"], [])
        self.assertNotIn("NO TABLET FOUND", output.getvalue())
        commands = [step["cmd"] for step in report["steps"] if "cmd" in step]
        self.assertTrue(any("bimanual" in " ".join(command) for command in commands))
        self.assertTrue(all(step.get("dry") is True for step in report["steps"]
                            if "cmd" in step))


if __name__ == "__main__":
    unittest.main()
