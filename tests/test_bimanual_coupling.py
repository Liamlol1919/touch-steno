import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import bimanual_coupling  # noqa: E402


class TestBimanualCoupling(unittest.TestCase):
    def _cue(self, cue_id, start, end, hand, index):
        return {"cue_id": cue_id, "label": f"bimanual_alternating_{hand}",
                "t_start": start, "t_end": end, "bimanual_mode": "alternating",
                "rate_hz": 1.0, "events": [0.0], "event_hands": [hand],
                "event_provenance": "expected_cue_schedule",
                "hand_provenance": "cued_anatomical_side_not_tracking_id",
                "block_index": 0, "condition_index": 0, "event_index": index,
                "condition_order": "alternating_then_simultaneous",
                "session_id": "p01", "dominant_hand": "unknown"}

    def test_alternating_capture_reports_timing_without_anatomical_labels(self):
        frames = [{"t": -0.1, "c": {}}]
        for i in range(30):
            t = i * 0.1
            if i < 10:
                contacts = {"1": (float(i), 0.0, 1.0)}
            elif 10 <= i < 20:
                contacts = {"2": (0.0, float(i - 10), 1.0)}
            else:
                contacts = {"1": (float(i - 20), 0.0, 1.0)}
            frames.append({"t": t, "c": contacts})
        records = [self._cue("bimanual-0", 0.0, 1.0, "left", 0),
                   self._cue("bimanual-1", 1.0, 2.0, "right", 1),
                   self._cue("bimanual-2", 2.0, 3.0, "left", 2)]
        report = bimanual_coupling.analyse(frames, records)
        block = report["blocks"][0]
        self.assertEqual(block["rates"]["valid_cycles"], 3)
        self.assertEqual(block["rates"]["realized_cycle_hz"], 1.0)
        self.assertEqual(block["alternating_intervals"]["samples_s"], [1.0, 1.0])
        self.assertFalse(block["alternating_intervals"]["anatomical_inter_hand_verified"])
        self.assertEqual(report["identity"]["anatomical_labels_emitted"], False)
        self.assertEqual(block["cues"][0]["onsets"][0]["associated_cued_side"], "left")
        self.assertNotIn("hand", block["cues"][0]["onsets"][0])

    def test_preexisting_contact_is_not_a_cue_onset(self):
        frames = [{"t": 0.0, "c": {"9": (0.0, 0.0, 1.0)}},
                  {"t": 0.1, "c": {"9": (1.0, 0.0, 1.0)}},
                  {"t": 1.0, "c": {"8": (0.0, 0.0, 1.0)}},
                  {"t": 1.1, "c": {"8": (1.0, 0.0, 1.0)}}]
        records = [self._cue("bimanual-0", 0.0, 1.0, "left", 0),
                   self._cue("bimanual-1", 1.0, 2.0, "right", 1)]
        report = bimanual_coupling.analyse(frames, records)
        cues = report["blocks"][0]["cues"]
        self.assertEqual(cues[0]["raw_new_episode_count"], 0)
        self.assertEqual(cues[0]["failure"], "no_new_contact")
        self.assertEqual(cues[1]["raw_new_episode_count"], 1)
        self.assertTrue(cues[1]["valid"])

    def test_simultaneous_onset_error_is_ordinal_not_anatomical(self):
        frames = [{"t": -0.1, "c": {}}]
        for i in range(20):
            t = i * 0.1
            if i < 10:
                contacts = {"3": (float(i), 0.0, 1.0)}
                if i >= 2:
                    contacts["4"] = (0.0, float(i - 2), 1.0)
            else:
                contacts = {"3": (float(i - 10), 0.0, 1.0)}
                if i >= 12:
                    contacts["4"] = (0.0, float(i - 12), 1.0)
            frames.append({"t": t, "c": contacts})
        def cue(cue_id, start, end, index):
            return {"cue_id": cue_id, "label": "bimanual_simultaneous",
                    "t_start": start, "t_end": end, "bimanual_mode": "simultaneous",
                    "rate_hz": 1.0, "events": [0.0, 0.0], "event_hands": ["left", "right"],
                    "event_provenance": "expected_cue_schedule",
                    "hand_provenance": "cued_anatomical_side_not_tracking_id",
                    "block_index": 0, "condition_index": 0, "event_index": index,
                    "condition_order": "alternating_then_simultaneous",
                    "session_id": "p01", "dominant_hand": "unknown"}
        report = bimanual_coupling.analyse(
            frames, [cue("bimanual-0", 0.0, 1.0, 0)])
        block = report["blocks"][0]
        self.assertEqual(block["simultaneous_onset_error_s"]["n"], 1)
        self.assertAlmostEqual(block["simultaneous_onset_error_s"]["mean"], 0.2)
        self.assertEqual(block["cues"][0]["onsets"][0]["associated_cued_side"], None)
        self.assertEqual(block["cues"][0]["onsets"][1]["associated_cued_side"], None)

    def test_reappearing_tracking_id_gets_new_episode_key(self):
        frames = [{"t": 0.0, "c": {"5": (0.0, 0.0, 1.0)}},
                  {"t": 0.1, "c": {"5": (1.0, 0.0, 1.0)}},
                  {"t": 0.2, "c": {}},
                  {"t": 0.3, "c": {"5": (0.0, 0.0, 1.0)}},
                  {"t": 0.4, "c": {"5": (1.0, 0.0, 1.0)}}]
        episodes = bimanual_coupling.contact_episodes(frames, "p01")
        self.assertEqual([row["trajectory_key"] for row in episodes],
                         ["p01::5::0", "p01::5::1"])
        self.assertTrue(episodes[0]["entered_before_capture"])
        self.assertFalse(episodes[1]["entered_before_capture"])

    def test_raw_pair_profile_is_unfiltered_and_requires_overlap(self):
        frames = [{"t": i * 0.01,
                   "c": {"a": (float(i), 0.0, 1.0), "b": (-float(i), 0.0, 1.0)}}
                  for i in range(50)]
        record = {"cue_id": "bimanual-0", "label": "bimanual_simultaneous",
                  "t_start": 0.0, "t_end": 0.5, "bimanual_mode": "simultaneous",
                  "rate_hz": 1.0, "events": [0.0, 0.0], "event_hands": ["left", "right"],
                  "event_provenance": "expected_cue_schedule",
                  "hand_provenance": "cued_anatomical_side_not_tracking_id",
                  "block_index": 0, "condition_index": 0, "event_index": 0,
                  "condition_order": "alternating_then_simultaneous",
                  "session_id": "p01", "dominant_hand": "unknown"}
        report = bimanual_coupling.analyse(frames, [record])
        pair = report["blocks"][0]["raw_pair_coupling"][0]
        self.assertEqual(pair["status"], "ok")
        self.assertAlmostEqual(pair["zero_lag_r"], -1.0)
        self.assertEqual(pair["peak_lag_frames"], 0)
        self.assertGreaterEqual(pair["n_overlap_samples"], 40)

    def test_duplicate_cue_id_fails_closed(self):
        record = self._cue("same", 0.0, 1.0, "left", 0)
        with self.assertRaises(ValueError):
            bimanual_coupling.analyse([{"t": 0.0, "c": {}}], [record, dict(record)])


if __name__ == "__main__":
    unittest.main()
