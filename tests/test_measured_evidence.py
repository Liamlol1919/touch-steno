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

class TestWpmCeiling(unittest.TestCase):
    def test_250_wpm_two_events_per_syllable_exceeds_the_ceiling(self):
        ceiling = wpm_ceiling.event_ceiling_hz()
        need = (250 / 60.0) * 1.5 * 2.0
        self.assertGreater(need, ceiling,
                           "250 WPM with 2 events/syllable must exceed the "
                           "88 ms detector ceiling -- this is the project constraint")

    def test_250_wpm_one_event_per_syllable_fits_under_the_ceiling(self):
        ceiling = wpm_ceiling.event_ceiling_hz()
        need = (250 / 60.0) * 1.5 * 1.0
        self.assertLess(need, ceiling)

    def test_every_target_exceeds_measured_free_motion(self):
        for target in wpm_ceiling.TARGETS_WPM:
            need = (target / 60.0) * 1.5 * 1.0
            self.assertGreater(need, wpm_ceiling.MOVE_EVENT_RATE_HZ)

    def test_rest_run_is_shorter_than_the_detector_window(self):
        """The 88 ms window exists precisely because rest runs reach 7 frames."""
        self.assertLess(wpm_ceiling.REST_RUN_MAX_MS, wpm_ceiling.EVENT_MS)
        self.assertAlmostEqual(wpm_ceiling.EVENT_MS / (1000.0 / wpm_ceiling.HZ), 8.0,
                               places=0)


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
        sessions = [Path.home() / "Projekte/commindv2/messung" / n
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

class TestQuantileHelpers(unittest.TestCase):
    def test_quantile_bounds(self):
        vals = [float(i) for i in range(100)]
        self.assertEqual(rse.quantile(vals, 0.0), 0.0)
        self.assertEqual(rse.quantile(vals, 0.5), 50.0)
        self.assertEqual(rse.quantile(vals, 1.0), 99.0)

    def test_max_run(self):
        self.assertEqual(rse.max_run([False, True, True, False, True]), 2)
        self.assertEqual(rse.max_run([False, False]), 0)


if __name__ == "__main__":
    unittest.main()
