"""Tests for the measured-evidence and intent-filter scripts (no hardware, no raw data).

These guard the *logic* behind the numbers in MEASURED_BIOMECHANICS.md and
CROSS_VALIDATION.md using synthetic traces with known ground truth, so the measured
constants cannot be silently broken by a refactor. The real biometric sessions are
deliberately not required: they stay out of the repo (MEASURED_BIOMECHANICS.md 0).
"""
import math
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import follower_predictability as fp  # noqa: E402
import intent_filter  # noqa: E402
import kinematics  # noqa: E402
import real_session_evidence as rse  # noqa: E402
import wpm_ceiling  # noqa: E402

import stroke_decoder  # noqa: E402
DT = 0.011  # ~91 Hz, the measured frame interval


def frames_to_payload(frames):
    return [{"t": i * DT, "c": dict(c)} for i, c in enumerate(frames)]


def rest_only(n=400, jitter=0.0):
    """A stationary contact: exactly zero movement when jitter == 0."""
    return frames_to_payload([{"1": (10.0, 10.0, 3.0)} for _ in range(n)])


def parallel_pair(n=200, gain=0.65, step=0.2):
    """Leader moves `step` mm per frame along +x; follower dragged by `gain` of it.

    step=0.2 mm/frame is 18 mm/s at 91 Hz (fine for the correlation maths).
    Detector tests pass step=0.6 (-> 55 mm/s) to clear the 40 mm/s gate, because
    the measured real movers run at 130-309 mm/s.
    """
    out = []
    for i in range(n):
        out.append({"1": (step * i, 0.0, 3.0), "2": (gain * step * i, 0.0, 3.0)})
    return frames_to_payload(out)


def mirrored_pair(n=200, gain=-0.4):
    """Leader moves along +x; follower is dragged backwards (anti-correlated)."""
    out = []
    for i in range(n):
        out.append({"1": (0.2 * i, 0.0, 3.0), "2": (gain * 0.2 * i, 0.0, 3.0)})
    return frames_to_payload(out)


def independent_pair(n=200, seed=7):
    """Leader moves along +x; follower is uncorrelated quantisation noise."""
    state = seed
    out = []
    for i in range(n):
        state = (1103515245 * state + 12345) % (1 << 31)
        noise = (state / (1 << 31) - 0.5) * 0.4
        out.append({"1": (0.2 * i, 0.0, 3.0), "2": (noise, noise * 0.5, 3.0)})
    return frames_to_payload(out)


class TestInitArtefactFilter(unittest.TestCase):
    def test_leading_default_frames_are_dropped(self):
        payload = frames_to_payload([
            {"9": [0.0, 0.0, 0.0]},      # reader init
            {"9": [0.0, 5.0, 0.0]},      # still init (x missing)
            {"9": [4.0, 5.0, 1.0]},      # first real sample
            {"9": [5.0, 5.0, 1.0]},
        ])
        clean = kinematics._strip_uninit_leads(payload)
        present = [f["c"].get("9") for f in clean]
        self.assertEqual(present[0], None)
        self.assertEqual(present[1], None)
        self.assertEqual(present[2], [4.0, 5.0, 1.0])

    def test_edge_contact_on_x0_is_kept(self):
        payload = frames_to_payload([{"8": [0.0, 2.0, 1.0]},
                                     {"8": [0.0, 3.0, 1.0]}])
        clean = kinematics._strip_uninit_leads(payload)
        self.assertEqual(len([f for f in clean if "8" in f["c"]]), 2)

    def test_analyze_does_not_report_phantom_velocity(self):
        payload = frames_to_payload([
            {"9": [0.0, 0.0, 0.0]},
            {"9": [0.0, 135.0, 0.0]},
            {"9": [223.6, 135.0, 0.0]},
            {"9": [223.7, 135.0, 0.0]},
        ])
        res = kinematics.analyze(payload)
        self.assertLess(res["9"]["peak_mm_s"], 200.0)
        self.assertLess(res["9"]["drift_mm"], 1.0)


class TestVectorCoupling(unittest.TestCase):
    def test_parallel_pair_is_cos_plus_one(self):
        res = rse.vector_coupling(parallel_pair(), min_frames=40)
        row = next(r for r in res if r["mover"] == "1" and r["follower"] == "2")
        self.assertGreater(row["cos"], 0.99)
        self.assertAlmostEqual(row["beta"], 0.65, places=2)

    def test_mirrored_pair_is_cos_minus_one(self):
        res = rse.vector_coupling(mirrored_pair(), min_frames=40)
        row = next(r for r in res if r["mover"] == "1" and r["follower"] == "2")
        self.assertLess(row["cos"], -0.99)

    def test_independent_pair_has_near_zero_correlation(self):
        res = rse.vector_coupling(independent_pair(), min_frames=40)
        row = next(r for r in res if r["mover"] == "1" and r["follower"] == "2")
        self.assertLess(abs(row["cos"]), 0.3)

    def test_predictability_separates_parallel_from_independent(self):
        par = fp.analyse.__wrapped__ if hasattr(fp.analyse, "__wrapped__") else None
        rows_p = fp.step_rows(parallel_pair())
        rows_i = fp.step_rows(independent_pair())
        rp = fp.pair_predictability(rows_p, "1", "2")
        ri = fp.pair_predictability(rows_i, "1", "2")
        self.assertGreater(rp["r2"], 0.9)      # suppressible
        self.assertLess(ri["r2"], 0.3)         # not suppressible
        del par


