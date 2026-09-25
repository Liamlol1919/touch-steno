import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import field_separability  # noqa: E402


BARE = [("N", [0.0]), ("S", [1.0]), ("E", [2.0]), ("W", [3.0]),
        ("NE", [4.0]), ("SW", [5.0]), ("NW", [6.0]), ("SE", [7.0])]


class TestAntipodalFold(unittest.TestCase):
    def test_bare_compass_names_fold_to_four_antipodal_classes(self):
        folded = field_separability.fold_compass_classes(BARE)
        self.assertEqual([label for label, _ in folded],
                         ["N/S", "N/S", "E/W", "E/W",
                          "NE/SW", "NE/SW", "NW/SE", "NW/SE"])
        self.assertEqual(len({label for label, _ in folded}), 4)

    def test_sector_prefixed_names_fold_to_the_same_classes(self):
        prefixed = [(f"sector_{label}", d) for label, d in BARE]
        self.assertEqual(field_separability.fold_compass_classes(prefixed),
                         field_separability.fold_compass_classes(BARE))

    def test_non_compass_label_is_rejected(self):
        with self.assertRaises(ValueError):
            field_separability.fold_compass_classes([("sector_HOME", [0.0])])
        with self.assertRaises(ValueError):
            field_separability.fold_compass_classes([("north", [0.0])])

    def test_folding_is_idempotent(self):
        once = field_separability.fold_compass_classes(BARE)
        twice = field_separability.fold_compass_classes(once)
        self.assertEqual(twice, once)


if __name__ == "__main__":
    unittest.main()
