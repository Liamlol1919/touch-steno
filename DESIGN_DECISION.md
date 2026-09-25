<<<<<<< HEAD
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
=======
# DESIGN DECISION — abandoning the compass, and what replaces it

**Date:** 2026-09-25, design sprint 10:00–11:00
**Method:** 12 ideation agents on distinct primitives, then 10 independent critics
scoring each shortlisted candidate on five axes (anatomy, observability, timing,
learnability, implementation risk), 50 critique passes total.

---

## 1. The result: every candidate in the old frame is dead

The existing primitive is "thumb moves in one of 8 compass directions, decoder
classifies the direction". Twelve variants were generated inside that frame and then
scored by independent critics:

| Candidate | Anatomy | Observability | Timing | Learnability | Implementation | **Total /50** | Verdict |
|---|---|---|---|---|---|---|---|
| Folded Eight (antipodal fold) | 7 | 2 | 3 | 4 | 5 | **21** | KILL |
| Folded Sixteen | 5 | 1 | 3 | 2 | 5 | **18** | KILL |
| Mirror Agreement (bimanual relation) | 3 | 1 | 1 | 2 | 4 | **11** | KILL |
| Counted Tap Chords | 6 | 2 | 3 | 4 | 5 | **20** | KILL |
| Hold Bin (dwell duration) | 8 | 2 | 2 | 3 | 5 | **20** | KILL |
| Binary Rhythm (tap timing) | 5 | 2 | 1 | 3 | 5 | **16** | KILL |
| Letter Silhouette 8 | 2 | 1 | 2 | 1 | 4 | **10** | KILL |
| Length Gate (4/10 mm) | 5 | 2 | 2 | 3 | 4 | **16** | KILL |

**Zero candidates reached 25/50.** The frame is not badly tuned; it is wrong.

### Why, in four lines

1. **Bimanual arithmetic kills it before any measurement.** Two thumbs at 47.6 % each
   give 0.476² = **22.7 %** of jointly valid frames → **1.3 events/s**, not the 3–4 that
   was assumed. Reaching 3 valid events/s would need 13.3 joint attempts/s, more than the
   entire 5.7/s ceiling.
2. **Timing channels have no error budget.** Binary rhythm needs 44 ms precision on a
   single 88 ms slot. Hold Bin needs a release boundary nobody has measured. A timing error
   produces a **valid but wrong** symbol, which is the worst failure mode: it corrupts
   silently.
3. **Drawing is not pointing.** Letter and digit silhouettes convert a weak directional
   task into a construction task — the thumb must plan closure, turns and scale without
   visual feedback. A/O do not close; E/A need retracing that gets segmented as new events.
4. **Folding buys immunity by destroying information.** Folding antipodal pairs neutralises
   the measured 180° error, but 3 bits at 2 strokes/s is *exactly* 2 bits at 3 strokes/s.
   It halves the physical rate for zero nominal bit-rate gain, and the 16-way version puts
   adjacent sector centres 2.36 mm apart against a 0.4 mm jitter median that is **not** a
   decision-error bound.

**Decision: the direction-quantisation frame is closed.** No tuning of radius, sector count
or fold will revive it.

---

## 2. What the evidence says a survivor must change

Two independent things must change: **the symbol unit** or **the signal**.

### 2.1 The signal: the pad is reporting more than we record

Verified against the device: the finger device exposes `ABS_MT_TOUCH_MAJOR`,
`ABS_MT_TOUCH_MINOR` (both 0–31 at 0.5 mm units) and `ABS_MT_ORIENTATION`. It does
**not** expose `ABS_MT_PRESSURE`.

The recorder currently stores **x, y and major only**. The minor axis and orientation are
discarded. Consequences:

- The full contact ellipse is available and unused. Its derived area
  `A = π · major · minor / 4` is **invariant to an in-place roll**, because a 90° rotation
  swaps the axes and leaves their product unchanged. It is therefore the one obvious
  channel that is **structurally immune** to the 180° direction error that killed every
  compass variant.
- It is a posture/load proxy, not force. A small movement and a firm press can overlap.
  The claim "a brief distal curl enlarges the contact ellipse" is **hypothesis, unmeasured**.
- No new code is required: the events already arrive, the parser simply drops them.

### 2.2 The symbol unit: the event must be bigger than a letter

At the measured ceiling, one certified event costs 88 ms detection + 88 ms segmentation
= 176 ms, so **5.7 events/s is absolute**. A 5-letter word at 1–2 strokes/word means the
decoder must turn 1–2 events into a whole word. Every candidate above that insisted one
event = one direction class instead let the arithmetic work against it.

The information statement is exact: for a lexicon of `V` words, one event must carry
`log2(V)` bits. For a 20k lexicon that is **14.3 bits per event** — which is only reachable
with top-3 candidates plus a lexicon constraint, and *cannot* be reached by 4 classes
(2 bits) or 8 classes (3 bits) at any event rate the hand can sustain.

---

## 2.3 The channel-capacity argument (the quantitative core)

One certified event is 176 ms. At 224 contact reports/s that is **~39 samples**.

