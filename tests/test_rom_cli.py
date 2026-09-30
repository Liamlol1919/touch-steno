import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rom_capture", ROOT / "rom_capture.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class RomCliTests(unittest.TestCase):
    def test_out_dir_is_forwarded_to_auto_capture(self):
        captured = {}
        old_run_auto = module.run_auto
        old_print_diag = module.print_diag
        old_print_diag = module.print_diag

        def fake_run_auto(args):
            captured["out_dir"] = args.out_dir
            captured["device"] = args.device
            return {"_status": "ACCEPTED"}, {"source": "test"}

        module.run_auto = fake_run_auto
        module.print_diag = lambda diag: None
        try:
            with tempfile.TemporaryDirectory() as tmp:
                expected = Path(tmp) / "raw"
                profile = Path(tmp) / "profile.json"
                module.main(["--device", "/dev/input/event19", "--out-dir", str(expected), "--profile", str(profile)])
        finally:
            module.run_auto = old_run_auto
            module.print_diag = old_print_diag
        self.assertEqual(captured["out_dir"], expected)


if __name__ == "__main__":
    unittest.main()
