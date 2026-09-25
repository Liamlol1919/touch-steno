"""Tests for the Fitts aiming instrument.

EVERY TIMING NUMBER IN THIS FILE IS SYNTHETIC. No trial here came off a pad. The
tests exercise geometry, the ID transform, the least-squares fit, the refusal
policy and the residual report against manufactured data; none of them says
anything about this thumb's real a and b, which have never been measured.
"""
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import fitts_probe  # noqa: E402

SYNTHETIC_A_S = 0.210          # synthetic ground truth, not a measurement
SYNTHETIC_B_S_PER_BIT = 0.155  # synthetic ground truth, not a measurement


def _trial(label, x, y, mt, practice=False, w=fitts_probe.TARGET_WIDTH_MM, status="ok"):
    return {"label": label, "x_mm": x, "y_mm": y, "w_mm": w, "mt_s": mt,
            "start_t": 0.0, "end_t": mt, "samples": 20, "practice": practice,
            "status": status}


def _synthetic_session(count=40, a=SYNTHETIC_A_S, b=SYNTHETIC_B_S_PER_BIT):
    """A synthetic manifest: exact a + b*ID, no noise, so the fit must be exact.

    A perfect line is the only way to assert that the least squares recovers a and b
    rather than something close to them. Real aiming data is not this clean, which
    is exactly why the instrument also reports residuals.
    """
    cells = fitts_probe.grid_targets()
    by_label = {c["label"]: c for c in cells}
    labels = list(by_label)
    order = fitts_probe.target_order(labels, count + 1, seed=7)
    trials = []
    for prev_label, label in zip(order, order[1:]):
        d = fitts_probe.distance(by_label[prev_label], by_label[label])
        trials.append(_trial(label, by_label[label]["x_mm"], by_label[label]["y_mm"],
                             a + b * fitts_probe.fitts_id(d, fitts_probe.TARGET_WIDTH_MM)))
    return trials


class TestGridGeometry(unittest.TestCase):
    def test_24_cells_with_centres_4mm_apart(self):
        cells = fitts_probe.grid_targets()
        self.assertEqual(len(cells), 24)
        self.assertEqual((fitts_probe.GRID_COLS, fitts_probe.GRID_ROWS), (6, 4))
        self.assertEqual(fitts_probe.CELL_PITCH_MM, 4.0)
        self.assertEqual(len({c["label"] for c in cells}), 24)

    def test_horizontal_neighbours_are_exactly_one_pitch_apart(self):
        cells = fitts_probe.grid_targets()
        a1 = next(c for c in cells if c["label"] == "A1")
        b1 = next(c for c in cells if c["label"] == "B1")
        self.assertAlmostEqual(fitts_probe.distance(a1, b1), 4.0, places=12)

    def test_whole_array_fits_inside_the_measured_thumb_envelope(self):
        span_x, span_y = fitts_probe.grid_extent()
        self.assertEqual(fitts_probe.ENVELOPE_MM, (24.6, 18.2))
        self.assertLessEqual(span_x, 24.6)
        self.assertLessEqual(span_y, 18.2)
        self.assertTrue(fitts_probe.grid_fits_envelope())
        cells = fitts_probe.grid_targets()
        half = fitts_probe.TARGET_WIDTH_MM / 2.0
        self.assertLessEqual(max(c["x_mm"] for c in cells) + half, 24.6 / 2.0)
        self.assertLessEqual(max(c["y_mm"] for c in cells) + half, 18.2 / 2.0)

    def test_diagonal_and_farthest_corner_match_the_quoted_geometries(self):
        a1 = next(c for c in fitts_probe.grid_targets() if c["label"] == "A1")
        b2 = next(c for c in fitts_probe.grid_targets() if c["label"] == "B2")
        self.assertAlmostEqual(fitts_probe.distance(a1, b2), 5.656854249492381, places=12)
        a1 = next(c for c in fitts_probe.grid_targets() if c["label"] == "A1")
        f4 = next(c for c in fitts_probe.grid_targets() if c["label"] == "F4")
        self.assertAlmostEqual(fitts_probe.distance(a1, f4), 23.3238075793812, places=9)