**What the compass extracts:** one direction class, 3 bits ideal. With the measured 47.6 %
correct and all errors landing on the exact opposite, the effective mutual information is

    I_eff = 3 − H2(0.476) = 3 − 0.999 = **2.00 bits per event**

**What the trajectory actually contains.** For a 2-D Gaussian position channel with
per-axis sigma = 0.4 mm and quantiser step Δ, the capacity per sample is

    C ≈ log2(1 + 1.92/Δ²)   bits/sample

| Δ | bits/sample | bits per 176 ms event |
|---|---|---|
| 0.4 mm | 3.70 | **~146** |
| 0.8 mm | 2.00 | ~79 |

**The compass discards roughly 70× of the information present in the signal it already
receives.** That is the quantitative statement of why every direction-classification
variant failed: the frame is not capacity-limited, it is capacity-*destroying*.

Two honest caveats on this calculation:
- A 0.4 mm **median** jitter is not a standard deviation, and the 1.92 factor assumes a
  Gaussian. The absolute numbers are indicative; the ORDER of magnitude gap is not.
- Channel capacity is not usable information. It is an upper bound that assumes an
  optimal decoder over noise-free semantics. Exploiting it requires a recogniser, which
  does not exist yet. This is the project's central engineering bet, not a result.

## 3. The concept that survives to build

**WORKING CONCEPT — "one stroke, one word, no event is a valid answer"**

- **Primitive:** the thumb makes one continuous pen-down → pen-up gesture in its natural
  region. The gesture is not classified as a direction, a letter or a digit. It is
  classified as a **whole word** by a lexicon-constrained recogniser.
- **Encoding:** one event → one word. The decoder holds the full 224 Hz trajectory,
  normalises translation, scale, slant and speed, and ranks the entire lexicon at lift-off.
  `log2(20000) = 14.3` bits are needed; the lexicon supplies the compression, the gesture
  supplies the index.
- **State machine:** pending trajectory only. No cross-event state, no segmentation between
  letters, no chord table. The event boundary is lift-off, which is unambiguous.
- **The critical design decision:** **there is a "no word" outcome, and it is a first-class
  result.** Below a confidence floor the decoder emits nothing and the user does not
  advance. This is the direct consequence of the 10-minute kill test below: a recogniser
  that cannot choose reliably will produce a *confident wrong word*, which is strictly worse
  than producing nothing.
- **Second channel, orthogonal:** contact ellipse area as a deliberate modifier — not a
  symbol, but a state. Small area = "I am about to draw"; large area = "I am correcting".
  This is untested and is listed as such.

### Why this is not the compass

The compass asks *where did the finger go* — a question this hand answers at 47.6 %. This
concept asks *what was the gesture* — a question the recogniser answers from a 224 Hz
trajectory over hundreds of samples rather than from one endpoint. The failure modes are
different in kind: a bad compass reading produces a wrong direction, a bad recognition
produces a rejected word, and rejection is recoverable because nothing was committed.

### The three earliest killing tests

1. **First-pass recognition, no feedback, no retry.** 30 uncued common words drawn in one
   pen-down. **Kill if more than 2 words are wrong, or if the user pauses or backtracks to
   define letter boundaries.** Pausing to segment letters is the signature failure: it
   means the recogniser is not doing the work.
2. **Resting-hand observability.** Repeat 8 × 10 with the other fingers and palm resting.
   **Kill if more than 5 % of strokes lose usable trajectory continuity.**
3. **Ellipse separability, 10 minutes, offline replay.** 3 min resting, 4 min of 20
   curl/release repetitions, 3 min replay with a median/MAD threshold. **Kill the ellipse
   channel if fewer than 18/20 repetitions cross the same hysteresis band, or if resting
   frames repeatedly cross it.**

---

## 4. Residual risks, stated plainly

1. **This concept is inherited from an agent proposal that was never measured.** No word
   has been drawn and recognised yet. The recogniser does not exist. The confidence floor
   does not exist.
2. **The 0.4 mm jitter is motor variation, not sensor noise**, and it is 3.3 % of a 12 mm
   gesture. It hurts tight loops, crossings and short letter strokes. Averaging over
   hundreds of samples stabilises the path but cannot repair a malformed stroke.
3. **Human writing time is the unknown that dominates.** 5.7 whole-word events/s is an
   addressability ceiling, not a typing rate. Nobody has measured how fast this user draws
   a word in one stroke, and that number decides whether the concept lives.
4. **The ellipse channel is a hypothesis about a device feature the recorder discards.**
   It is cheap to test and currently unmeasured.
5. **The bimanual and syllable/chord-algebra directions were still under evaluation when the
   deadline hit.** Those ten agents were not evaluated in time. They may beat this concept,
   and the chord-algebra route in particular has a stronger theoretical claim to density
   than anything in the table above.

---

## 5. What is explicitly not decided

- No WPM figure is claimed. None has been measured.
- No seconds-per-correction is claimed. It does not exist in the literature and was not
  measured here.
- No Plover integration exists. The path to text is a lexicon decoder, not Plover.
- The 47.6 % figure is one person, one session, one thumb, n = 63, with no error bars.
>>>>>>> fca1cd6 (Design decision: the direction-quantisation frame is closed, and what replaces it)
