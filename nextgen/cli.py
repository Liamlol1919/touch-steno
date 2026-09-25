"""Command-line interface for the next-generation English steno transport."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .english_steno import MESSAGE_MASKS, StenoCodec


def _parse_mask(value: str) -> int:
    value = value.strip()
    try:
        if value.lower().startswith("0b") or (len(value) == 10 and set(value) <= {"0", "1"}):
            return int(value, 2)
        return int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid contact mask: {value}") from exc



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    encode = sub.add_parser("encode", help="encode a slash-separated English steno outline")
    encode.add_argument("outline")
    encode.add_argument("--out", type=Path)
    decode = sub.add_parser("decode", help="decode comma-separated decimal or binary masks")
    decode.add_argument("masks", help="comma-separated ten-bit masks")
    decode.add_argument("--out", type=Path)
    plover = sub.add_parser("plover-json", help="emit a Plover boundary payload")
    plover.add_argument("outline")
    plover.add_argument("--out", type=Path)
    codebook = sub.add_parser("codebook", help="print the fixed 32-word profile")
    codebook.add_argument("--out", type=Path)
    args = parser.parse_args()
    codec = StenoCodec()

    if args.command == "encode":
        result = {
            "outline": args.outline,
            "masks": [f"{mask:010b}" for mask in codec.encode_outline(args.outline)],
        }
    elif args.command == "decode":
        masks = tuple(_parse_mask(item) for item in args.masks.split(",") if item.strip())
        results = codec.decode_outline(masks)
        result = {
            "status": "OK" if all(item.ok for item in results) else "NACK",
            "results": [
                {
                    "status": item.status,
                    "notation": item.stroke.notation if item.stroke else None,
                    "distance": item.distance,
                    "corrected": item.corrected,
                    "observed": f"{item.observed_mask:010b}",
                    "expected": f"{item.expected_mask:010b}" if item.expected_mask is not None else None,
                }
                for item in results
            ],
        }
    elif args.command == "plover-json":
        result = codec.plover_json(args.outline)
    else:
        result = {
            "distance": codec.minimum_distance(),
            "entries": [
                {"message_id": index, "mask": f"{mask:010b}", "stroke": stroke.notation}
                for index, (mask, stroke) in enumerate(codec.codebook)
            ],
        }

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if result.get("status", "OK") == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
