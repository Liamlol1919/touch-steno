import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import plover_dictionary_check  # noqa: E402


class TestPloverDictionaryCheck(unittest.TestCase):
    def _write(self, root: Path, name: str, data: str) -> Path:
        path = root / name
        path.write_text(data, encoding="utf-8")
        return path

    def test_valid_layered_dictionary_has_no_conflicts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            stock = self._write(root, "stock.json", json.dumps({"KAT": "cat"}))
            briefs = self._write(root, "briefs.json", json.dumps({"TP": "the"}))
            report = plover_dictionary_check.check_files([stock, briefs])
        self.assertTrue(report["valid"])
        self.assertEqual(report["entries"], 2)
        self.assertEqual(report["conflicts"], [])

    def test_duplicate_outline_in_same_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write(Path(td), "bad.json", '{"KAT":"cat","KAT":"catalog"}')
            report = plover_dictionary_check.check_files([path])
        self.assertFalse(report["valid"])
        self.assertIn("duplicate JSON key", report["errors"][0]["error"])

    def test_same_outline_in_layers_is_reported_as_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            a = self._write(root, "a.json", json.dumps({"KAT": "cat"}))
            b = self._write(root, "b.json", json.dumps({"KAT": "catalog"}))
            report = plover_dictionary_check.check_files([a, b])
        self.assertFalse(report["valid"])
        self.assertEqual(report["conflicts"][0]["outline"], "KAT")

    def test_invalid_outline_and_empty_translation_are_errors(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._write(Path(td), "bad.json", json.dumps({"bad key": ""}))
            report = plover_dictionary_check.check_files([path])
        self.assertFalse(report["valid"])
        self.assertEqual(len(report["errors"]), 2)


if __name__ == "__main__":
    unittest.main()
