"""Next-generation English steno transport prototype.

The physical layer is a ten-bit, one-error-correcting contact code. It emits
canonical English steno strokes and ordered outlines for a Plover-compatible
adapter. It does not emit German steno or claim a complete English dictionary.
"""

from .english_steno import (
    CODE_COLUMNS,
    CODE_OFFSET,
    FINGER_NAMES,
    MESSAGE_MASKS,
    STENO_KEYS,
    STROKE_LIBRARY,
    DecodeResult,
    StenoCodec,
)

__all__ = [
    "CODE_COLUMNS",
    "CODE_OFFSET",
    "DecodeResult",
    "FINGER_NAMES",
    "MESSAGE_MASKS",
    "STENO_KEYS",
    "STROKE_LIBRARY",
    "StenoCodec",
]