class TestDistanceAndWidth(unittest.TestCase):
    def test_distance_is_centre_to_centre_for_a_known_pair(self):
        a1 = {"x_mm": -10.0, "y_mm": -6.0, "w_mm": 3.0}
        c3 = {"x_mm": 0.0, "y_mm": 6.0, "w_mm": 3.0}
        # dx = 10, dy = 12 -> sqrt(100 + 144)
        self.assertAlmostEqual(fitts_probe.distance(a1, c3), math.sqrt(244.0), places=12)
        self.assertAlmostEqual(fitts_probe.distance(a1, a1), 0.0, places=12)

    def test_width_is_the_cued_target_width_not_the_cell_pitch(self):
        cells = {c["label"]: c for c in fitts_probe.grid_targets()}
        self.assertEqual(cells["D2"]["w_mm"], 3.0)
        self.assertNotEqual(cells["D2"]["w_mm"], fitts_probe.CELL_PITCH_MM)

    def test_id_uses_that_distance_and_that_width(self):
        # D = 4.0 mm, W = 3.0 mm -> log2(1 + 4/3)
        self.assertAlmostEqual(fitts_probe.fitts_id(4.0, 3.0),
                               math.log2(1.0 + 4.0 / 3.0), places=12)
        self.assertAlmostEqual(fitts_probe.fitts_id(4.0, 3.0), 1.222392421336448, places=12)
        # the diagonal neighbour row of the project's rate table, recomputed here
        # from the definitions rather than copied from the table
        self.assertAlmostEqual(fitts_probe.fitts_id(5.656854249492381, 3.0),
                               1.5289, places=3)

    def test_id_rejects_a_non_positive_width(self):
        with self.assertRaises(ValueError):
            fitts_probe.fitts_id(4.0, 0.0)


class TestOlsFit(unittest.TestCase):
    def test_recovers_known_a_and_b_exactly_from_perfect_synthetic_data(self):
        # synthetic data, no noise: the fit must be exact, not approximately right
        xs = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
        ys = [SYNTHETIC_A_S + SYNTHETIC_B_S_PER_BIT * x for x in xs]
        fit = fitts_probe.ols(xs, ys)
        self.assertAlmostEqual(fit["intercept"], SYNTHETIC_A_S, places=12)
        self.assertAlmostEqual(fit["slope"], SYNTHETIC_B_S_PER_BIT, places=12)
        self.assertAlmostEqual(fit["rss"], 0.0, places=18)
        self.assertAlmostEqual(fit["se_slope"], 0.0, places=12)
        self.assertAlmostEqual(fit["r_squared"], 1.0, places=12)

    def test_fit_fitts_recovers_a_and_b_from_a_whole_synthetic_session(self):
        res = fitts_probe.fit_fitts(_synthetic_session(40))
        self.assertTrue(res["fitted"])
        # the first cued target has no predecessor, so 40 trials yield 39 usable
        self.assertEqual(res["trials_usable"], 39)
        self.assertAlmostEqual(res["a_s"], SYNTHETIC_A_S, places=12)
        self.assertAlmostEqual(res["b_s_per_bit"], SYNTHETIC_B_S_PER_BIT, places=12)
        self.assertAlmostEqual(res["rss"], 0.0, places=18)
        self.assertAlmostEqual(res["r_squared"], 1.0, places=12)
        self.assertEqual(len(res["residuals"]), 39)

    def test_standard_errors_grow_with_scatter(self):
        rng = __import__("random").Random(11)
        xs = [0.5 + 0.1 * i for i in range(40)]
        clean = [SYNTHETIC_A_S + SYNTHETIC_B_S_PER_BIT * x for x in xs]
        noisy = [y + rng.uniform(-0.05, 0.05) for y in clean]
        tight = fitts_probe.ols(xs, clean)
        loose = fitts_probe.ols(xs, noisy)
        self.assertGreater(loose["rss"], tight["rss"])
        self.assertGreater(loose["se_slope"], tight["se_slope"])
        self.assertGreater(loose["sigma"], tight["sigma"])

    def test_residual_sum_of_squares_is_reported(self):
        # synthetic data with a deliberate 0.1 s bump on one trial
        trials = _synthetic_session(30)
        trials[7] = dict(trials[7], mt_s=trials[7]["mt_s"] + 0.1)
        res = fitts_probe.fit_fitts(trials)
        self.assertTrue(res["fitted"])
        self.assertIn("rss", res)
        self.assertGreater(res["rss"], 0.0)
        self.assertAlmostEqual(res["rss"],
                               sum(r["residual_s"] ** 2 for r in res["residuals"]),
                               places=12)
        self.assertLess(res["r_squared"], 1.0)
        self.assertEqual(len(res["residuals"]), 29)

    def test_residual_sum_of_squares_is_zero_on_a_perfect_synthetic_line(self):
        # no noise means no scatter: RSS == 0 is the check that the reported line is
        # a real least-squares fit through the points and not a shortcut
        res = fitts_probe.fit_fitts(_synthetic_session(30))
        self.assertTrue(res["fitted"])
        self.assertAlmostEqual(res["rss"], 0.0, places=25)
        self.assertAlmostEqual(sum(r["residual_s"] ** 2 for r in res["residuals"]),
                               0.0, places=25)
        self.assertAlmostEqual(res["r_squared"], 1.0, places=12)


    def test_ols_refuses_a_degenerate_design(self):
        with self.assertRaises(ValueError):
            fitts_probe.ols([1.0, 1.0, 1.0], [0.2, 0.3, 0.4])