class TestPersistenceDetector(unittest.TestCase):
    def test_rest_only_never_fires(self):
        rows = intent_filter.steps_of(kinematics._strip_uninit_leads(rest_only()))
        events = intent_filter.detect_events(rows, intent_filter.MIN_SPEED_MM_S,
                                            intent_filter.MIN_RUN_FRAMES)
        self.assertEqual(events, [])

    def test_mover_above_threshold_fires(self):
        rows = intent_filter.steps_of(kinematics._strip_uninit_leads(
            parallel_pair(step=0.6)))
        events = intent_filter.detect_events(rows, intent_filter.MIN_SPEED_MM_S,
                                            intent_filter.MIN_RUN_FRAMES)
        self.assertTrue(events)

    def test_brief_spike_below_min_run_does_not_fire(self):
        """The measured rest behaviour: a short burst must not become an event."""
        frames = []
        for i in range(400):
            x = 10.0 + (0.3 if 100 <= i < 105 else 0.0)
            frames.append({"1": (x, 10.0, 3.0)})
        rows = intent_filter.steps_of(kinematics._strip_uninit_leads(
            frames_to_payload(frames)))
        events = intent_filter.detect_events(rows, intent_filter.MIN_SPEED_MM_S,
                                            intent_filter.MIN_RUN_FRAMES)
        self.assertEqual(events, [])

    def test_intent_filter_suppresses_a_parallel_follower(self):
        payload = parallel_pair(n=200, gain=0.65, step=0.6)
        pairs = intent_filter.fit_pairs(intent_filter.steps_of(payload))
        self.assertIn(("1", "2"), pairs)
        self.assertGreater(pairs[("1", "2")]["r2"], 0.5)


class TestChordCriterion(unittest.TestCase):
    """A chord is a temporally aligned second mover, not merely a second contact."""

    def _rows(self, series):
        """series: list of {tid: (dx, dy, speed)} -> list of rows."""
        return [s for s in series]

    def test_two_aligned_peaks_are_a_chord(self):
        row = {"1": (1.0, 0.0, 100.0), "2": (0.8, 0.0, 90.0)}
        rows = [row] * 8
        chord, diag = stroke_decoder.chord_candidates(rows, 0, 7, "1")
        self.assertEqual(chord, ["2"])
        self.assertTrue(diag["2"]["chord"])

    def test_weak_follower_is_not_a_chord(self):
        row = {"1": (1.0, 0.0, 100.0), "2": (0.1, 0.0, 10.0)}
        rows = [row] * 8
        chord, diag = stroke_decoder.chord_candidates(rows, 0, 7, "1")
        self.assertEqual(chord, [])
        self.assertFalse(diag["2"]["chord"])

    def test_delayed_peer_is_not_a_chord(self):
        """Same magnitude, but the second peak arrives 5 frames later."""
        rows = []
        for i in range(8):
            rows.append({"1": (1.0, 0.0, 100.0),
                         "2": (0.9, 0.0, 95.0 if i >= 5 else 5.0)})
        chord, diag = stroke_decoder.chord_candidates(rows, 0, 7, "1")
        self.assertEqual(chord, [])

    def test_sector_mapping_is_axis_aligned(self):
        self.assertEqual(stroke_decoder.sector_of(10.0, 0.0), "E")
        self.assertEqual(stroke_decoder.sector_of(0.0, -10.0), "N")
        self.assertEqual(stroke_decoder.sector_of(0.0, 10.0), "S")
        self.assertEqual(stroke_decoder.sector_of(-10.0, 0.0), "W")
        self.assertEqual(stroke_decoder.sector_of(10.0, -10.0), "NE")

    def test_band_boundaries(self):
        self.assertEqual(stroke_decoder.band_of(1.0), "micro")
        self.assertEqual(stroke_decoder.band_of(3.0), "small")
        self.assertEqual(stroke_decoder.band_of(7.0), "medium")
        self.assertEqual(stroke_decoder.band_of(30.0), "large")

    def test_unmapped_descriptors_are_reported_not_guessed(self):
        self.assertNotIn("N|small|chord3", stroke_decoder.DEFAULT_MAP)

    def test_confidence_flags_sector_fences(self):
        # dead centre of the E sector (0 deg) -> max margin
        centred = stroke_decoder.confidence(10.0, 0.0, 8.0, "E")
        self.assertFalse(centred["on_fence"])
        self.assertGreater(centred["edge_margin_deg"], 20)
        # exactly on the E/NE boundary (22.5 deg) -> on the fence
        edge = stroke_decoder.confidence(10.0, -4.142, 8.0, "E")
        self.assertTrue(edge["on_fence"])
        self.assertLess(edge["edge_margin_deg"], 2)

    def test_confidence_arc_occupancy_is_bounded(self):
        short = stroke_decoder.confidence(10.0, 0.0, 2.0, "E")
        long = stroke_decoder.confidence(10.0, 0.0, 40.0, "E")
        self.assertLess(short["arc_occupancy"], long["arc_occupancy"])
        self.assertLessEqual(long["arc_occupancy"], 1.0)

    def test_strokes_carry_confidence_and_provenance(self):
        self.assertEqual(stroke_decoder.sector_of(1.0, 0.0), "E")
        c = stroke_decoder.confidence(1.0, 0.0, 5.0, "E")
        for key in ("edge_margin_deg", "on_fence", "arc_occupancy", "sector_arc_mm"):
            self.assertIn(key, c)



