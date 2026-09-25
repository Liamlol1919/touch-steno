#!/usr/bin/env python3
"""Versioned raw contact-frame JSONL codec.

The analysis pipeline consumes a small canonical frame shape (``t`` + ``c``),
while recordings on disk carry an explicit schema name and version. Legacy
unversioned frames remain readable so existing sessions can be replayed.
"""
from __future__ import annotations

from typing import Any

SCHEMA = "touchsteno.raw_frame"
VERSION = 1


def encode_frame(t: float, contacts: dict[str, Any]) -> dict:
    """Encode one contact frame using raw-frame schema v1."""
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "t": float(t),
        "c": contacts,
    }


def decode_record(record: dict) -> dict:
    """Return the canonical analysis frame, accepting legacy records too.

    Unknown schemas and versions fail closed. Legacy records are accepted only
    when they have the historical ``t``/``c`` shape and no schema marker.
    """
    schema = record.get("schema")
    version = record.get("version")
    if schema is None:
        if version is not None:
            raise ValueError("raw frame has version without schema")
        if "t" not in record or "c" not in record:
            raise ValueError("legacy raw frame requires t and c")
        return {"t": float(record["t"]), "c": record["c"]}
    if schema != SCHEMA:
        raise ValueError(f"unsupported raw frame schema: {schema}")
    if type(version) is not int or version != VERSION:
        raise ValueError(f"unsupported raw frame version: {version}")
    if "t" not in record or "c" not in record:
        raise ValueError("raw frame v1 requires t and c")
    return {"t": float(record["t"]), "c": record["c"]}