class TestRefusalAndExclusions(unittest.TestCase):
    def test_a_fit_below_twenty_usable_trials_is_refused(self):
        res = fitts_probe.fit_fitts(_synthetic_session(20))
        self.assertFalse(res["fitted"])
        self.assertNotIn("a_s", res)
        self.assertIn("refusing", res["refusal"])
        self.assertIn("19 usable", res["refusal"])

    def test_exactly_twenty_usable_trials_is_still_fitted(self):
        res = fitts_probe.fit_fitts(_synthetic_session(21))
        self.assertTrue(res["fitted"])
        self.assertEqual(res["trials_usable"], 20)

    def test_practice_trials_are_excluded_from_the_fit_but_name_the_start(self):
        trials = _synthetic_session(34)
        for i, t in enumerate(trials):
            t["practice"] = i < 4
        res = fitts_probe.fit_fitts(trials)
        self.assertEqual(res["trials_usable"], 30)
        self.assertEqual(res["trials_excluded"], 4)
        self.assertTrue(all(e["reason"] == "practice" for e in res["excluded"]))
        self.assertAlmostEqual(res["a_s"], SYNTHETIC_A_S, places=12)
        self.assertAlmostEqual(res["b_s_per_bit"], SYNTHETIC_B_S_PER_BIT, places=12)

    def test_first_cued_target_is_dropped_because_it_has_no_predecessor(self):
        # D is undefined without a previous cued target, so the instrument reports
        # the exclusion instead of inventing a start position
        res = fitts_probe.fit_fitts(_synthetic_session(30))
        self.assertEqual(res["trials_total"], 30)
        self.assertEqual(res["trials_usable"], 29)
        self.assertEqual(res["excluded"][0]["reason"], "no previous cued target")

    def test_incomplete_and_timeout_trials_are_excluded_with_the_reason(self):
        trials = _synthetic_session(24)
        trials[3] = dict(trials[3], status="moved but never settled in the cued target",
                         mt_s=None)
        trials[5] = dict(trials[5], status="no contact samples in the movement window",
                         mt_s=None)
        res = fitts_probe.fit_fitts(trials)
        self.assertEqual(res["trials_usable"], 21)
        reasons = {e["reason"] for e in res["excluded"]}
        self.assertIn("not a completed target hit: "
                      "moved but never settled in the cued target", reasons)
        self.assertIn("not a completed target hit: "
                      "no contact samples in the movement window", reasons)

    def test_non_positive_movement_time_is_excluded(self):
        trials = _synthetic_session(24)
        trials[2] = dict(trials[2], mt_s=0.0)
        res = fitts_probe.fit_fitts(trials)
        self.assertEqual(res["trials_usable"], 22)
        self.assertIn("no positive movement time",
                      {e["reason"] for e in res["excluded"]})