class TestBenchmarkArtefacts(unittest.TestCase):
    """The benchmark must not manufacture signals that the detector then has to survive."""

    def test_blocks_are_physically_continuous(self):
        """A cue change must not teleport a contact; that fakes an idle false trigger."""
        import argparse
        import make_benchmark as mb
        a = argparse.Namespace(seed=7, sector_reps=1, tempo=[], chord_reps=1,
                                rest_blocks=1)
        frames, manifest = mb.build(a.seed, a.sector_reps, a.tempo, a.chord_reps,
                                    a.rest_blocks)
        by_tid = {}
        for fr in frames:
            for tid, (x, y, _m) in fr["c"].items():
                by_tid.setdefault(tid, []).append((x, y))
        for tid, pts in by_tid.items():
            jumps = [max(abs(pts[i + 1][0] - pts[i][0]),
                         abs(pts[i + 1][1] - pts[i][1])) for i in range(len(pts) - 1)]
            # no step may exceed a plausible fast stroke frame (5 mm)
            self.assertLess(max(jumps), 5.0,
                            f"contact {tid} teleports by {max(jumps):.1f} mm")

    def test_gestures_exceed_the_detector_window(self):
        """Sector cues must be longer than the persistence window or they cannot be scored."""
        import argparse
        import make_benchmark as mb
        a = argparse.Namespace(seed=7, sector_reps=1, tempo=[], chord_reps=0,
                                rest_blocks=1)
        _frames, manifest = mb.build(a.seed, a.sector_reps, a.tempo, a.chord_reps,
                                     a.rest_blocks)
        min_s = intent_filter.MIN_RUN_FRAMES * 0.011
        for rec in manifest:
            if (rec.get("label") or "").startswith(("sector_", "chord", "single")):
                self.assertGreater(rec["t_end"] - rec["t_start"], min_s,
                                   f"{rec['label']} is shorter than the window")

    def test_label_lookup_is_half_open(self):
        import evaluate_session as ev
        man = [{"t_start": 0.0, "t_end": 1.0, "label": "a"},
               {"t_start": 1.0, "t_end": 2.0, "label": "b"}]
        self.assertEqual(ev.label_at(man, 0.999)["label"], "a")
        self.assertEqual(ev.label_at(man, 1.0)["label"], "b",
                         "a boundary timestamp belongs to the later block")


class TestStrokeSink(unittest.TestCase):
    def test_undo_removes_last_stroke(self):
        import stroke_sink
        t = stroke_sink.Transcript()
        for s in ("T", "H", "*", "A"):
            t.push(s)
        self.assertEqual(t.strokes, ["T", "A"])
        self.assertEqual(t.text(), "ta")

    def test_undo_on_empty_is_safe(self):
        import stroke_sink
        t = stroke_sink.Transcript()
        t.push("*")
        self.assertEqual(t.strokes, [])

    def test_plover_json_shape_and_retraction_marker(self):
        import stroke_sink
        t = stroke_sink.Transcript()
        t.push("K")
        out = t.plover_json(12.5)
        self.assertEqual(out, {"t": 12.5, "strokes": ["K"]})
        empty = stroke_sink.Transcript().plover_json(0.0)
        self.assertEqual(empty["strokes"], ["*"],
                         "an empty transcript must still emit a valid retraction")

    def test_transcript_ignores_hyphen_prefixes(self):
        import stroke_sink
        t = stroke_sink.Transcript()
        t.push("-T")
        self.assertEqual(t.text(), "t")


class TestLatencyBudget(unittest.TestCase):
    def test_pipeline_is_far_under_the_frame_budget(self):
        """Regression guard: an accidental O(n^2) must fail here, not in live typing."""
        import latency_budget
        import make_benchmark as mb
        import argparse
        import tempfile
        a = argparse.Namespace(seed=3, sector_reps=2, tempo=[1, 2, 3],
                               chord_reps=2, rest_blocks=1)
        frames, _man = mb.build(a.seed, a.sector_reps, a.tempo, a.chord_reps,
                                a.rest_blocks)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "b.jsonl"
            with kinematics.Recorder(path) as rec:
                for fr in frames:
                    rec.frame(fr["t"], {int(k): tuple(v)
                                        for k, v in fr["c"].items()})
            rep = latency_budget.analyse(path)
        budget_us = 1e6 / 91.0
        self.assertLess(rep["cpu_us_per_frame"], budget_us * 0.25,
                        "pipeline must stay under 25% of one frame's budget")

class TestWpmRateBudget(unittest.TestCase):
    def test_150_wpm_one_event_per_syllable_requires_3_75_hz(self):
        self.assertAlmostEqual(
            wpm_ceiling.required_event_rate_hz(150, 1.5, 1.0), 3.75)

    def test_250_wpm_one_event_per_syllable_requires_6_25_hz(self):
        self.assertAlmostEqual(
            wpm_ceiling.required_event_rate_hz(250, 1.5, 1.0), 6.25)

    def test_two_events_per_syllable_doubles_the_rate(self):
        one = wpm_ceiling.required_event_rate_hz(250, 1.5, 1.0)
        two = wpm_ceiling.required_event_rate_hz(250, 1.5, 2.0)
        self.assertAlmostEqual(two, one * 2.0)

    def test_event_rate_maps_back_to_target_wpm(self):
        rate = wpm_ceiling.required_event_rate_hz(200, 1.5, 1.0)
        self.assertAlmostEqual(wpm_ceiling.wpm_for(rate, 1.5, 1.0), 200)

    def test_rest_run_is_shorter_than_the_detector_window(self):
        """The 88 ms window exists because rest runs reach seven frames."""
        self.assertLess(wpm_ceiling.REST_RUN_MAX_MS, wpm_ceiling.EVENT_MS)
        self.assertAlmostEqual(wpm_ceiling.EVENT_MS / (1000.0 / wpm_ceiling.HZ),
                               8.0, places=0)


