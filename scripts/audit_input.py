#!/usr/bin/env python3
"""Safe Linux input audit for a PTH-660/touch tablet.

This script only enumerates evdev devices and capabilities. It does not grab
input, inject events, or modify permissions. Use --device to inspect a
specific /dev/input/eventN and --watch to record events after the device is
connected.

Examples:
  python3 scripts/audit_input.py
  python3 scripts/audit_input.py --device /dev/input/event20
  python3 scripts/audit_input.py --watch --seconds 30 --output data/pth-touch.jsonl
"""
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
from evdev import InputDevice, ecodes, list_devices

ABS = ecodes.EV_ABS
KEY = ecodes.EV_KEY
SYN = ecodes.EV_SYN


def abs_name(code: int) -> str:
    return ecodes.ABS.get(code, str(code))


def key_name(code: int) -> str:
    return ecodes.KEY.get(code, str(code))


def describe(path: str) -> dict:
    dev = InputDevice(path)
    capabilities = dev.capabilities(absinfo=True)
    caps = []
    for code, axis in capabilities.get(ABS, []):
        caps.append({
            "axis": abs_name(code),
            "code": code,
            "min": axis.min,
            "max": axis.max,
            "fuzz": axis.fuzz,
            "flat": axis.flat,
            "resolution": axis.resolution,
        })
    keys = [key_name(c) for c in capabilities.get(KEY, []) if c != 0]
    return {
        "path": path,
        "name": dev.name,
        "phys": dev.phys,
        "uniq": dev.uniq,
        "info": {k: getattr(dev.info, k) for k in ("vendor", "product", "version")},
        "abs": caps,
        "keys": keys,
    }


def decode(event, dev) -> dict:
    row = {
        "timestamp": event.timestamp,
        "type": ecodes.EV.get(event.type, str(event.type)),
        "code": ecodes.KEY.get(event.code, str(event.code))
        if event.type == KEY else
        ecodes.ABS.get(event.code, str(event.code))
        if event.type == ABS else
        ecodes.SYN.get(event.code, str(event.code))
        if event.type == SYN else str(event.code),
        "value": event.value,
    }
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", help="specific /dev/input/eventN")
    ap.add_argument("--watch", action="store_true", help="read events until duration expires")
    ap.add_argument("--seconds", type=float, default=30.0)
    ap.add_argument("--output", type=Path, help="JSONL event output")
    args = ap.parse_args()

    paths = [args.device] if args.device else sorted(list_devices())
    report = []
    for path in paths:
        try:
            report.append(describe(path))
        except PermissionError:
            report.append({"path": path, "error": "permission denied"})
        except OSError as exc:
            report.append({"path": path, "error": str(exc)})
    print(json.dumps(report, indent=2, sort_keys=True))

    if args.watch:
        if not args.device:
            raise SystemExit("--watch requires --device")
        if not args.output:
            raise SystemExit("--watch requires --output")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        dev = InputDevice(args.device)
        deadline = time.monotonic() + args.seconds
        with args.output.open("w", encoding="utf-8") as fp:
            fp.write(json.dumps({"device": describe(args.device)}) + "\n")
            for event in dev.read_loop():
                if time.monotonic() >= deadline:
                    break
                if event.type in (ABS, KEY, SYN):
                    fp.write(json.dumps(decode(event, dev), sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