class TestRateTable(unittest.TestCase):
    def test_three_quoted_geometries_are_reported_with_and_without_the_delay(self):
        rows = fitts_probe.predicted_rates(fitts_probe.PLANNING_A_S,
                                            fitts_probe.PLANNING_B_S_PER_BIT)
        self.assertEqual([r["geometry"].split()[0] for r in rows],
                         ["adjacent", "diagonal", "farthest"])
        self.assertAlmostEqual(rows[0]["d_mm"], 4.0, places=12)
        self.assertAlmostEqual(rows[1]["d_mm"], 5.656854249492381, places=12)
        self.assertAlmostEqual(rows[2]["d_mm"], 23.3238075793812, places=9)
        for r in rows:
            self.assertAlmostEqual(r["mt_s"],
                                   fitts_probe.PLANNING_A_S
                                   + fitts_probe.PLANNING_B_S_PER_BIT * r["id"],
                                   places=12)
            self.assertAlmostEqual(r["rate_per_s"], 1.0 / r["mt_s"], places=12)
            self.assertAlmostEqual(r["mt_plus_delay_s"],
                                   r["mt_s"] + fitts_probe.PROCESSING_DELAY_S, places=12)
            self.assertAlmostEqual(r["rate_with_delay_per_s"],
                                   1.0 / r["mt_plus_delay_s"], places=12)
            self.assertLess(r["rate_with_delay_per_s"], r["rate_per_s"])

    def test_planning_values_reproduce_the_published_adjacent_rate(self):
        # BINDING_CONSTRAINT.md quotes 0.2967 s and 3.37 /s for the adjacent cell
        # from a = 0.150 s, b = 0.120 s/bit. That is the number being replaced.
        rows = fitts_probe.predicted_rates(0.150, 0.120)
        self.assertAlmostEqual(rows[0]["mt_s"], 0.2967, places=4)
        self.assertAlmostEqual(rows[0]["rate_per_s"], 3.37, places=2)


class TestCaptureWithoutHardware(unittest.TestCase):
    def test_import_needs_no_device_and_exposes_both_modes(self):
        self.assertTrue(hasattr(fitts_probe, "capture"))
        self.assertTrue(hasattr(fitts_probe, "analyse"))
        self.assertFalse(hasattr(fitts_probe, "WacomTouchReader"))

    def test_order_is_randomised_deterministically_for_a_seed(self):
        labels = [c["label"] for c in fitts_probe.grid_targets()]
        a = fitts_probe.target_order(labels, 30, seed=20260925)
        b = fitts_probe.target_order(labels, 30, seed=20260925)
        c = fitts_probe.target_order(labels, 30, seed=1)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, sorted(a))
        for prev, nxt in zip(a, a[1:]):
            self.assertNotEqual(prev, nxt)

    def test_onset_and_settle_rules_on_a_synthetic_contact_track(self):
        # synthetic track: 0.3 s still on the previous cell, then a straight move
        prev = {"x_mm": 0.0, "y_mm": 0.0}
        target = {"x_mm": 4.0, "y_mm": 0.0}
        points = [(i * 0.005, 0.0, 0.0) for i in range(60)]
        for k in range(200):
            frac = min(1.0, k / 100.0)
            points.append((0.30 + k * 0.005, 4.0 * frac, 0.0))
        for k in range(40):
            points.append((1.30 + k * 0.005, 4.0, 0.0))
        onset = fitts_probe._find_onset(points, (prev["x_mm"], prev["y_mm"]))
        self.assertIsNotNone(onset)
        settled = fitts_probe._find_settle(points, onset, target)
        self.assertIsNotNone(settled)
        first, last = settled
        # the settle index is the first sample inside the target radius ...
        self.assertLessEqual(math.hypot(points[first][1] - target["x_mm"],
                                        points[first][2] - target["y_mm"]),
                             fitts_probe.SETTLE_RADIUS_MM)
        # ... and the window it certifies spans at least the hold time
        self.assertGreaterEqual(points[last][0] - points[first][0],
                                fitts_probe.SETTLE_HOLD_S)
        # a sample just outside the radius is not accepted as the arrival
        self.assertGreater(math.hypot(points[first - 1][1] - target["x_mm"],
                                      points[first - 1][2] - target["y_mm"]),
                           fitts_probe.SETTLE_RADIUS_MM)

    def test_a_movement_that_never_settles_is_not_reported_as_a_hit(self):
        target = {"x_mm": 4.0, "y_mm": 0.0}
        points = [(k * 0.005, 4.0 * min(1.0, k / 50.0) * 0.5, 6.0) for k in range(200)]
        onset = fitts_probe._find_onset(points, (0.0, 0.0))
        self.assertIsNotNone(onset)
        self.assertIsNone(fitts_probe._find_settle(points, onset, target))


