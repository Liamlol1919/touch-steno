#!/usr/bin/env python3
"""Validate a consented local held-out language corpus without copying its text.

The manifest binds a local reference file and semantic event log to SHA-256 hashes. The
validator reports only structural status and file hashes are never emitted in the result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path

SCHEMA = "touchsteno.language_corpus_manifest"
VERSION = 1
REQUIRED = {
    "schema", "version", "corpus_id", "consent", "split", "reference_file",
    "reference_sha256", "event_log", "event_log_sha256", "retention_until",
}
SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative_file(root: Path, value: object, label: str, errors: list[str]) -> Path | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{label} must be a relative path")
        return None
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        errors.append(f"{label} must stay within the manifest directory")
        return None
    return root / path


def check_manifest(manifest_path: Path) -> dict:
    """Validate metadata, hashes, consent, split, and semantic event-log schema."""
    manifest_path = Path(manifest_path)
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"schema": SCHEMA, "version": VERSION, "valid": False,
                "event_log_valid": False, "errors": [f"manifest unreadable: {exc}"]}
    if not isinstance(manifest, dict):
        return {"schema": SCHEMA, "version": VERSION, "valid": False,
                "event_log_valid": False, "errors": ["manifest must be an object"]}
    if set(manifest) != REQUIRED:
        errors.append("manifest fields do not match schema")
    if manifest.get("schema") != SCHEMA or manifest.get("version") != VERSION:
        errors.append("unsupported manifest schema/version")
    if not isinstance(manifest.get("corpus_id"), str) or not SAFE_ID.fullmatch(manifest["corpus_id"]):
        errors.append("corpus_id must be a short safe identifier")
    if manifest.get("consent") is not True:
        errors.append("consent must be explicitly true")
    if manifest.get("split") != "held_out":
        errors.append("split must be held_out")
    if not isinstance(manifest.get("retention_until"), str):
        errors.append("retention_until must be an ISO date")
    else:
        try:
            date.fromisoformat(manifest["retention_until"])
        except ValueError:
            errors.append("retention_until must be an ISO date")
    for key in ("reference_sha256", "event_log_sha256"):
        if not isinstance(manifest.get(key), str) or not SHA256.fullmatch(manifest[key]):
            errors.append(f"{key} must be a lowercase SHA-256 hex digest")

    reference = _relative_file(manifest_path.parent, manifest.get("reference_file"),
                               "reference_file", errors)
    event_log = _relative_file(manifest_path.parent, manifest.get("event_log"),
                               "event_log", errors)
    if reference is not None and event_log is not None and reference.resolve() == event_log.resolve():
        errors.append("reference_file and event_log must be separate files")
    for path, key in ((reference, "reference_sha256"), (event_log, "event_log_sha256")):
        if path is None:
            continue
        if not path.is_file():
            errors.append(f"{key} file is missing")
        elif isinstance(manifest.get(key), str) and SHA256.fullmatch(manifest[key]) and _sha256(path) != manifest[key]:
            errors.append(f"{key} does not match the local file")

    event_log_valid = False
    if event_log is not None and event_log.is_file():
        try:
            from language_layer_metrics import load_events
            load_events(event_log)
            event_log_valid = True
        except (OSError, ValueError) as exc:
            errors.append(f"event log invalid: {exc}")
    return {"schema": SCHEMA, "version": VERSION, "valid": not errors,
            "event_log_valid": event_log_valid, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = check_manifest(args.manifest)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.json:
        print(text)
    else:
        print("valid" if report["valid"] else "invalid")
        for error in report["errors"]:
            print(f"- {error}")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
