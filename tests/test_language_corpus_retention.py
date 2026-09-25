import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import language_corpus_retention  # noqa: E402


class TestLanguageCorpusRetention(unittest.TestCase):
    def _manifest(self, root, until):
        path = root / "manifest.json"
        path.write_text(json.dumps({
            "schema": "touchsteno.language_corpus_manifest", "version": 1,
            "corpus_id": "p01-heldout", "consent": True, "split": "held_out",
            "reference_file": "reference.txt", "reference_sha256": "0" * 64,
            "event_log": "events.jsonl", "event_log_sha256": "0" * 64,
            "retention_until": until,
        }), encoding="utf-8")
        return path

    def test_future_retention_is_retained(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._manifest(Path(td), "2099-01-01")
            report = language_corpus_retention.retention_status(
                path, today=date(2026, 9, 25))
        self.assertEqual(report["state"], "retain")
        self.assertFalse(report["deletion_due"])

    def test_due_and_absent_files_are_deleted(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._manifest(Path(td), "2026-09-01")
            report = language_corpus_retention.retention_status(
                path, today=date(2026, 9, 25))
        self.assertEqual(report["state"], "deleted")
        self.assertTrue(report["deletion_due"])

    def test_due_but_present_files_are_overdue(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = self._manifest(root, "2026-09-01")
            (root / "reference.txt").write_text("private", encoding="utf-8")
            (root / "events.jsonl").write_text("{}\n", encoding="utf-8")
            report = language_corpus_retention.retention_status(
                path, today=date(2026, 9, 25))
        self.assertEqual(report["state"], "overdue")

    def test_invalid_manifest_does_not_leak_content_or_paths(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "manifest.json"
            path.write_text(json.dumps({"schema": "wrong"}), encoding="utf-8")
            report = language_corpus_retention.retention_status(path)
        encoded = json.dumps(report)
        self.assertEqual(report["state"], "invalid")
        self.assertNotIn("reference.txt", encoded)
        self.assertNotIn("events.jsonl", encoded)


if __name__ == "__main__":
    unittest.main()
