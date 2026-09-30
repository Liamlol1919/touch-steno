import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rom_capture", ROOT / "rom_capture.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RomProfileSafetyTests(unittest.TestCase):
    def test_rejected_profile_becomes_a_check_failure_not_process_exit(self):
        rejected = {"_status": "REJECTED - unusable", "_rejected_because": ["bad run"]}
        result = module._profile_feeds_optimiser(rejected)
        self.assertIsInstance(result, str)
        self.assertIn("REJECTED", result)


if __name__ == "__main__":
    unittest.main()
