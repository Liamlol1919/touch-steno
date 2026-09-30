import importlib.util
import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hardware_preflight", ROOT / "hardware_preflight.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class HardwarePreflightTests(unittest.TestCase):
    def test_evdev_handles_are_closed(self):
        opened = []

        class FakeDevice:
            name = "Wacom Intuos Pro M"

            def close(self):
                opened.append("closed")

        fake = types.SimpleNamespace(
            InputDevice=lambda node: FakeDevice(),
            list_devices=lambda: ["/dev/input/event99"],
        )
        old = sys.modules.get("evdev")
        sys.modules["evdev"] = fake
        try:
            self.assertEqual(module.main(["--no-usb"]), 0)
        finally:
            if old is None:
                sys.modules.pop("evdev", None)
            else:
                sys.modules["evdev"] = old
        self.assertEqual(opened, ["closed"])


if __name__ == "__main__":
    unittest.main()
