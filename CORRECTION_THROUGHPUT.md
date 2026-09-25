# Correction Throughput

Issue #21 identifies the missing human input: seconds per correction. W19 found no
published measurement at the relevant event rate.

This tool summarizes a local observation log. It does not simulate corrections and does not
claim a benchmark result.

## Observation format

JSONL, one record per observed correction:

```json
{"correction_seconds": 0.42, "observation_seconds": 600}
```

`correction_seconds` is the measured repair interval. `observation_seconds` is the total
observation window; when present, the report includes corrections per minute.

```bash
python3 scripts/correction_throughput.py corrections.jsonl \
  --out correction-throughput.json
```

The report contains:

- observation count;
- median, mean and P95 seconds per correction;
- corrections per minute when observation duration is present;
- no WPM extrapolation.

## Protocol

1. Choose a fixed word list and target event rate.
2. Record the start/end of the session and every repair interval.
3. Keep the raw log local; telemetry consent does not imply upload consent.
4. Repeat across users/postures and report the distribution, not only the mean.
5. Feed the measured seconds-per-correction into the LM recovery model only as an
   explicitly labelled scenario.

The current repository contains no human correction-throughput observations.