class TestEnvelopeAndMetricContract(unittest.TestCase):
    """Pin the envelope claims and the metrics that produced them.

    Three separate bugs in the evaluation harness produced three confident wrong numbers
    (BENCHMARK_RESULTS.md addendum). These tests exist so a fourth cannot.
    """

    def _cell(self, length_s, rate_hz):
        import tempfile
        import envelope_sweep as es
        frames, man = es.build(length_s, rate_hz, seed=11)
        with tempfile.TemporaryDirectory() as td:
            return es.measure(frames, man, Path(td))

    def test_100ms_gestures_are_never_detected(self):
        m = self._cell(0.10, 3.0)
        self.assertEqual(m["detected"], 0,
                         "the envelope claims a 100ms gesture is undetectable")

    def test_working_range_detects_everything_with_zero_idle(self):
        for rate in (1.0, 3.0, 6.0):
            m = self._cell(0.25, rate)
            self.assertEqual(m["rate_ratio"], 1.0, f"rate {rate}")
            self.assertEqual(m["sector_acc"], 1.0, f"rate {rate}")
            self.assertEqual(m["idle_fp"], 0, f"rate {rate}")

    def test_long_gestures_lose_events_not_accuracy(self):
        m = self._cell(0.50, 3.0)
        self.assertLess(m["rate_ratio"], 1.0)
        self.assertEqual(m["sector_acc"], 1.0,
                         "500ms gestures are unreliable in count, not in direction")

    def test_return_phase_changes_the_direction_estimate(self):
        """Without a return to a common centre the error is a constant 67.5 degrees."""
        import math
        S = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        V = {n: (math.cos(math.radians(i * 45)), -math.sin(math.radians(i * 45)))
             for i, n in enumerate(S)}

        def first_step_error(reset):
            pos = (0.0, 0.0)
            errs = []
            for n in S:
                if reset:
                    pos = (0.0, 0.0)
                tgt = (V[n][0] * 20, V[n][1] * 20)
                e1 = min(1.0, (1 / 22) * 1.4)
                x = pos[0] + (tgt[0] - pos[0]) * e1
                y = pos[1] + (tgt[1] - pos[1]) * e1
                first = math.degrees(math.atan2(-(y - pos[1]), x - pos[0]))
                soll = math.degrees(math.atan2(-V[n][1], V[n][0]))
                errs.append((first - soll + 180) % 360 - 180)
                pos = tgt
            return errs
        chained = [abs(e) for e in first_step_error(False)][1:]
        self.assertTrue(all(60 < e < 75 for e in chained),
                        f"expected a constant ~67.5deg error, got {chained}")
        centred = [abs(e) for e in first_step_error(True)]
        self.assertTrue(all(e < 5 for e in centred), f"got {centred}")


    def test_no_thumb_radius_survives_chained_gestures(self):
        """Compaction: at r <= 25mm the repositioning error exceeds the sector half-width."""
        import compass_geometry as cg
        for r in (8, 10, 12, 15, 20, 25):
            row = cg.analyse(r, cg.DEFAULT_WINDOW_MS, cg.DEFAULT_SPEED_MM_S)
            self.assertFalse(row["within_half_width"],
                             f"r={r}mm unexpectedly survives chained gestures")
        self.assertTrue(cg.analyse(40, cg.DEFAULT_WINDOW_MS,
                                   cg.DEFAULT_SPEED_MM_S)["within_half_width"])

    def test_reversal_detector_closes_on_a_turn(self):
        """Out-and-back: the event must close at the reversal, not run into the return."""
        out = [{"1": (1.0, 0.0, 120.0)} for _ in range(14)]
        back = [{"1": (-1.0, 0.0, 120.0)} for _ in range(14)]
        rows = out + back
        evs = intent_filter.detect_reversal_events(
            rows, intent_filter.MIN_SPEED_MM_S, intent_filter.MIN_RUN_FRAMES)
        self.assertTrue(evs, "a reversal must produce an event")
        self.assertLessEqual(evs[0]["end"], 14,
                             "event must close on the first return frame")

    def test_reversal_detector_ignores_a_straight_run(self):
        rows = [{"1": (1.0, 0.0, 120.0)} for _ in range(30)]
        evs = intent_filter.detect_reversal_events(
            rows, intent_filter.MIN_SPEED_MM_S, intent_filter.MIN_RUN_FRAMES)
        for e in evs:
            self.assertIsNone(e["turn_deg"],
                              "a straight run has no reversal to report")

    def test_first_window_beats_whole_stroke_on_hooked_strokes(self):
        """A worker recommended accumulating over the whole event. Measured: it loses.

        On a stroke that turns mid-way, the whole-event vector averages the out-leg with
        the hook and the sector estimate collapses; the 8-frame window that the speed gate
        selected stays at 1.00. Pinned so the recommendation cannot be re-adopted silently.
        """
        import math
        import random

        def hooked(n_len, sigma, turn_deg, rng, turn_frac=0.4):
            ang = rng.randrange(8)
            head = math.radians(ang * 45)
            xs, ys, step = [0.0], [0.0], 20.0 / n_len
            for j in range(n_len):
                if j == int(n_len * turn_frac):
                    head += math.radians(turn_deg)
                xs.append(xs[-1] + step * math.cos(head) + rng.gauss(0, sigma))
                ys.append(ys[-1] - step * math.sin(head) + rng.gauss(0, sigma))
            return xs, ys, ang

        def vectors(xs, ys):
            n = len(xs) - 1
            steps = [(xs[i + 1] - xs[i], ys[i + 1] - ys[i]) for i in range(n)]
            speeds = [math.hypot(*s) / 0.011 for s in steps]
            above = [i for i, v in enumerate(speeds)
                     if v >= intent_filter.MIN_SPEED_MM_S]
            if len(above) < intent_filter.MIN_RUN_FRAMES:
                return None
            s0 = above[0]
            k = intent_filter.MIN_RUN_FRAMES
            return {"first": (sum(dx for dx, _ in steps[s0:s0 + k]),
                              sum(dy for _, dy in steps[s0:s0 + k])),
                    "whole": (xs[-1] - xs[0], ys[-1] - ys[0])}

        sectors = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        for turn in (0, 20, 45, 90):
            rng = random.Random(7)
            hits = {"first": 0, "whole": 0}
            n = 0
            for _ in range(200):
                xs, ys, ang = hooked(22, 0.14, turn, rng)
                v = vectors(xs, ys)
                if v is None:
                    continue
                n += 1
                for k, (dx, dy) in v.items():
                    if stroke_decoder.sector_of(dx, dy) == sectors[ang]:
                        hits[k] += 1
            self.assertEqual(hits["first"] / n, 1.0, f"first-8 window, turn {turn}")
            if turn >= 45:
                self.assertLess(hits["whole"] / n, 0.5,
                                f"whole-event estimate should collapse at turn {turn}")


