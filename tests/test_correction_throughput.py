import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import correction_throughput  # noqa: E402


class TestCorrectionThroughput(unittest.TestCase):
    def test_summary_reports_median_p95_and_rate(self):
        report = correction_throughput.summarize([
            {"correction_seconds": 0.3, "observation_seconds": 60},
            {"correction_seconds": 0.5, "observation_seconds": 60},
            {"correction_seconds": 1.0, "observation_seconds": 60},
        ])
        self.assertEqual(report["observations"], 3)
        self.assertEqual(report["median_seconds"], 0.5)
        self.assertEqual(report["p95_seconds"], 1.0)
        self.assertEqual(report["corrections_per_minute"], 3.0)

    def test_invalid_observation_fails_closed(self):
        for record in ({"correction_seconds": 0}, {"correction_seconds": -1},
                       {"correction_seconds": float("nan")},
                       {"correction_seconds": 0.2, "observation_seconds": 0}):
            with self.assertRaises(ValueError):
                correction_throughput.summarize([record])


if __name__ == "__main__":
    unittest.main()
