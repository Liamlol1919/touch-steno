# Novelty Statement — what is known, what we measured, what we claim

**Author:** Agent 2. **Date:** 2026-09-25 05:59 CEST.
**Purpose:** stop this project from overclaiming. Two worker passes (W1, W12) plus direct
source verification were used to separate *known biology* from *new measurement* from *new
method*. Everything below is a claim we are willing to defend.

## Summary

| component | status | claim we make |
|---|---|---|
| finger enslavement as a phenomenon | **known since decades** | none — Zatsiorsky/Latash, Häger-Ross & Schieber, Park et al. |
| drift/baseline compensation in capacitive touch | **known, textbook and patented** | none — slew-rate reference followers, forced re-baseline |
| resting-finger drift *magnitude in mm over time* on a touch pad | **no published number found** | we measured 11.96 mm worst case over 20 s on this hand/device |
| adaptive-baseline noise reduction for a *resting* contact | **not found** | 200 ms sliding window cuts the worst residual to 5.04 mm |
| enslavement expressed as *touch-point covariation* on a capacitive surface | **not found** | neighbouring touch points move 62–92 % in parallel with a leader |
| per-pair signed linear regression to suppress that covariation | **not found** | 175 followers suppressed at r² 0.55–0.93 in one session |
| suppressibility being a property of r² rather than the coupling sign | **our finding** | mirrored cross-hand pairs (r = −0.86) suppress as well as parallel ones |
| thumb↔thumb coupling resisting suppression (r² 0.10–0.25) | **our finding** | the one measured pair class a linear filter cannot fix |
| event rate supplied by free finger motion (2.56 events/s) | **not found** | measured; framed as a day-0 baseline, not a ceiling |
| 360 WPM human steno record | **known** (Guinness/NCRA, verified) | used as a headroom reference, not as a claim |

## The two things we must not claim

1. **"We discovered finger enslavement."** No. The biology is well established: slave forces
   up to 67.5 % of a slave finger's own MVC (Zatsiorsky et al. 2000), individuation index
   0.898–0.991 with the ring finger worst (Häger-Ross & Schieber 2000), enslaving index
   ordering I, M < L < R (Park et al. 2017). W1 retrieved all of these with exact numbers.
2. **"We invented drift compensation."** No. Baseline/drift compensation in capacitive touch
   is textbook and patented. W12 found the established literature and explicitly advises
   against a general "drift correction" claim.

## What we can claim, precisely

1. **A quantified operating point that the literature does not have.** W1 and W12 both
   searched explicitly for resting-finger drift in mm/mm-per-second on a touch surface and
   returned NOT FOUND. We measured it: per-frame step p99 = 0.56 mm, speed p99 = 57 mm/s,
   net drift 11.96 mm over 20 s. That is the bridge between the force-domain enslavement
   literature and a position-only sensor.
2. **A suppression method for the touch-signal domain, with numbers.** W12 found no
   touch-UI paper or patent that decouples neighbouring *touch points* by per-pair linear
   regression. We implemented it, measured its residual factor (0.29–0.62 for the finger row)
   and its failure case (0.87–0.95 for thumb↔thumb).
3. **A falsifiable discriminator**: the sign of the coupling does not determine
   suppressibility, r² does. The cross-hand pairs are mirrored *and* 72–74 % suppressable;
   the thumbs are mirrored *and* only 10–25 % suppressable. Any method that keys on
   "parallel vs mirrored" is wrong, and we can demonstrate it.

## Standing caveat on novelty

These are one hand, three sessions (~80 s of recorded motion), one device, and one operator.
W12's own advice applies: publish the rig and the numbers so the claims can be re-measured.
Until an independent session reproduces 11.96 mm / 5.04 mm and the r² table, these are
**measurements from one hand**, not population statistics. The documents label them that way.

## Provenance

- `W1_ACADEMIC_ENSLAVEMENT.md` — enslavement/force literature with exact values.
- `W12_DRIFT_AND_ENSLAVEMENT_PRIOR_ART.md` — prior-art search for both failure modes.
- Direct verification by agent 2: PMC6773164 (Häger-Ross & Schieber 2000), PMID 10766271
  (Zatsiorsky et al. 2000), billbuxton.com/MMExpert.html (Kurtenbach & Buxton 1993),
  nymag.com interview with the 360 WPM record holder.
