import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "audit_layout_provenance", ROOT / "audit_layout_provenance.py"
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ProvenanceAuditTests(unittest.TestCase):
    def test_rejected_profile_and_measured_layout_is_mismatch(self):
        layout = {"geometry": {"source": "measured hand profile"}}
        profile = {"_status": "REJECTED - not a usable measurement"}
        self.assertTrue(module.find_issues(layout, profile))

    def test_matching_provenance_is_clean(self):
        layout = {
            "geometry": {
                "source": "measured hand profile",
                "hand_profile": {
                    "_status": "ACCEPTED",
                    "_measured_by": "rom_capture.py",
                },
            }
        }
        profile = {"_status": "ACCEPTED", "_measured_by": "rom_capture.py"}
        self.assertEqual(module.find_issues(layout, profile), [])

    def test_repository_inputs_are_detected_as_stale(self):
        layout = json.loads((ROOT / "layout.json").read_text())
        profile = json.loads((ROOT / "hand_profile.json").read_text())
        self.assertTrue(module.find_issues(layout, profile))


if __name__ == "__main__":
    unittest.main()
