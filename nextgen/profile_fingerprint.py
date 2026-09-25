"""Reproducible SHA-256 digest of the declared English steno profile.

This is a digest of declared profile data, not evidence that the profile is
correct, not a performance claim, and not a validation result.  If the profile
changes, the fingerprint changes, and that is the entire point.

Canonical form
--------------
``canonical_profile_bytes()`` reads these inputs, in this exact order, directly
from their defining modules: ``STROKE_LIBRARY``, ``COLUMN_TO_FINGER``,
``CODE_OFFSET``, ``CODE_COLUMNS``, ``MESSAGE_MASKS``, ``STENO_KEYS``,
``CONTRACT_VERSION``, and ``PROFILE_ID``.  The result is the UTF-8 encoding of
one or more records in the form ``NAME=JSON``.  Each JSON value uses compact
separators ``,`` and ``:``, keys sorted lexicographically, ASCII preserved, and
non-finite numbers rejected.  Stroke objects become objects with ``keys`` and
``notation`` fields; sets and frozensets become lexicographically sorted lists;
all other supported declared values keep their semantic sequence or scalar
form.  Records are joined by one US (0x1f) byte, with no leading or trailing
separator.  The returned bytes are hashed directly with SHA-256; no text
normalisation or trailing newline is applied.

The digest cannot capture whether the declared values are correct, ergonomic,
usable on hardware, or supported by measurements.  It captures only these
profile declarations and their order-independent set membership, represented
through the canonical form above.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from .boundary import CONTRACT_VERSION, PROFILE_ID
from .english_steno import (
    CODE_COLUMNS,
    CODE_OFFSET,
    COLUMN_TO_FINGER,
    MESSAGE_MASKS,
    STENO_KEYS,
    STROKE_LIBRARY,
)

COVERED_INPUTS: tuple[str, ...] = (
    "STROKE_LIBRARY",
    "COLUMN_TO_FINGER",
    "CODE_OFFSET",
    "CODE_COLUMNS",
    "MESSAGE_MASKS",
    "STENO_KEYS",
    "CONTRACT_VERSION",
    "PROFILE_ID",
)

_FIELD_SEPARATOR = b"\x1f"


def _canonical_value(name: str, value: Any) -> Any:
    """Convert one declared value to JSON-compatible profile data."""
    if is_dataclass(value) and not isinstance(value, type):
        value = asdict(value)
    if isinstance(value, (set, frozenset)):
        try:
            return sorted(value)
        except TypeError as error:
            raise ValueError(f"profile input {name} contains mixed-type values") from error
    if isinstance(value, dict):
        return {str(key): _canonical_value(name, item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(name, item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ValueError(
        f"profile input {name} has unsupported type {type(value).__name__}"
    )


def _require_declared(name: str, value: Any) -> Any:
    """Reject missing, empty, or unsupported declared profile inputs."""
    if value in (None, "", (), [], {}, set(), frozenset()):
        raise ValueError(f"profile input {name} is empty")
    return _canonical_value(name, value)


def canonical_profile_bytes() -> bytes:
    """Return the exact canonical byte string whose SHA-256 digest is used."""
    values = (
        _require_declared("STROKE_LIBRARY", STROKE_LIBRARY),
        _require_declared("COLUMN_TO_FINGER", COLUMN_TO_FINGER),
        _require_declared("CODE_OFFSET", CODE_OFFSET),
        _require_declared("CODE_COLUMNS", CODE_COLUMNS),
        _require_declared("MESSAGE_MASKS", MESSAGE_MASKS),
        _require_declared("STENO_KEYS", STENO_KEYS),
        _require_declared("CONTRACT_VERSION", CONTRACT_VERSION),
        _require_declared("PROFILE_ID", PROFILE_ID),
    )
    records = []
    for name, value in zip(COVERED_INPUTS, values, strict=True):
        encoded = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        records.append(f"{name}={encoded}".encode("utf-8"))
    return _FIELD_SEPARATOR.join(records)


def layout_fingerprint() -> str:
    """Return the lowercase 64-character SHA-256 profile fingerprint."""
    return hashlib.sha256(canonical_profile_bytes()).hexdigest()


LAYOUT_FINGERPRINT = layout_fingerprint()


def _print_fingerprint() -> None:
    """Print the derived value and the declarations it covers."""
    print(f"LAYOUT_FINGERPRINT={LAYOUT_FINGERPRINT}")
    print("covered inputs:")
    for name in COVERED_INPUTS:
        print(f"- {name}")


if __name__ == "__main__":
    _print_fingerprint()
