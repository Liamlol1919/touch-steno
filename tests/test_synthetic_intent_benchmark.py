import importlib.util
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "synthetic_intent_benchmark",
    ROOT / "scripts" / "synthetic_intent_benchmark.py",
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class SyntheticIntentTest(unittest.TestCase):
    def setUp(self):
        self.cfg = module.Config()
        self.rng = random.Random(3)

    def test_tap_and_drift_are_detected(self):
        for kind in ("tap", "drift"):
            detections = module.detect(module.trace(kind, self.cfg, self.rng), self.cfg)
            self.assertTrue(detections, kind)
            self.assertEqual(detections[0].finger, "index")

    def test_rest_and_palm_do_not_trigger(self):
        for kind in ("rest", "palm"):
            detections = module.detect(module.trace(kind, self.cfg, self.rng), self.cfg)
            self.assertEqual(detections, [], kind)

    def test_coupled_ring_is_not_reported_as_independent(self):
        detections = module.detect(module.trace("ring_coupled", self.cfg, self.rng), self.cfg)
        self.assertTrue(detections)
        self.assertNotIn("ring", {d.finger for d in detections})


if __name__ == "__main__":
    unittest.main()
