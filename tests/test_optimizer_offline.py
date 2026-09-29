import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("layout_optimizer", ROOT / "layout_optimizer.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class OfflineSelfTestCorpusTests(unittest.TestCase):
    def test_fixture_covers_full_inventory_without_external_corpus(self):
        corpus = module.self_test_corpus()
        self.assertEqual(corpus.phones_seen, module.PHONEMES)
        self.assertEqual(len(corpus.words), 2 * len(module.PHONEMES))
        self.assertEqual(corpus.provenance["source"], "deterministic self-test fixture")

    def test_offline_self_test_entrypoint_does_not_need_cache(self):
        self.assertEqual(module.main(["--self-test", "--offline", "--quiet"]), 0)


if __name__ == "__main__":
    unittest.main()
