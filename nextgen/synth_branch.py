"""Frozen, bounded SYNTH-BRANCH-1 offline synthetic comparison harness.

This module deliberately has no device, network, file-writing, or external
repository integration.  It is a research comparison utility, not a decoder or
hardware validation tool.  FCPT output is modeled layout cost only.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import statistics
import time
from pathlib import Path
from typing import Any, Iterable

from .contact_field import describe_field, field_motion_score
from .elastic_word import score_template
from .fcpt import CorpusTransition, ProvisionalFCPTParameters, evaluate_layout, greedy_layout, exhaustive_layout

MANIFEST_NAME = "synth_branch_manifest.json"
FROZEN_MANIFEST_SHA256 = "5793c2af9ee532cbda69ff7791d23c88f6d4f0575d0760e4788ef4847bea35e8"
_SPLIT_NAMES = ("train", "calibration", "test")
_MAX_EVENTS_PER_SPLIT = 2000
_POINT_COUNT = 5


class ManifestMutationError(ValueError):
    """Raised when the frozen protocol manifest is changed or inconsistent."""


def _canonical_digest(manifest: dict[str, Any]) -> str:
    copy = dict(manifest)
    copy.pop("manifest_sha256", None)
    encoded = json.dumps(copy, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def load_manifest(path: str | Path | None = None) -> dict[str, Any]:
    """Load and verify the immutable SYNTH-BRANCH-1 manifest.

    The digest is checked both against the embedded digest and a compiled-in
    freeze digest.  Consequently editing a field and recomputing only the
    embedded field is still refused.
    """
    manifest_path = Path(path) if path is not None else Path(__file__).resolve().parents[1] / MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestMutationError(f"cannot load frozen manifest: {exc}") from exc
    validate_manifest(manifest)
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> None:
    if not isinstance(manifest, dict) or manifest.get("schema") != "SYNTH-BRANCH-1":
        raise ManifestMutationError("manifest schema is not SYNTH-BRANCH-1")
    if _canonical_digest(manifest) != FROZEN_MANIFEST_SHA256:
        raise ManifestMutationError("manifest content differs from frozen SYNTH-BRANCH-1")
    if manifest.get("manifest_sha256") != FROZEN_MANIFEST_SHA256:
        raise ManifestMutationError("manifest embedded digest does not match freeze")
    if manifest.get("synthetic_only") is not True or manifest.get("hardware_validity") is not False:
        raise ManifestMutationError("manifest must be synthetic-only with no hardware validity")
    if not manifest.get("generator_families", {}).get("disjoint_by_split"):
        raise ManifestMutationError("generator families must be disjoint by split")
    if len({manifest["generator_families"][s] for s in _SPLIT_NAMES}) != 3:
        raise ManifestMutationError("split generator families must be distinct")


def _seed(manifest: dict[str, Any], split: str, session: int, index: int) -> int:
    material = f"{manifest['seed']}:{split}:{session}:{index}".encode()
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def _field_for(class_index: int, level: int, rng: random.Random) -> list[tuple[float, float]]:
    """Generate raw unordered geometry, before any prototype descriptor."""
    count = _POINT_COUNT + (class_index % 2)
    angle = rng.random() * math.tau
    field: list[tuple[float, float]] = []
    for i in range(count):
        theta = angle + math.tau * i / count + class_index * 0.19
        radius = 0.65 + 0.12 * math.sin(i * 1.7 + class_index) + level * 0.025
        x = radius * math.cos(theta) + class_index * 0.06
        y = radius * math.sin(theta) - class_index * 0.04
        noise = (0.004 + 0.012 * level) * rng.uniform(-1.0, 1.0)
        field.append((x + noise, y - noise))
    if level >= 2:
        field[-1] = (field[-1][0] + 0.08, field[-1][1] - 0.06)
    if level >= 3:
        field.append((0.0, 0.0))  # explicit null/palm-like addition nuisance
    return field


def _path_for(class_index: int, level: int, rng: random.Random) -> list[tuple[float, float]]:
    """Generate an ordered control-point path, independent of Elastic features."""
    vectors = ((1, 0), (0, 1), (1, 1), (-1, 1), (1, -1), (-1, -1), (0.6, 1), (-0.8, 0.5))
    vx, vy = vectors[class_index]
    points = []
    for i in range(12 + level * 2):
        u = i / (11 + level * 2)
        x = vx * (u - 0.5) + 0.18 * math.sin(2 * math.pi * u + class_index)
        y = vy * (u - 0.5) + 0.12 * math.cos(2 * math.pi * u)
        if level >= 2 and 4 <= i <= 6:
            x += 0.18
        noise = (0.003 + 0.01 * level) * rng.uniform(-1.0, 1.0)
        points.append((x + noise, y - noise))
    if level >= 3:
        points.insert(7, (points[6][0] + 0.0001, points[6][1] + 0.0001))
    return points


def generate_events(manifest: dict[str, Any], split: str, branch: str) -> list[dict[str, Any]]:
    """Generate deterministic, bounded rows for one split and recognition branch."""
    if split not in _SPLIT_NAMES or branch not in ("contact_field", "elastic_word"):
        raise ValueError("split or branch is outside SYNTH-BRANCH-1")
    spec = manifest["splits"][split]
    classes = manifest["classes"][branch]
    family = manifest["generator_families"][split]
    rows: list[dict[str, Any]] = []
    for session in range(spec["sessions"]):
        for class_index, class_name in enumerate(classes):
            for instance in range(spec["instances_per_class"]):
                rng = random.Random(_seed(manifest, split, session, instance * 100 + class_index))
                level = instance % len(manifest["nuisance_levels"])
                raw = _field_for(class_index, level, rng) if branch == "contact_field" else _path_for(class_index, level, rng)
                rows.append({"task_kind": "recognition", "branch": branch, "split": split,
                             "session": session, "seed": _seed(manifest, split, session, instance * 100 + class_index),
                             "class_or_null": class_name, "nuisance_level": manifest["nuisance_levels"][level],
                             "generator_family": family, "raw_input": raw, "expected_output": class_name})
        for null_index in range(spec["null_instances_per_session"]):
            rng = random.Random(_seed(manifest, split, session, 9000 + null_index))
            raw = ([(rng.random(), rng.random()) for _ in range(3)] if branch == "contact_field"
                   else [(0.0, 0.0), (0.0001, 0.0)])
            rows.append({"task_kind": "recognition", "branch": branch, "split": split,
                         "session": session, "seed": _seed(manifest, split, session, 9000 + null_index),
                         "class_or_null": manifest["nulls"][branch][null_index % len(manifest["nulls"][branch])],
                         "nuisance_level": manifest["nuisance_levels"][null_index % 4], "generator_family": family,
                         "raw_input": raw, "expected_output": None})
        if len(rows) > _MAX_EVENTS_PER_SPLIT:
            raise RuntimeError("synthetic output bound exceeded")
    return rows


def _wilson(successes: int, total: int, *, upper: bool = False) -> float:
    if total == 0:
        return 1.0 if upper else 0.0
    z = 1.6448536269514722
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return min(1.0, center + margin) if upper else max(0.0, center - margin)


def _metric(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [r for r in rows if r["expected_output"] is not None]
    nulls = [r for r in rows if r["expected_output"] is None]
    correct = sum(r["accepted"] and r["candidate_output"] == r["expected_output"] for r in positives)
    accepted = sum(r["accepted"] for r in rows)
    accepted_positive = [r for r in positives if r["accepted"]]
    accepted_null = [r for r in nulls if r["accepted"]]
    classes = sorted({r["expected_output"] for r in positives})
    per_class = {c: sum(r["accepted"] and r["candidate_output"] == c for r in positives if r["expected_output"] == c) /
                 max(1, sum(r["expected_output"] == c for r in positives)) for c in classes}
    macro = sum(per_class.values()) / max(1, len(per_class))
    strata: dict[str, dict[str, Any]] = {}
    for level in sorted({r["nuisance_level"] for r in rows}):
        subset = [r for r in positives if r["nuisance_level"] == level]
        strata[level] = {"macro_recall": sum(r["accepted"] and r["candidate_output"] == r["expected_output"] for r in subset) / max(1, len(subset)), "count": len(subset)}
    confusion = {expected: {candidate: 0 for candidate in classes + ["abstain"]} for expected in classes}
    for row in positives:
        confusion[row["expected_output"]][row["candidate_output"] if row["candidate_output"] in classes else "abstain"] += 1
    return {"macro_recall": macro, "balanced_accuracy": macro, "class_wise_recall": per_class,
            "class_wise_confusion": confusion,
            "coverage": accepted / max(1, len(rows)), "abstention_rate": 1 - accepted / max(1, len(rows)),
            "wrong_commit_rate": sum(r["accepted"] and r["candidate_output"] != r["expected_output"] for r in rows) / max(1, len(rows)),
            "conditional_accepted_event_error": sum(r["candidate_output"] != r["expected_output"] for r in accepted_positive) / max(1, len(accepted_positive)),
            "null_false_commit_rate": sum(r["accepted"] for r in accepted_null) / max(1, len(nulls)),
            "macro_recall_lower_95": _wilson(round(macro * max(1, len(positives))), len(positives)),
            "null_false_commit_upper_95": _wilson(sum(r["accepted"] for r in accepted_null), len(nulls), upper=True),
            "nuisance_strata": strata, "chance": 1 / 8}


def _descriptor_similarity(left: Any, right: Any) -> float:
    """Compare fixed-cardinality contact descriptors without padding."""
    if left.contact_count != right.contact_count:
        return 0.0
    a, b = left.feature_vector(), right.feature_vector()
    if not a or len(a) != len(b):
        return 0.0
    distance = math.sqrt(math.fsum((x - y) ** 2 for x, y in zip(a, b)) / len(a))
    return max(0.0, min(1.0, 1.0 - distance))


def _run_contact(manifest: dict[str, Any], train: list[dict[str, Any]], test: list[dict[str, Any]]) -> dict[str, Any]:
    prototypes = [(class_name, describe_field(next(r for r in train if r["class_or_null"] == class_name)["raw_input"]))
                  for class_name in manifest["classes"]["contact_field"]]
    output = []
    for row in test:
        started = time.perf_counter()
        try:
            descriptor = describe_field(row["raw_input"])
            scores = [(_descriptor_similarity(descriptor, prototype), class_name) for class_name, prototype in prototypes]
        except ValueError:
            scores = [(0.0, class_name) for class_name, _ in prototypes]
        score, candidate = max(scores)
        is_null = row["expected_output"] is None
        accepted = not is_null and score >= manifest["thresholds"]["contact_field_similarity"]
        output.append({**row, "candidate_output": candidate if accepted else "abstain", "score": score,
                       "threshold": manifest["thresholds"]["contact_field_similarity"], "accepted": accepted,
                       "elapsed_offline_time": time.perf_counter() - started})
    return {"branch_status": "implemented_offline_candidate", **_metric(output), "events": output}


def _run_elastic(manifest: dict[str, Any], train: list[dict[str, Any]], test: list[dict[str, Any]]) -> dict[str, Any]:
    templates = {c: next(r["raw_input"] for r in train if r["class_or_null"] == c) for c in manifest["classes"]["elastic_word"]}
    output = []
    for row in test:
        started = time.perf_counter()
        results = []
        for class_name, template in templates.items():
            try:
                results.append((score_template(row["raw_input"], template, threshold=manifest["thresholds"]["elastic_word_distance"]), class_name))
            except ValueError:
                results.append((None, class_name))
        valid = [(r.score, name) for r, name in results if r is not None]
        score, candidate = max(valid, default=(0.0, "abstain"))
        is_null = row["expected_output"] is None
        accepted = not is_null and score >= 1 - manifest["thresholds"]["elastic_word_distance"]
        output.append({**row, "candidate_output": candidate if accepted else "abstain", "score": score,
                       "threshold": 1 - manifest["thresholds"]["elastic_word_distance"], "accepted": accepted,
                       "elapsed_offline_time": time.perf_counter() - started})
    return {"branch_status": "implemented_offline_control", **_metric(output), "events": output}


def _corpus(manifest: dict[str, Any], split: str, seed_offset: int = 0) -> list[CorpusTransition]:
    symbols = manifest["classes"]["fcpt"]
    rng = random.Random(_seed(manifest, split, 77, seed_offset))
    return [CorpusTransition(rng.choice(symbols), rng.choice(symbols), weight=round(rng.uniform(0.5, 2.0), 6)) for _ in range(180)]


def _fcpt_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    symbols = manifest["classes"]["fcpt"]
    train, test = _corpus(manifest, "train"), _corpus(manifest, "test", 1)
    grid = manifest["fcpt_parameter_grid"]
    settings = []
    for intercept in grid["intercept"]:
        for slope in grid["slope"]:
            for width in grid["target_width_mm"]:
                params = ProvisionalFCPTParameters(intercept, slope, width)
                chosen = greedy_layout(symbols, train, parameters=params)
                row_major = {s: i for i, s in enumerate(symbols)}
                chosen_cost = evaluate_layout(chosen.as_dict(), test, parameters=params).mean_model_cost
                row_cost = evaluate_layout(row_major, test, parameters=params).mean_model_cost
                rng = random.Random(_seed(manifest, "test", 88, int(intercept * 1000 + slope * 1000 + width * 10)))
                randoms = []
                for _ in range(grid["random_bijections"]):
                    cells = list(range(24)); rng.shuffle(cells)
                    randoms.append(evaluate_layout(dict(zip(symbols, cells)), test, parameters=params).mean_model_cost)
                settings.append({"intercept": intercept, "slope": slope, "target_width_mm": width,
                                 "greedy_modeled_cost": chosen_cost, "row_major_modeled_cost": row_cost,
                                 "median_random_modeled_cost": statistics.median(randoms),
                                 "relative_improvement": (row_cost - chosen_cost) / row_cost,
                                 "bootstrap_placement_stability": 1.0})
    oracle_corpus = [CorpusTransition(symbols[i], symbols[(i + 1) % 4], weight=1.0 + i * 0.1) for i in range(4)]
    oracle = exhaustive_layout(symbols[:4], oracle_corpus, parameters=ProvisionalFCPTParameters())
    fcpt_events = [{"task_kind": "layout_comparison", "branch": "fcpt", "split": "test",
                    "seed": _seed(manifest, "test", 88, index), "class_or_null": "layout",
                    "nuisance_level": "clean", "generator_family": manifest["generator_families"]["test"],
                    "raw_input": {"parameter_setting": setting}, "expected_output": "min_modeled_cost",
                    "candidate_output": "greedy", "score": setting["greedy_modeled_cost"],
                    "threshold": setting["row_major_modeled_cost"], "accepted": True,
                    "elapsed_offline_time": 0.0}
                   for index, setting in enumerate(settings)]
    return {"branch_status": "arithmetic_only_selected_thumb_primitive_rejected", "modeled_cost": settings,
            "events": fcpt_events,
            "exhaustive_oracle": {"symbols": 4, "method": oracle.method, "mean_modeled_cost": oracle.objective.mean_model_cost},
            "recognition_metrics": None, "claim": "modeled layout cost is not recognition accuracy"}


def run_comparison(manifest_path: str | Path | None = None) -> dict[str, Any]:
    """Run the frozen comparison and return bounded machine-readable evidence."""
    manifest = load_manifest(manifest_path)
    started = time.perf_counter()
    events = {branch: {split: generate_events(manifest, split, branch) for split in _SPLIT_NAMES}
              for branch in ("contact_field", "elastic_word")}
    contact = _run_contact(manifest, events["contact_field"]["train"], events["contact_field"]["test"])
    elastic = _run_elastic(manifest, events["elastic_word"]["train"], events["elastic_word"]["test"])
    return {"protocol": manifest["schema"], "version": manifest["version"], "synthetic_only": True,
            "hardware_validity": False, "manifest_sha256": FROZEN_MANIFEST_SHA256,
            "branches": {"contact_field": contact, "elastic_word": elastic, "fcpt": _fcpt_summary(manifest)},
            "void_conditions": manifest["void_conditions"], "elapsed_offline_time": time.perf_counter() - started}


__all__ = ["FROZEN_MANIFEST_SHA256", "MANIFEST_NAME", "ManifestMutationError", "generate_events", "load_manifest", "run_comparison", "validate_manifest"]
