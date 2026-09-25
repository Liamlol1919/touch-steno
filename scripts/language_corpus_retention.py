#!/usr/bin/env python3
"""Report whether a local language corpus is retained or past its deletion date."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

SCHEMA = "touchsteno.language_corpus_retention"
VERSION = 1
REQUIRED = {"schema", "version", "consent", "split", "reference_file", "event_log", "retention_until"}


def _safe(root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return None
    return root / path


def retention_status(manifest_path: Path, *, today: date | None = None) -> dict:
    """Return retain/deleted/overdue/invalid without copying content or paths."""
    manifest_path = Path(manifest_path)
    errors = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"schema": SCHEMA, "version": VERSION, "state": "invalid",
                "deletion_due": None, "errors": [f"manifest unreadable: {exc}"]}
    if not isinstance(manifest, dict) or set(manifest) != REQUIRED | {
            "corpus_id", "reference_sha256", "event_log_sha256"}:
        errors.append("manifest fields do not match retention schema")
    if manifest.get("schema") != SCHEMA.replace("retention", "manifest") or manifest.get("version") != 1:
        errors.append("unsupported manifest schema/version")
    if manifest.get("consent") is not True or manifest.get("split") != "held_out":
        errors.append("consent and held_out split are required")
    until = None
    try:
        until = date.fromisoformat(manifest["retention_until"])
    except (KeyError, TypeError, ValueError):
        errors.append("retention_until must be an ISO date")
    reference = _safe(manifest_path.parent, manifest.get("reference_file"))
    event_log = _safe(manifest_path.parent, manifest.get("event_log"))
    if reference is None or event_log is None:
        errors.append("file paths must be relative and stay inside the manifest directory")
    if errors:
        return {"schema": SCHEMA, "version": VERSION, "state": "invalid",
                "deletion_due": None, "errors": errors}
    current = today or date.today()
    due = current >= until
    if not due:
        state = "retain"
    else:
        state = "deleted" if not reference.exists() and not event_log.exists() else "overdue"
    return {"schema": SCHEMA, "version": VERSION, "state": state,
            "deletion_due": due, "errors": []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--today", type=date.fromisoformat,
                        help="override current date for deterministic retention checks")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = retention_status(args.manifest, today=args.today)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.json:
        print(text)
    else:
        print(report["state"])
    return 0 if report["state"] in ("retain", "deleted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