class TestSeparationModel(unittest.TestCase):
    """The model must predict the measured resting behaviour, not restate it."""

    def test_angular_noise_stays_inside_the_sector(self):
        import separation_model as sm
        self.assertLess(sm.angular_noise_deg(sm.REST_STEP_P99), 180.0 / 8 / 3)
        self.assertLess(sm.angular_noise_deg(1.479), 180.0 / 8 / 2,
                        "even the worst observed frame must stay inside half a sector")

    def test_sector_margin_is_zero_on_a_boundary(self):
        import separation_model as sm
        self.assertAlmostEqual(sm.sector_margin_deg(22.5), 0.0, places=6)
        self.assertAlmostEqual(sm.sector_margin_deg(0.0), 22.5, places=6)
        self.assertAlmostEqual(sm.sector_margin_deg(11.25), 11.25, places=6)

    def test_operating_point_margin_against_measured_runs(self):
        """The chosen (40, 8) setting has exactly one frame of margin. Pin that."""
        import separation_model as sm
        import real_session_evidence as rse
        import kinematics
        from pathlib import Path
        # Raw sessions are biometric and never committed; point at them explicitly.
        import os
        root = os.environ.get("TOUCH_STENO_SESSIONS")
        if not root:
            self.skipTest("set TOUCH_STENO_SESSIONS to a directory of raw captures")
        sessions = [Path(root) / n
                    for n in ("test.jsonl", "test-daumen.jsonl", "test-zeige.jsonl")]
        if not all(p.exists() for p in sessions):
            self.skipTest("measured sessions not available")
        worst = 0
        for p in sessions:
            runs = sm.rest_run_lengths(p)
            if 40.0 in runs:
                worst = max(worst, runs[40.0]["worst_run"])
        self.assertLess(worst, sm.K_FRAMES,
                        "the operating point must not fire on measured rest")
        self.assertGreaterEqual(sm.K_FRAMES - worst, 1,
                                "margin is at least one frame by construction")


class TestLayoutAssignment(unittest.TestCase):
    """W16 reported this as NOT FOUND in the literature; we measure it instead."""

    def _conf(self, trials=300, seed=5):
        import layout_assignment as la
        sigma = la.calibrate_sigma(trials=200, seed=3)
        return la, sigma, la.build_confusion(trials, seed, sigma)

    def test_confusions_are_overwhelmingly_adjacent(self):
        """Measured: 99.6% of confusion mass goes to a neighbouring sector, 0.4% skips.

        Not a hard ring - a 2-sector skip does occur, just 3 times in 4800 trials. The design
        rule is therefore "never place minimal pairs on adjacent sectors", with a small
        residual risk across the compass, not "adjacency is the only failure".
        """
        la, _s, conf = self._conf(trials=600)
        idx = {name: i for i, name in enumerate(la.SECTORS)}
        adj = skip = 0
        for a, row in conf.items():
            for b, n in row.items():
                if a == b or not n:
                    continue
                if abs(idx[a] - idx[b]) in (1, 7):
                    adj += n
                else:
                    skip += n
        self.assertGreater(adj / (adj + skip), 0.99,
                           "confusion must be overwhelmingly to a neighbour")

    def test_on_axis_rule_beats_naive_and_optimiser_beats_it(self):
        import layout_assignment as la
        la_, _s, conf = self._conf()
        freq = la.zipf(8)
        naive = [i % 8 for i in range(8)]
        axis = la.on_axis_first(8)
        opt, _e = la.optimise(freq, conf, iters=4000, seed=5)
        e_naive = la.expected_error(freq, naive, conf)
        e_axis = la.expected_error(freq, axis, conf)
        e_opt = la.expected_error(freq, opt, conf)
        self.assertLess(e_axis, e_naive, "on-axis-first rule must beat naive order")
        self.assertLessEqual(e_opt, e_axis + 1e-9,
                             "the annealer must not be worse than the rule")

    def test_direction_error_exceeds_sensor_noise(self):
        """The fitted per-frame noise is several times the resting noise floor."""
        la, sigma, _c = self._conf()
        self.assertGreater(sigma, 3 * la.REST_STEP_P99,
                           "aim error dominates sensor noise; a better sensor would "
                           "not fix direction accuracy")


class TestIdentityDatasetCheck(unittest.TestCase):
    """A finger-identity capture must be validated before it trains anything."""

    def _capture(self, tmp, lift_frames=18, lift_two=False):
        import json
        import kinematics
        DT = 0.011
        contacts = {"1": (10.0, 10.0), "2": (30.0, 12.0), "3": (50.0, 14.0)}
        frames, manifest, t = [], [], 0.0
        for _rep in range(2):
            for i, (tid, (x, y)) in enumerate(contacts.items()):
                t0 = t
                for _ in range(120):
                    frames.append({"t": round(t, 6),
                                   "c": {k: [v[0], v[1], 2.0] for k, v in contacts.items()}})
                    t += DT
                victims = list(contacts)[:2] if (lift_two and i == 1) else [tid]
                for _ in range(lift_frames):
                    frames.append({"t": round(t, 6),
                                   "c": {k: [v[0], v[1], 2.0]
                                         for k, v in contacts.items() if k not in victims}})
                    t += DT
                for _ in range(60):
                    frames.append({"t": round(t, 6),
                                   "c": {k: [v[0], v[1], 2.0] for k, v in contacts.items()}})
                    t += DT
                manifest.append({"t_start": t0, "t_end": t,
                                 "label": f"identity_f{i}", "finger": f"f{i}"})
        path = Path(tmp) / "cap.jsonl"
        with kinematics.Recorder(path, force=True) as rec:
            for fr in frames:
                rec.frame(fr["t"], {int(k): tuple(v) for k, v in fr["c"].items()})
        path.with_suffix(".manifest.jsonl").write_text(
            "\n".join(json.dumps(r) for r in manifest), encoding="utf-8")
        return path
    @staticmethod
    def _mapping():
        return {"f0": "1", "f1": "2", "f2": "3"}


    def test_clean_capture_is_all_valid(self):
        import tempfile
        import identity_dataset_check as idc
        with tempfile.TemporaryDirectory() as td:
            rep = idc.check(self._capture(td), self._mapping())
        self.assertTrue(rep["all_valid"])
        self.assertEqual(rep["counts"].get("VALID"), rep["cues"])

    def test_shallow_lift_is_rejected(self):
        """3 frames of jitter is not a lift; the capture must not pass as labelled data."""
        import tempfile
        import identity_dataset_check as idc
        with tempfile.TemporaryDirectory() as td:
            rep = idc.check(self._capture(td, lift_frames=3), self._mapping())
        self.assertFalse(rep["all_valid"])
        self.assertIn("MISSING", rep["counts"])

    def test_two_fingers_lifted_at_once_is_ambiguous(self):
        """The label cannot be attributed when more than one contact vanished."""
        import tempfile
        import identity_dataset_check as idc
        with tempfile.TemporaryDirectory() as td:
            rep = idc.check(self._capture(td, lift_two=True), self._mapping())
        self.assertFalse(rep["all_valid"])
        self.assertIn("AMBIGUOUS", rep["counts"])


    def test_unique_lift_without_mapping_is_unverified(self):
        import tempfile
        import identity_dataset_check as idc
        with tempfile.TemporaryDirectory() as td:
            rep = idc.check(self._capture(td))
        self.assertFalse(rep["all_valid"])
        self.assertEqual(rep["counts"].get("UNVERIFIED"), rep["cues"])

    def test_wrong_explicit_mapping_is_contaminated(self):
        import tempfile
        import identity_dataset_check as idc
        with tempfile.TemporaryDirectory() as td:
            rep = idc.check(self._capture(td), {"f0": "2", "f1": "2", "f2": "3"})
        self.assertFalse(rep["all_valid"])
        self.assertIn("CONTAMINATED", rep["counts"])

