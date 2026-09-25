#!/usr/bin/env python3
"""Validate layered Plover JSON dictionaries and report outline collisions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "touchsteno.plover_dictionary_check"
VERSION = 1
STENO_KEYS = set("STKPWHRAO*EUFRPBLGTSDZ")


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _valid_outline(outline: str) -> bool:
    if not isinstance(outline, str) or not outline:
        return False
    strokes = outline.split("/")
    return all(stroke and set(stroke) <= STENO_KEYS for stroke in strokes)


def check_files(paths: list[Path]) -> dict:
    files, errors, entries, owners = [], [], 0, {}
    conflicts = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"),
                             object_pairs_hook=_reject_duplicate_keys)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            errors.append({"file": path.name, "error": str(exc)})
            continue
        if not isinstance(data, dict):
            errors.append({"file": path.name, "error": "top-level JSON must be an object"})
            continue
        files.append(path.name)
        for outline, translation in data.items():
            entries += 1
            if not _valid_outline(outline):
                errors.append({"file": path.name, "outline": outline,
                               "error": "invalid steno outline"})
            if not isinstance(translation, str) or not translation.strip():
                errors.append({"file": path.name, "outline": outline,
                               "error": "translation must be a non-empty string"})
            previous = owners.get(outline)
            if previous is not None:
                conflicts.append({"outline": outline, "files": [previous, path.name]})
            else:
                owners[outline] = path.name
    return {"schema": SCHEMA, "version": VERSION, "files": files,
            "entries": entries, "errors": errors, "conflicts": conflicts,
            "valid": not errors and not conflicts}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dictionaries", nargs="+", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    report = check_files(args.dictionaries)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
