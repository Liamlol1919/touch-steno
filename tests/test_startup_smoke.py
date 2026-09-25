import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import startup_smoke  # noqa: E402


@dataclass
class FakeResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


class StartupSmokeTest(unittest.TestCase):
    def test_classifies_subprocess_results(self):
        successful = FakeResult(0, stdout="usage: probe")
        missing_device = FakeResult(1, stdout="ERROR: no such device: /dev/input/event99")

        self.assertEqual(startup_smoke.classify_result(successful), startup_smoke.PASS)
        self.assertEqual(
            startup_smoke.classify_result(missing_device, "clear-error"),
            startup_smoke.PASS,
        )

    def test_explicit_unverified_reason(self):
        result = FakeResult(0, stdout="STATUS: PASS device=/dev/input/event19")
        self.assertEqual(
            startup_smoke.classify_result(
                result,
                unverified_reason="no readable Wacom finger device",
            ),
            startup_smoke.UNVERIFIED,
        )

    def test_traceback_always_fails(self):
        result = FakeResult(
            0,
            stdout="Traceback (most recent call last):\n  RuntimeError: broken",
        )

        self.assertEqual(startup_smoke.classify_result(result), startup_smoke.FAIL)

    def test_no_device_is_unverified_without_success_word(self):
        status = startup_smoke.classify_hardware_result(None)
        line = startup_smoke.status_line(
            "reshape_probe.py",
            "hardware open/read",
            status,
            "hardware startup NOT VERIFIED: no real Wacom finger device is present",
        )

        self.assertEqual(status, startup_smoke.UNVERIFIED)
        self.assertIn(startup_smoke.UNVERIFIED, line)
        self.assertNotIn(startup_smoke.PASS, line)

    def test_exit_code_allows_unverified_but_rejects_fail(self):
        self.assertEqual(
            startup_smoke.exit_code_for_statuses([
                startup_smoke.PASS,
                startup_smoke.UNVERIFIED,
            ]),
            0,
        )
        self.assertEqual(
            startup_smoke.exit_code_for_statuses([
                startup_smoke.PASS,
                startup_smoke.FAIL,
                startup_smoke.UNVERIFIED,
            ]),
            1,
        )


if __name__ == "__main__":
    unittest.main()