class TestRigidFit(unittest.TestCase):
    """Translation+rotation must be removed from the anchors, and only from them."""

    def test_translation_is_removed(self):
        import intent_filter as ifl
        pos = {"1": (0.0, 0.0), "2": (10.0, 0.0), "3": (0.0, 10.0)}
        delta = {k: (0.4, -0.2) for k in pos}          # pure translation
        tx, ty, omega, n = ifl.fit_rigid(delta, pos, list(pos))
        self.assertEqual(n, 3)
        self.assertAlmostEqual(tx, 0.4, places=6)
        self.assertAlmostEqual(ty, -0.2, places=6)
        self.assertAlmostEqual(omega, 0.0, places=9)

    def test_rotation_is_removed(self):
        import intent_filter as ifl
        pos = {"1": (-20.0, 0.0), "2": (0.0, 20.0), "3": (-20.0, 20.0)}
        omega_true = 2e-4                                # rad/mm
        delta = {k: (-omega_true * pos[k][1], omega_true * pos[k][0]) for k in pos}
        tx, ty, omega, _n = ifl.fit_rigid(delta, pos, list(pos))
        self.assertAlmostEqual(omega, omega_true, places=8)
        # use the shipped subtraction, not a re-derivation of the centring convention:
        # the first version mixed absolute and centred coordinates and reported a
        # 0.0038mm residual that was pure bookkeeping.
        fixed, n_anchor = ifl.apply_rigid(delta, pos, list(pos))
        self.assertEqual(n_anchor, 3)
        for k in pos:
            self.assertLess(math.hypot(*fixed[k]), 1e-6, f"residual at {k}")

    def test_two_anchors_are_enough_and_one_is_not(self):
        import intent_filter as ifl
        pos = {"1": (0.0, 0.0), "2": (10.0, 5.0), "3": (40.0, -5.0)}
        delta = {"1": (0.1, 0.0), "2": (0.1, 0.0), "3": (3.0, -1.0)}  # 3 is the mover
        _tx, _ty, _om, n2 = ifl.fit_rigid(delta, pos, ["1", "2"])
        self.assertEqual(n2, 2)
        _tx, _ty, omega, n1 = ifl.fit_rigid(delta, pos, ["1"])
        self.assertEqual(n1, 1)
        self.assertEqual(omega, 0.0, "with one anchor a rotation is not identifiable")


class TestCompassSurface(unittest.TestCase):
    """The radius trade-off must be monotone in accuracy and in cycle cost."""

    def test_accuracy_rises_with_radius(self):
        import compass_surface as cs
        small = cs.row(12.0, trials=1500, seed=5)
        large = cs.row(30.0, trials=1500, seed=5)
        self.assertGreater(large["accuracy"], small["accuracy"] + 0.2,
                           "more arc per frame means more signal at fixed noise")
        self.assertLess(large["contamination_error_deg"],
                        small["contamination_error_deg"],
                        "larger target spacing means less repositioning contamination")
        self.assertGreater(small["cycle_limit_hz"], large["cycle_limit_hz"],
                           "the return leg is the only cost, and it grows with radius")
    def test_return_speed_is_explicit_in_rate_model(self):
        import compass_surface as cs
        fast = cs.row(20.0, trials=200, seed=5, return_speed_mm_s=600.0)
        subgate = cs.row(20.0, trials=200, seed=5, return_speed_mm_s=30.0)
        self.assertEqual(fast["return_strategy"], "fast_reversal")
        self.assertEqual(subgate["return_strategy"], "sub_gate_return")
        self.assertLess(subgate["cycle_limit_hz"], fast["cycle_limit_hz"])
        self.assertEqual(subgate["rate_basis"], "conditional_cycle_model")

    def test_radius_below_15mm_is_not_viable(self):
        import compass_surface as cs
        row = cs.row(12.0, trials=1500, seed=5)
        self.assertLess(row["accuracy"], 0.7,
                        "at 12mm the sector pitch is only ~16x the resting step")

    def test_error_is_variance_not_bias(self):
        """A bias fit would only help if the error had a systematic component."""
        import math
        import random
        import stroke_decoder
        sectors = ("E", "NE", "N", "NW", "W", "SW", "S", "SE")
        vec = {n: (math.cos(math.radians(i * 45)), -math.sin(math.radians(i * 45)))
               for i, n in enumerate(sectors)}
        rng = random.Random(3)
        errs = []
        for _ in range(1500):
            ti = rng.randrange(8)
            vx, vy = vec[sectors[ti]]
            dx = dy = 0.0
            for _ in range(8):
                dx += vx * (20.0 / (8 * 0.011)) * 0.011 + rng.gauss(0, 2.03)
                dy += vy * (20.0 / (8 * 0.011)) * 0.011 + rng.gauss(0, 2.03)
            ang = math.degrees(math.atan2(-dy, dx)) % 360.0
            errs.append((ang - ti * 45 + 180) % 360 - 180)
        m = sum(errs) / len(errs)
        var = sum((e - m) ** 2 for e in errs) / len(errs)
        self.assertLess(abs(m) / math.sqrt(var), 0.1,
                        "the direction error must be variance, not a correctable bias")


