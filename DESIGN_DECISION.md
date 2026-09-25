# Product Design Decision — Next-Generation English Steno

**Decision:** build a clean English steno transport, not a German-native steno
system and not a continuation of the archived compass decoder.

## User-facing target

- Wacom PTH-660, continuous zero-force surface
- Ten-finger input with anonymous/ephemeral contacts
- English steno engine and English text output
- Canonical English steno outlines at the Plover boundary
- Plover owns dictionary, translation, formatting, and output
- Raw contact coordinates remain local

German steno is explicitly out of scope. There is no German-native steno
alphabet in the new product.

## Sprint record

- 50 clean-room mathematical/biomechanical/steno fragments
- 10 consolidated physical input concepts
- 10 reviewers scoring every concept on anatomy, observability, timing,
  eyes-free learnability, and implementation/safety
- 3 finalist roles selected for the product architecture
- 3 final red-team reviews of the proposed ten-contact carrier
- Legacy experiments preserved under the pre-sprint archive tag

The strongest physical candidates were static contact-set chords, a framed
low-load event ledger, and a graceful-degradation share ledger. They are not
combined into a dense or visually guided layout. The implementation chooses a
bounded static transport because it is deterministic, replayable, and directly
testable offline.

## Final transport: Simplex-10 English Steno

A ten-contact observation is decoded as a fixed affine binary `[10, 5, 4]`
codebook:

- 32 nonzero physical masks
- 32 canonical English steno stroke entries
- minimum Hamming distance: 4
- correct one arbitrary substituted contact bit
- NACK ties and all radius-two observations
- no two-error correction claim
- all-zero observation is not a valid word
- Plover `*` is the English undo stroke
- Plover `#` is the English number-bar stroke

The ten bits are assigned to the ten fingers by a fixed, documented permutation.
This permutation is a design seed, not a measured ergonomic result.

## English steno boundary

The physical codeword is not a letter. It selects one canonical stroke from a
versioned 32-stroke profile. A sequence of decoded strokes becomes an ordered
outline:

```text
ST / PH / KW / *
```

The adapter emits side-specific Plover key events, for example:

```json
{
  "v": 1,
  "type": "stroke",
  "keys": ["S-", "T-"],
  "notation": "ST"
}
```

A larger custom English Plover system can replace the 32-stroke profile without
changing the physical transport, decoder, transaction log, or replay format.
Stock Plover dictionaries are not claimed to cover this custom profile until a
separate dictionary/system integration is authored and tested.

## State machine

```text
REST
  -> FRAME_START
  -> TENTATIVE
  -> CORRECTED / NACK / COMMITTED
  -> PLOVER_OUTLINE
  -> REST
```

- REST accepts palm and resting contacts but emits no stroke.
- A complete contact mask is required before decoding.
- A one-bit correction is logged as corrected; the observed mask is retained.
- A tie or distance-two result is NACK and never rounded to a plausible stroke.
- A committed outline is append-only.
- Plover `*` reopens the last English steno correction semantics.
- Interrupted or partial frames never produce a Plover event.

## Anatomy and privacy

The design does not assume that an evdev tracking ID is an anatomical finger.
The ten-bit profile is a transport code, not an identity claim. The product
must validate reach, palm separation, bilateral posture, ring/little coupling,
fatigue, and missed contacts in a held-out hardware session before deployment.

The codebook may detect a one-bit substitution only. A multi-bit physical error
can be misdecoded; therefore the decoder must fail closed whenever its distance
gate is not satisfied, and the hardware study must measure wrong commits rather
than assuming coding distance equals user accuracy.

## Implemented vertical slice

The repository now contains:

- `nextgen/english_steno.py` — fixed codebook, stroke library, decoder,
  outline round-trip, and Plover JSON boundary
- `nextgen/cli.py` — encode, decode, codebook, and Plover payload commands
- `tests/test_nextgen_steno.py` — exhaustive distance/one-bit correction/
  two-bit NACK and outline tests
- `nextgen/README.md` — product and validation contract

The vertical slice is intentionally honest: it proves the mathematical and
Plover-boundary engine, not PTH-660 usability, dictionary coverage, WPM, or
human correction time.

## Prohibited claims

Until hardware and dictionary integration are complete, do not claim:

- standard 23-key PTH-660 ergonomics;
- complete English vocabulary coverage;
- Plover translation success;
- WPM or correction throughput;
- zero wrong commits under real contact noise;
- two-error physical correction;
- German steno or German text output.
