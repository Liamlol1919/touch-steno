import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_core_checks", ROOT / "run_core_checks.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class CoreCheckExitTests(unittest.TestCase):
    def test_all_pass_returns_zero(self):
        self.assertEqual(module.overall_exit([("a", 0), ("b", 0)]), 0)

    def test_stale_provenance_returns_two(self):
        self.assertEqual(module.overall_exit([("a", 0), ("provenance", 2)]), 2)

    def test_technical_failure_wins_over_stale_provenance(self):
        self.assertEqual(module.overall_exit([("a", 1), ("provenance", 2)]), 1)


if __name__ == "__main__":
    unittest.main()