class TestCouplingTimingSignature(unittest.TestCase):
    """The two coupling classes differ in temporal SHAPE, not only in magnitude."""

    def test_sharp_pair_peaks_at_lag_zero_and_collapses_fast(self):
        import follower_predictability as fp
        rows = []
        for i in range(80):
            rows.append({"1": (1.0, 0.0), "2": (0.65, 0.0)})
            rows.append({"1": (0.0, 0.0), "2": (0.0, 0.0)})
        prof = fp.lag_profile(rows, "1", "2", max_lag=4)
        self.assertAlmostEqual(prof[0], 1.0, places=6)
        self.assertLess(fp.half_width_frames(prof), 3,
                        "a mechanical parallel coupling is sharp")

    def test_broad_pair_stays_correlated_over_several_frames(self):
        import follower_predictability as fp
        import math
        rows = []
        for i in range(120):
            # leader moves in bursts of 5 frames; follower trails the burst envelope,
            # so the relation spans several frames but still peaks at zero lag
            lead = 1.0 if (i // 5) % 2 == 0 else 0.0
            follow = 1.0 if ((i + 1) // 5) % 2 == 0 else 0.0
            rows.append({"1": (lead, 0.0), "2": (-0.5 * follow, 0.0)})
        prof = fp.lag_profile(rows, "1", "2", max_lag=6)
        self.assertLess(abs(prof[0]), 1.0)
        del math

    def test_half_width_is_none_when_nothing_decays(self):
        import follower_predictability as fp
        prof = {0: 0.5, 1: 0.4, 2: 0.3}
        self.assertIsNone(fp.half_width_frames(prof),
                          "a profile that never halves has no half-width")
    def test_sharp_pair_passes_opt_in_temporal_gate(self):
        import follower_predictability as fp
        decision = fp.suppression_decision(0.8, {0: 1.0, 1: 0.4, 2: 0.2})
        self.assertTrue(decision["suppress"])
        self.assertEqual(decision["half_width_frames"], 1)

    def test_broad_pair_fails_opt_in_temporal_gate(self):
        import follower_predictability as fp
        decision = fp.suppression_decision(0.8, {0: 1.0, 1: 0.9, 2: 0.8,
                                                 3: 0.7, 4: 0.4})
        self.assertFalse(decision["suppress"])
        self.assertEqual(decision["half_width_frames"], 4)

    def test_low_magnitude_fails_opt_in_temporal_gate(self):
        import follower_predictability as fp
        decision = fp.suppression_decision(0.2, {0: 1.0, 1: 0.1})
        self.assertFalse(decision["suppress"])
        self.assertIn("r2", decision["reason"])

class TestQuantileHelpers(unittest.TestCase):
    def test_quantile_bounds(self):
        vals = [float(i) for i in range(100)]
        self.assertEqual(rse.quantile(vals, 0.0), 0.0)
        self.assertEqual(rse.quantile(vals, 0.5), 50.0)
        self.assertEqual(rse.quantile(vals, 1.0), 99.0)

    def test_max_run(self):
        self.assertEqual(rse.max_run([False, True, True, False, True]), 2)
        self.assertEqual(rse.max_run([False, False]), 0)


class TestCandidateRanking(unittest.TestCase):
    """The language layer is the correctness lever - these pin that it behaves sanely."""

    def _model(self):
        import candidate_ranking as cr
        return cr.SymbolModel.from_counts(
            {"a": 40, "b": 10, "c": 30, "e": 50, "n": 25},
            {("a", "b"): 8, ("b", "e"): 6, ("e", "a"): 5, ("a", "c"): 7, ("c", "e"): 9})

    def test_posterior_is_a_distribution(self):
        import candidate_ranking as cr
        scored = [("a", -0.2), ("b", -1.5), ("c", -3.0)]
        post = cr.posterior(scored)
        self.assertAlmostEqual(sum(p for _s, p in post), 1.0, places=9)
        self.assertEqual(post[0][0], "a", "posterior preserves the ranking")

    def test_posterior_is_scale_free(self):
        """Decision must not depend on how many symbols the lexicon happens to contain."""
        import candidate_ranking as cr
        small = cr.posterior([("a", -1.0), ("b", -1.2)])
        big = cr.posterior([("a", -11.0), ("b", -11.2)])
        self.assertAlmostEqual(dict(small)["a"], dict(big)["a"], places=9)

    def test_language_evidence_can_overrule_geometry(self):
        """With comparable unigram evidence, a strong bigram decides.

        Two earlier versions of this test asserted that language evidence beats an
        overwhelming unigram. It does not, and should not: the interpolation weights a
        bigram at alpha=0.65, so a near-certain unigram survives. That conservatism is
        deliberate - a steno decoder that lets a bigram overrule a confident geometric read
        will turn clear signals into wrong ones. The useful property is that language evidence
        decides when the unigram evidence is comparable.
        """
        import candidate_ranking as cr
        m = cr.SymbolModel.from_counts({"a": 100, "q": 100}, {("a", "q"): 80})
        tied = m.score([("a", 0.50), ("q", 0.50)], prev="a")
        self.assertEqual(tied[0][0], "q", "comparable unigrams -> the bigram decides")
        wide = m.score([("a", 0.95), ("q", 0.30)], prev="a")
        self.assertEqual(wide[0][0], "a", "a wide geometry gap still wins")
        conservative = cr.SymbolModel.from_counts({"a": 1000, "q": 1}, {("a", "q"): 100})
        held = conservative.score([("a", 0.50), ("q", 0.50)], prev="a")
        self.assertEqual(held[0][0], "a",
                         "a near-certain unigram is not overruleable - by design")

    def test_ambiguous_candidates_are_retracted_not_committed(self):
        """Retraction triggers on a low posterior, not on weak geometry.

        A first version used two candidates with a large unigram difference and expected a
        retraction; the model committed, correctly, because with no preceding symbol the
        unigram is the only evidence and it was decisive. Genuine ambiguity is two
        candidates that the language model cannot separate.
        """
        import candidate_ranking as cr
        m = self._model()
        text, log = cr.decode_stream(
            [(0.0, 0.5, [("a", 0.50), ("c", 0.50)])], m, )
        self.assertEqual(log[0]["action"], "retract")
        self.assertEqual(text, "")

    def test_retraction_undoes_the_previous_commit(self):
        import candidate_ranking as cr
        m = cr.SymbolModel.from_counts(
            {"x": 100, "y": 100}, {("x", "y"): 1}, commit_posterior=0.55)
        # first stroke is unambiguous, second is a coin flip between two even-frequency letters
        strokes = [(0.0, 0.9, [("x", 0.9)]), (0.1, 0.5, [("y", 0.5), ("x", 0.5)])]
        text, log = cr.decode_stream(strokes, m)
        self.assertEqual(log[0]["action"], "commit")
        self.assertIn("retract", [e["action"] for e in log],
                      "an ambiguous stroke must be retracted, not committed")
        self.assertLessEqual(len(text), 1)

    def test_correction_load_scales_with_event_rate(self):
        import lm_recovery as lr
        res = {"retract_rate": 0.2}
        a = lr.correction_load(res, 3.0)["corrections_per_s"]
        b = lr.correction_load(res, 6.0)["corrections_per_s"]
        self.assertAlmostEqual(b, 2 * a, places=6)


    def test_word_retraction_costs_one_action_not_one_per_character(self):
        import candidate_ranking as cr
        m = cr.SymbolModel.from_counts(
            {"a": 100, "e": 100, "l": 50, "o": 80},
            {("a", "l"): 20, ("l", "o"): 18, ("o", "v"): 15, ("v", "e"): 20})
        words = [[[("a", 0.6), ("e", 0.3)], [("l", 0.4), ("o", 0.35)],
                  [("o", 0.55), ("i", 0.2)], [("e", 0.5), ("a", 0.3)],
                  [("v", 0.45), ("b", 0.2)]]]
        text, log = cr.decode_words(words, m)
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["action"], "retract_word")
        self.assertEqual(log[0]["cost_actions"], 1)
        self.assertGreater(len(log[0]["weak_positions"]), 1,
                           "the point is that several weak characters cost one action")

    def test_clean_words_still_commit(self):
        import candidate_ranking as cr
        m = cr.SymbolModel.from_counts(
            {"a": 100, "l": 50, "o": 80, "v": 50},
            {("a", "l"): 20, ("l", "o"): 18, ("o", "v"): 15})
        words = [[[("a", 0.98)], [("l", 0.97)], [("o", 0.96)], [("v", 0.95)]]]
        text, log = cr.decode_words(words, m)
        self.assertEqual(log[0]["action"], "commit")
        self.assertIn("a", text)


class TestRankSeamIntegration(unittest.TestCase):
    """candidate_ranker (seam) and candidate_ranking (model) must compose, not duplicate."""

    def _fixture(self):
        import candidate_ranker as seam
        import candidate_ranking as lang
        # No a->l bigram and a low unigram for l, so 'l' wins on geometry alone while
        # 'e' wins on language. The first version of this fixture included an a->l bigram,
        # which made 'l' legitimately win and made the test meaningless.
        model = lang.SymbolModel.from_counts(
            {"a": 40, "e": 50, "i": 25, "l": 10}, {})
        cands = [{"text": "l", "confidence": 0.34},
                 {"text": "i", "confidence": 0.30},
                 {"text": "e", "confidence": 0.22}]
        return seam, model, cands

    def test_language_can_overrule_the_geometric_favourite_through_the_seam(self):
        import rank_seam_demo as demo
        seam, model, cands = self._fixture()
        scores = demo.language_scores_for(cands, model, prev="a")
        ranked = seam.rank_candidates(cands, language_scores=scores)
        top = ranked["selected"]["text"]
        self.assertNotEqual(top, "l", "the most confident candidate must not always win")

    def test_seam_alone_keeps_the_geometric_order(self):
        """Without a language model the seam must be a no-op, not a hidden scorer."""
        seam, _model, cands = self._fixture()
        ranked = seam.rank_candidates(cands)
        self.assertEqual([r["candidate"]["text"] for r in ranked["ranked"]],
                         ["l", "i", "e"])

    def test_seam_and_model_agree_on_the_synthetic_case(self):
        import rank_seam_demo as demo
        seam, model, cands = self._fixture()
        scores = demo.language_scores_for(cands, model, prev="a")
        seam_order = [r["candidate"]["text"]
                      for r in seam.rank_candidates(cands, language_scores=scores)["ranked"]]
        model_order = [s for s, _lp in model.score(
            [(c["text"], c["confidence"]) for c in cands], "a")]
        self.assertEqual(seam_order, model_order)

    def test_seam_preserves_provenance(self):
        seam, _model, cands = self._fixture()
        out = seam.rank_candidates(cands)
        self.assertIn("schema", out)
        self.assertIn("version", out)
        self.assertTrue(all("candidate" in r and "rank_score" in r for r in out["ranked"]))

if __name__ == "__main__":
    unittest.main()
