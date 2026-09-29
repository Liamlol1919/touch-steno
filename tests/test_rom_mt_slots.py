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


class MultiTouchSlotTests(unittest.TestCase):
    def test_slots_keep_independent_contacts(self):
        tracker = module.ContactTracker(lambda x, y: (x, y))
        feed = tracker.feed

        # Slot 0 contact.
        feed(module.ABS_MT_SLOT, 0, 0.0)
        feed(module.ABS_MT_TRACKING_ID, 11, 0.0)
        feed(module.ABS_MT_POSITION_X, 10, 0.0)
        feed(module.ABS_MT_POSITION_Y, 20, 0.0)

        # Slot 1 must not overwrite or alias slot 0.
        feed(module.ABS_MT_SLOT, 1, 0.1)
        feed(module.ABS_MT_TRACKING_ID, 12, 0.1)
        feed(module.ABS_MT_POSITION_X, 100, 0.1)
        feed(module.ABS_MT_POSITION_Y, 200, 0.1)
        self.assertEqual(tracker.live_points(), [(10, 20), (100, 200)])

        closed = feed(module.ABS_MT_TRACKING_ID, -1, 0.2)
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].x, 100)
        self.assertEqual(closed[0].y, 200)
        self.assertEqual(tracker.live_points(), [(10, 20)])

        closed = feed(module.ABS_MT_SLOT, 0, 0.3) or feed(module.ABS_MT_TRACKING_ID, -1, 0.3)
        self.assertEqual(len(closed), 1)
        self.assertEqual((closed[0].x, closed[0].y), (10, 20))


    def test_partial_axis_order_does_not_fake_palm_span(self):
        tracker = module.ContactTracker(lambda x, y: (x, y))
        feed = tracker.feed
        # X arrives before Y. The missing Y must not be treated as y=0,
        # which used to create a >30 mm span and a false palm rejection.
        feed(module.ABS_MT_SLOT, 0, 0.0)
        feed(module.ABS_MT_TRACKING_ID, 21, 0.0)
        feed(module.ABS_MT_POSITION_X, 100, 0.0)
        feed(module.ABS_MT_POSITION_Y, 200, 0.0)
        closed = feed(module.ABS_MT_TRACKING_ID, -1, 0.1)
        self.assertEqual(len(closed), 1)
        self.assertEqual(closed[0].rejected, "")
        self.assertLess(closed[0].span, module.FINGER_MAX_SPAN_MM)

    def test_legacy_pointer_also_waits_for_both_axes(self):
        tracker = module.ContactTracker(lambda x, y: (x, y))
        tracker.feed(tracker.ABS_X, 100, 0.0)
        tracker.feed(tracker.ABS_Y, 200, 0.0)
        self.assertEqual(tracker.live_points(), [(100, 200)])


    def test_flush_closes_contact_at_step_boundary(self):
        tracker = module.ContactTracker(lambda x, y: (x, y))
        feed = tracker.feed
        feed(module.ABS_MT_SLOT, 0, 0.0)
        feed(module.ABS_MT_TRACKING_ID, 31, 0.0)
        feed(module.ABS_MT_POSITION_X, 100, 0.0)
        feed(module.ABS_MT_POSITION_Y, 200, 0.0)
        closed = tracker.flush()
        self.assertEqual(len(closed), 1)
        self.assertEqual((closed[0].x, closed[0].y), (100, 200))
        self.assertEqual(tracker.live_points(), [])
        # A late driver release after the boundary must not emit a duplicate.
        self.assertEqual(feed(module.ABS_MT_TRACKING_ID, -1, 0.1), [])


if __name__ == "__main__":
    unittest.main()
