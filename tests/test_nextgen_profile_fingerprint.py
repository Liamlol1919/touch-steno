import importlib
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from nextgen import profile_fingerprint  # noqa: E402


class TestProfileFingerprint(unittest.TestCase):
    def test_digest_is_lowercase_sha256_hex(self):
        digest = profile_fingerprint.layout_fingerprint()
        self.assertIsNotNone(re.fullmatch(r"[0-9a-f]{64}", digest))

    def test_digest_is_deterministic_across_calls(self):
        self.assertEqual(
            profile_fingerprint.layout_fingerprint(),
            profile_fingerprint.layout_fingerprint(),
        )

    def test_digest_is_stable_after_fresh_module_reimport(self):
        expected = profile_fingerprint.layout_fingerprint()
        reloaded = importlib.reload(profile_fingerprint)
        self.assertEqual(reloaded.layout_fingerprint(), expected)
        self.assertEqual(reloaded.LAYOUT_FINGERPRINT, expected)

    def test_canonical_bytes_name_every_covered_input(self):
        canonical = profile_fingerprint.canonical_profile_bytes()
        for name in profile_fingerprint.COVERED_INPUTS:
            with self.subTest(name=name):
                self.assertIn(f"{name}=".encode("utf-8"), canonical)
