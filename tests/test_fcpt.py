import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nextgen.fcpt import (  # noqa: E402
    ASSUMPTION_ONLY,
    CELL_COUNT,
    ENVELOPE_HEIGHT_MM,
    ENVELOPE_WIDTH_MM,
    GRID_COLUMNS,
    GRID_ROWS,
    MAX_EXHAUSTIVE_SYMBOLS,
    TARGET_GEOMETRY,
    CorpusTransition,
    ProvisionalFCPTParameters,
    build_target_geometry,
    evaluate_layout,
    exhaustive_layout,
    greedy_layout,
    optimize_layout,
)


class TestFCPTGeometry(unittest.TestCase):
    def test_geometry_has_24_unique_bounded_row_major_cells(self):
        geometry = build_target_geometry()

        self.assertEqual(geometry, TARGET_GEOMETRY)
        self.assertEqual(len(geometry), CELL_COUNT)
        self.assertEqual(CELL_COUNT, GRID_COLUMNS * GRID_ROWS)
        self.assertEqual(len({cell.cell_id for cell in geometry}), CELL_COUNT)
        self.assertEqual(len({(cell.x_mm, cell.y_mm) for cell in geometry}), CELL_COUNT)
        for cell in geometry:
            self.assertTrue(0.0 <= cell.x_mm <= ENVELOPE_WIDTH_MM)
            self.assertTrue(0.0 <= cell.y_mm <= ENVELOPE_HEIGHT_MM)
            self.assertTrue(math.isfinite(cell.x_mm))
            self.assertTrue(math.isfinite(cell.y_mm))
        for row in range(GRID_ROWS):
            row_cells = geometry[row * GRID_COLUMNS:(row + 1) * GRID_COLUMNS]
            self.assertEqual(len({cell.y_mm for cell in row_cells}), 1)
            self.assertEqual(
                [cell.cell_id for cell in row_cells],
                list(range(row * GRID_COLUMNS, (row + 1) * GRID_COLUMNS)),
            )

    def test_geometry_has_orthogonal_horizontal_and_vertical_neighbors(self):
        first = TARGET_GEOMETRY[0]
        horizontal = TARGET_GEOMETRY[1]
        vertical = TARGET_GEOMETRY[GRID_COLUMNS]
        diagonal = TARGET_GEOMETRY[GRID_COLUMNS + 1]

        self.assertAlmostEqual(horizontal.x_mm - first.x_mm, 4.0)
        self.assertAlmostEqual(vertical.y_mm - first.y_mm, 4.0)
        self.assertAlmostEqual(
            math.hypot(diagonal.x_mm - first.x_mm, diagonal.y_mm - first.y_mm),
            math.hypot(4.0, 4.0),
        )


class TestFCPTCost(unittest.TestCase):
    def test_coefficients_are_explicitly_assumption_only_and_finite(self):
        parameters = ProvisionalFCPTParameters()

        self.assertTrue(parameters.assumption_only)
        self.assertEqual(parameters.assumption_note, ASSUMPTION_ONLY)
        self.assertIn("ASSUMPTION ONLY", parameters.assumption_note)
        self.assertTrue(all(math.isfinite(value) for value in (
            parameters.intercept,
            parameters.slope,
            parameters.target_width_mm,
        )))

    def test_objective_uses_shannon_fitts_form_and_corpus_weights(self):
        parameters = ProvisionalFCPTParameters()
        corpus = (
            CorpusTransition("A", "B", weight=1.0),
            CorpusTransition("B", "A", weight=3.0),
        )
        placements = {"A": 0, "B": 6}
        first = TARGET_GEOMETRY[0]
        second = TARGET_GEOMETRY[6]
        adjacent = parameters.intercept + parameters.slope * math.log2(1.0 + 4.0 / 3.0)
        long_jump = parameters.intercept + parameters.slope * math.log2(
            1.0 + math.hypot(
                second.x_mm - first.x_mm,
                second.y_mm - first.y_mm,
            ) / 3.0,
        )
        expected_mean = (adjacent + 3.0 * long_jump) / 4.0

        objective = evaluate_layout(placements, corpus, parameters=parameters)

        self.assertTrue(math.isfinite(objective.mean_model_cost))
        self.assertTrue(math.isfinite(objective.total_weighted_cost))
        self.assertAlmostEqual(objective.mean_model_cost, expected_mean)
        self.assertAlmostEqual(objective.total_weight, 4.0)
        self.assertAlmostEqual(
            objective.total_weighted_cost,
            adjacent + 3.0 * long_jump,
        )
        self.assertEqual(objective.transition_count, 2)
        self.assertTrue(objective.assumption_only)

    def test_self_transition_is_finite(self):
        objective = evaluate_layout(
            {"A": 0},
            (CorpusTransition("A", "A"),),
        )

        self.assertAlmostEqual(objective.mean_model_cost, 0.150)
        self.assertTrue(math.isfinite(objective.mean_model_cost))


