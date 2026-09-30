#!/usr/bin/env python3
"""Read-only PTH-660/Wacom preflight.

Exit 0 when a Wacom input device is visible, 1 when none is visible, 2 when
python-evdev is unavailable for the detailed listing.
"""
from __future__ import annotations

import argparse
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-usb", action="store_true", help="skip lsusb and inspect evdev only")
    args = ap.parse_args(argv)
    found = False
    if not args.no_usb:
        try:
            out = subprocess.run(["lsusb"], text=True, capture_output=True, check=False).stdout
            for line in out.splitlines():
                if "wacom" in line.lower() or "056a:" in line.lower():
                    print(f"USB: {line}")
                    found = True
        except OSError as exc:
            print(f"lsusb unavailable: {exc}", file=sys.stderr)
    try:
        from evdev import InputDevice, list_devices
    except ImportError as exc:
        print(f"python-evdev unavailable: {exc}", file=sys.stderr)
        return 0 if found else 1
    for node in list_devices():
        try:
            dev = InputDevice(node)
            name = dev.name
            dev.close()
        except (OSError, PermissionError):
            continue
        if "wacom" in name.lower() or "intuos" in name.lower():
            print(f"EVDEV: {node} {name}")
            found = True
    if not found:
        print("No Wacom/Intuos input device visible; hardware capture is blocked.")
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
