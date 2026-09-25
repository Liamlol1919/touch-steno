import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import language_corpus_manifest  # noqa: E402


class TestLanguageCorpusManifest(unittest.TestCase):
    def _fixture(self, root: Path, **overrides):
        reference = root / "reference.txt"
        events = root / "events.jsonl"
        reference.write_text("held out reference text\n", encoding="utf-8")
        events.write_text('{"event":"stroke"}\n{"event":"word","delta":1}\n',
                          encoding="utf-8")
        def digest(path):
            return hashlib.sha256(path.read_bytes()).hexdigest()
        manifest = {
            "schema": "touchsteno.language_corpus_manifest", "version": 1,
            "corpus_id": "p01-heldout", "consent": True, "split": "held_out",
            "reference_file": "reference.txt", "reference_sha256": digest(reference),
            "event_log": "events.jsonl", "event_log_sha256": digest(events),
            "retention_until": "2099-01-01",
        }
        manifest.update(overrides)
        path = root / "manifest.json"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        return path

    def test_valid_consented_heldout_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._fixture(Path(td))
            report = language_corpus_manifest.check_manifest(path)
        self.assertTrue(report["valid"])
        self.assertTrue(report["event_log_valid"])
        self.assertEqual(report["errors"], [])

    def test_consent_and_split_are_required(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._fixture(Path(td), consent=False, split="train")
            report = language_corpus_manifest.check_manifest(path)
        self.assertFalse(report["valid"])
        self.assertTrue(any("consent" in error for error in report["errors"]))
        self.assertTrue(any("held_out" in error for error in report["errors"]))

    def test_hash_mismatch_and_path_traversal_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = self._fixture(root, reference_sha256="0" * 64,
                                 reference_file="../outside.txt")
            report = language_corpus_manifest.check_manifest(path)
        self.assertFalse(report["valid"])
        self.assertTrue(any("manifest directory" in error for error in report["errors"]))

    def test_output_does_not_copy_reference_text_or_paths(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._fixture(Path(td))
            report = language_corpus_manifest.check_manifest(path)
        encoded = json.dumps(report)
        self.assertNotIn("held out reference text", encoded)
        self.assertNotIn("reference.txt", encoded)
        self.assertNotIn("events.jsonl", encoded)


if __name__ == "__main__":
    unittest.main()