class TestFCPTAssignment(unittest.TestCase):
    def setUp(self):
        self.corpus = (
            CorpusTransition("B", "A", weight=3.0),
            CorpusTransition("A", "B", weight=1.0),
        )

    def assert_valid_assignment(self, assignment):
        assignment.validate()
        self.assertEqual(len(assignment.placements), 2)
        self.assertEqual(len({cell_id for _, cell_id in assignment.placements}), 2)
        self.assertEqual(assignment.as_dict(), dict(assignment.placements))
        self.assertTrue(math.isfinite(assignment.objective.mean_model_cost))

    def test_exhaustive_and_greedy_find_deterministic_adjacent_layout(self):
        exhaustive = exhaustive_layout(("B", "A"), self.corpus)
        greedy = greedy_layout(("B", "A"), self.corpus)

        self.assert_valid_assignment(exhaustive)
        self.assert_valid_assignment(greedy)
        self.assertEqual(exhaustive.as_dict(), {"A": 0, "B": 1})
        self.assertEqual(greedy.as_dict(), {"A": 0, "B": 1})
        self.assertEqual(exhaustive.method, "exhaustive")
        self.assertEqual(greedy.method, "greedy")

    def test_dispatch_preserves_selected_method(self):
        exhaustive = optimize_layout(
            ("A", "B"),
            self.corpus,
            method="exhaustive",
        )
        greedy = optimize_layout(("A", "B"), self.corpus, method="greedy")

        self.assertEqual(exhaustive.as_dict(), greedy.as_dict())
        self.assertEqual(exhaustive.method, "exhaustive")
        self.assertEqual(greedy.method, "greedy")

    def test_greedy_can_fill_all_24_cells(self):
        symbols = tuple(f"S{index:02d}" for index in range(CELL_COUNT))
        corpus = tuple(
            CorpusTransition(symbols[index - 1], symbols[index], weight=index)
            for index in range(1, CELL_COUNT)
        )

        assignment = greedy_layout(symbols, corpus)

        assignment.validate()
        self.assertEqual(set(assignment.as_dict().values()), set(range(CELL_COUNT)))
        self.assertTrue(math.isfinite(assignment.objective.mean_model_cost))

    def test_exhaustive_search_has_an_explicit_small_table_bound(self):
        symbols = tuple(f"S{index}" for index in range(MAX_EXHAUSTIVE_SYMBOLS + 1))
        corpus = (CorpusTransition(symbols[0], symbols[1]),)

        with self.assertRaisesRegex(ValueError, f"bounded to {MAX_EXHAUSTIVE_SYMBOLS} symbols"):
            exhaustive_layout(symbols, corpus)

    def test_rejects_duplicate_cells_and_unknown_corpus_symbols(self):
        with self.assertRaisesRegex(ValueError, "cell at most once"):
            evaluate_layout({"A": 0, "B": 0}, self.corpus)
        with self.assertRaisesRegex(ValueError, "declared symbols"):
            evaluate_layout(
                {"A": 0, "B": 1},
                (CorpusTransition("A", "missing"),),
            )

    def test_rejects_nonfinite_or_nonpositive_numeric_inputs(self):
        for name, values in (
            ("infinite intercept", {"intercept": float("inf")}),
            ("zero slope", {"slope": 0.0}),
            ("negative width", {"target_width_mm": -1.0}),
        ):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    ProvisionalFCPTParameters(**values)
        with self.assertRaises(ValueError):
            CorpusTransition("A", "B", weight=float("nan"))
        with self.assertRaises(ValueError):
            CorpusTransition("A", "B", weight=0.0)

    def test_rejects_invalid_layout_shape_and_method(self):
        with self.assertRaisesRegex(ValueError, "declared symbols"):
            evaluate_layout({"A": 0}, self.corpus)
        with self.assertRaisesRegex(ValueError, "method must be"):
            optimize_layout(("A", "B"), self.corpus, method="unknown")


if __name__ == "__main__":
    unittest.main()
