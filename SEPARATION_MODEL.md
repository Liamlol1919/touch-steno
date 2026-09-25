# Separation Model — the rules written down, and checked against the data

**Author:** Agent 2. **Date:** 2026-09-25 06:32 CEST.
`scripts/separation_model.py` — run with `--verify <sessions>` to reproduce the table below.

Every threshold in this project arrived as a working rule in a script. This document states
the model they belong to, so the assumptions become falsifiable instead of implicit.

## The model, in six steps

1. A contact emits one **sample** per frame: $(dx, dy, v)$ with $v = \lVert \Delta p \rVert / \Delta t$.
2. A frame is **active** for contact $a$ when $v \ge v_\text{gate}$.
3. An **event** is a run of $\ge k$ consecutive active frames (the persistence window).
4. Inside an event, the contact with the largest accumulated displacement is the **mover**.
5. A follower is **explained** when a per-pair signed fit explains at least $r^2$ of its
   displacement energy; otherwise it is a chord candidate.
6. The mover's accumulated vector gives (sector, band); the angular distance to the nearest
   sector boundary gives the geometric confidence.

## The four constants and the measurement that fixes each

| constant | value | fixed by |
|---|---:|---|
| $v_\text{gate}$ | 40 mm/s | resting speed p99 = 57.4 mm/s — the gate sits *inside* the rest distribution, which is exactly why it must be paired with $k$ |
| $k$ | 8 frames (88 ms) | resting runs reach 7 frames at 30–40 mm/s, 5 at 60 mm/s |
| $r^2$ | 0.5 | finger row 0.62–0.92, thumb pair 0.10–0.25 |
| $\sigma_\text{rest}$ | 0.56 mm (p99) | measured per-frame step of resting contacts |

Derived, at a thumb radius of 20 mm:

| quantity | value |
|---|---:|
| angular noise at p99 | **1.60°** |
| angular noise at the worst observed frame | **4.24°** |
| sector half-width (8-way) | 22.5° |
| margin at p99 / at worst frame | **20.9° / 18.3°** |

The noise is comfortably inside the sector, so a direction estimate accumulated over an event
is reliable — while a *single-frame* vote on a 4.24° noise floor is not, which is why step 4–6
accumulate rather than vote.

## The check that matters: resting runs against the window

Worst run of consecutive supra-threshold frames among resting contacts, pooled over the three
real sessions (17 contacts; the worst session is `test-zeige`, where three contacts drift for
10–12 mm):

| $v_\text{gate}$ | worst rest run | fires at $k=8$? | margin at $k=8$ |
|---:|---:|---|---:|
| 20 mm/s | 13 frames | **yes** (still fires at $k=12$) | – |
| 30 mm/s | 7 frames | no | 1 frame |
| **40 mm/s (chosen)** | **7 frames** | **no** | **1 frame** |
| 60 mm/s | 5 frames | no | 3 frames |
| 80 mm/s | 4 frames | no | 4 frames |
| 100 mm/s | 3 frames | no | 5 frames |

### The uncomfortable part, stated plainly

**The chosen operating point has a one-frame margin.** $(40\ \text{mm/s}, k=8)$ is the
*cheapest* setting that did not produce a false activation in the recorded data — it is not the
*safest* one. $(60\ \text{mm/s}, k=8)$ has three frames of margin, $(100\ \text{mm/s}, k=8)$
has five.

What follows from that:

- A resting outlier three frames longer than anything recorded would fire at the current
  setting. That is a real failure mode, not a theoretical one.
- The choice was made to minimise latency (88 ms is the floor for detection and segmentation
  together). Trading margin for latency is a defensible product decision, but it has to be a
  *decision*, and the margin has to be known — which is what this table is for.
- A per-user adaptive $v_\text{gate}$ is the obvious mitigation, and it is cheap: the rest-floor
  session (`guided_calibration.py --task noise`) measures exactly this distribution per user,
  and the matrix above shows the rule that would be applied to it.

## What this model does not cover

- **Chords.** Step 5 uses an $r^2$ threshold with a single global value; the measured structure
  (finger row vs thumb pair vs whole-body) argues for per-pair thresholds with uncertainty.
- **Calibration portability.** Tracking IDs are ephemeral, so the coupling matrix is per-session
  (issue #9) and step 5 cannot survive a restart without finger identity.
- **Rate.** Nothing in this model bounds throughput. The cycle-time arithmetic in
  `BENCHMARK_RESULTS.md` addendum 2 is unverified, and addendum 3 records that the rate axis of
  the synthetic sweep was never measured at all.
- **The resting contacts in `test-zeige` were slow drifts, not rest.** They are the worst case
  in the table and are arguably the most realistic: a hand that settles while you think.

## Reproduce

```bash
python3 scripts/separation_model.py
python3 scripts/separation_model.py --verify messung/*.jsonl
python3 scripts/separation_model.py --json --verify messung/*.jsonl
```