class TestManifestRoundTrip(unittest.TestCase):
    def _write(self, root: Path, trials: list[dict]) -> Path:
        path = root / "fitts_synthetic.jsonl"
        header = {"record": "header", "schema": fitts_probe.SCHEMA, "seed": 7,
                  "grid": {"cols": 6, "rows": 4, "pitch_mm": 4.0,
                           "target_width_mm": 3.0, "envelope_mm": [24.6, 18.2]},
                  "measures": "aiming time only; not a drawn-path primitive",
                  "layout_fingerprint": None}
        path.write_text("".join(json.dumps(r) + "\n" for r in [header, *trials]),
                        encoding="utf-8")
        return path

    def test_synthetic_manifest_loads_and_fits_device_free(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write(Path(td), _synthetic_session(40))
            header, trials = fitts_probe.load_manifest(path)
            self.assertEqual(header["schema"], fitts_probe.SCHEMA)
            self.assertEqual(len(trials), 40)
            res = fitts_probe.analyse(trials, header)
        self.assertTrue(res["fitted"])
        self.assertAlmostEqual(res["a_s"], SYNTHETIC_A_S, places=12)
        self.assertAlmostEqual(res["b_s_per_bit"], SYNTHETIC_B_S_PER_BIT, places=12)
        self.assertEqual(len(res["rates"]), 3)

    def test_analyse_cli_refuses_a_short_synthetic_session(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write(Path(td), _synthetic_session(8))
            out = subprocess.run(
                [sys.executable, str(SCRIPTS / "fitts_probe.py"),
                 "--mode", "analyse", "--in", str(path)],
                capture_output=True, text=True, check=True)
        self.assertIn("refusing to report a Fitts fit", out.stdout)
        self.assertNotIn("b (slope)", out.stdout)

    def test_analyse_cli_prints_coefficients_residuals_and_both_rate_columns(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write(Path(td), _synthetic_session(40))
            out = subprocess.run(
                [sys.executable, str(SCRIPTS / "fitts_probe.py"),
                 "--mode", "analyse", "--in", str(path)],
                capture_output=True, text=True, check=True)
        self.assertIn("a (intercept)", out.stdout)
        self.assertIn("b (slope)", out.stdout)
        self.assertIn("residual sum of sq", out.stdout)
        self.assertIn("RESIDUALS", out.stdout)
        self.assertIn("DERIVED from the fitted coefficients", out.stdout)
        self.assertIn("NOT a measured typing rate", out.stdout)
        self.assertIn("176 ms processing delay", out.stdout)
        self.assertIn("ASSUMPTIONS, not measurements", out.stdout)


if __name__ == "__main__":
    unittest.main()
