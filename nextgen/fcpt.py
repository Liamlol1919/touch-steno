"""Bounded offline FCPT target-layout arithmetic.

This module is a research prototype for assigning a small symbol table to a
fixed 6-by-4 array using a corpus-weighted Fitts-style objective. It performs
no device I/O and contains no fitted ergonomic parameters. Coordinates are
model-space design values; outputs are model scores, not hardware or human
performance measurements.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import permutations
from math import hypot, isfinite, log2
from typing import Literal, Mapping, Sequence


GRID_COLUMNS = 6
GRID_ROWS = 4
CELL_COUNT = GRID_COLUMNS * GRID_ROWS
CELL_PITCH_MM = 4.0
ENVELOPE_WIDTH_MM = 24.6
ENVELOPE_HEIGHT_MM = 18.2
MAX_EXHAUSTIVE_SYMBOLS = 4
ASSUMPTION_ONLY = (
    "ASSUMPTION ONLY: coefficients are provisional arithmetic defaults, not "
    "fitted ergonomic measurements."
)

AssignmentMethod = Literal["exhaustive", "greedy"]


def _finite_number(value: float, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class TargetCell:
    """One bounded, immutable point in the model-space target array."""

    cell_id: int
    x_mm: float
    y_mm: float

    def __post_init__(self) -> None:
        if isinstance(self.cell_id, bool) or not isinstance(self.cell_id, int):
            raise TypeError("cell_id must be an integer")
        if not 0 <= self.cell_id < CELL_COUNT:
            raise ValueError(f"cell_id must be in [0, {CELL_COUNT})")
        x = _finite_number(self.x_mm, "x_mm")
        y = _finite_number(self.y_mm, "y_mm")
        if not 0.0 <= x <= ENVELOPE_WIDTH_MM:
            raise ValueError("x_mm is outside the model envelope")
        if not 0.0 <= y <= ENVELOPE_HEIGHT_MM:
            raise ValueError("y_mm is outside the model envelope")
        object.__setattr__(self, "x_mm", x)
        object.__setattr__(self, "y_mm", y)


def build_target_geometry() -> tuple[TargetCell, ...]:
    """Return the deterministic 24-cell model geometry in row-major order."""

    first_x = (ENVELOPE_WIDTH_MM - (GRID_COLUMNS - 1) * CELL_PITCH_MM) / 2.0
    first_y = (ENVELOPE_HEIGHT_MM - (GRID_ROWS - 1) * CELL_PITCH_MM) / 2.0
    cells: list[TargetCell] = []
    for row in range(GRID_ROWS):
        for column in range(GRID_COLUMNS):
            cells.append(TargetCell(
                cell_id=row * GRID_COLUMNS + column,
                x_mm=first_x + column * CELL_PITCH_MM,
                y_mm=first_y + row * CELL_PITCH_MM,
            ))
    return tuple(cells)

TARGET_GEOMETRY: tuple[TargetCell, ...] = build_target_geometry()
_CELLS_BY_ID = {cell.cell_id: cell for cell in TARGET_GEOMETRY}


@dataclass(frozen=True)
class ProvisionalFCPTParameters:
    """Assumption-only inputs to the Shannon-form Fitts-style model.

    The defaults reproduce the project's provisional arithmetic. They are not
    measurements, and a future empirical fit must supply a different explicit
    object rather than silently changing these values.
    """

    intercept: float = 0.150
    slope: float = 0.120
    target_width_mm: float = 3.0
    assumption_only: bool = field(default=True, init=False)

    def __post_init__(self) -> None:
        intercept = _finite_number(self.intercept, "intercept")
        slope = _finite_number(self.slope, "slope")
        width = _finite_number(self.target_width_mm, "target_width_mm")
        if intercept < 0.0:
            raise ValueError("intercept must be non-negative")
        if slope <= 0.0:
            raise ValueError("slope must be positive")
        if width <= 0.0:
            raise ValueError("target_width_mm must be positive")
        object.__setattr__(self, "intercept", intercept)
        object.__setattr__(self, "slope", slope)
        object.__setattr__(self, "target_width_mm", width)

    @property
    def assumption_note(self) -> str:
        return ASSUMPTION_ONLY


DEFAULT_PARAMETERS = ProvisionalFCPTParameters()


@dataclass(frozen=True)
class CorpusTransition:
    """One observed source-to-destination corpus transition."""

    source: str
    symbol: str
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source:
            raise ValueError("source must be a non-empty string")
        if not isinstance(self.symbol, str) or not self.symbol:
            raise ValueError("symbol must be a non-empty string")
        weight = _finite_number(self.weight, "weight")
        if weight <= 0.0:
            raise ValueError("weight must be positive")
        object.__setattr__(self, "weight", weight)


@dataclass(frozen=True)
class CostObjective:
    """Finite arithmetic summary of one candidate layout."""

    mean_model_cost: float
    total_weighted_cost: float
    total_weight: float
    transition_count: int
    assumption_only: bool = field(default=True, init=False)


@dataclass(frozen=True)
class LayoutAssignment:
    """A symbol-to-cell bijection and its corpus-weighted objective."""

    method: AssignmentMethod
    placements: tuple[tuple[str, int], ...]
    objective: CostObjective

    def as_dict(self) -> dict[str, int]:
        """Return a fresh mutable symbol-to-cell mapping."""

        return dict(self.placements)

    def validate(self) -> None:
        if self.method not in ("exhaustive", "greedy"):
            raise ValueError("assignment method is unknown")
        symbols = [symbol for symbol, _ in self.placements]
        cell_ids = [cell_id for _, cell_id in self.placements]
        if not symbols or len(symbols) > CELL_COUNT:
            raise ValueError("an assignment must contain 1 to 24 symbols")
        if len(set(symbols)) != len(symbols):
            raise ValueError("an assignment cannot contain a symbol twice")
        if len(set(cell_ids)) != len(cell_ids):
            raise ValueError("assigned cells must be unique")
        if any(cell_id not in _CELLS_BY_ID for cell_id in cell_ids):
            raise ValueError("assignment contains an unknown cell")


def _ordered_symbols(symbols: Sequence[str]) -> tuple[str, ...]:
    if isinstance(symbols, (str, bytes)):
        raise TypeError("symbols must be a sequence of names, not text")
    ordered = tuple(symbols)
    if not 1 <= len(ordered) <= CELL_COUNT:
        raise ValueError(f"symbols must contain 1 to {CELL_COUNT} entries")
    if any(not isinstance(symbol, str) or not symbol for symbol in ordered):
        raise ValueError("every symbol must be a non-empty string")
    if len(set(ordered)) != len(ordered):
        raise ValueError("symbols must be unique")
    return tuple(sorted(ordered))


def _validated_corpus(
    corpus: Sequence[CorpusTransition],
    symbols: tuple[str, ...],
) -> tuple[CorpusTransition, ...]:
    if isinstance(corpus, (str, bytes)):
        raise TypeError("corpus must be a sequence of CorpusTransition values")
    transitions = tuple(corpus)
    if not transitions:
        raise ValueError("corpus must contain at least one transition")
    known = set(symbols)
    for transition in transitions:
        if not isinstance(transition, CorpusTransition):
            raise TypeError("every corpus entry must be a CorpusTransition")
        if transition.source not in known or transition.symbol not in known:
            raise ValueError("corpus transitions must reference declared symbols")
    return transitions


def _validated_parameters(
    parameters: ProvisionalFCPTParameters,
) -> ProvisionalFCPTParameters:
    if not isinstance(parameters, ProvisionalFCPTParameters):
        raise TypeError("parameters must be ProvisionalFCPTParameters")
    return parameters


def _validated_placements(
    placements: Mapping[str, int],
    symbols: tuple[str, ...],
) -> dict[str, int]:
    if set(placements) != set(symbols):
        raise ValueError("layout keys must exactly match the symbol table")
    values: list[int] = []
    for cell_id in placements.values():
        if isinstance(cell_id, bool) or not isinstance(cell_id, int):
            raise TypeError("assigned cell ids must be integers")
        if cell_id not in _CELLS_BY_ID:
            raise ValueError("layout contains an unknown cell id")
        values.append(cell_id)
    if len(set(values)) != len(values):
        raise ValueError("layout must assign each cell at most once")
    return dict(placements)


def _movement_cost(
    source: TargetCell,
    destination: TargetCell,
    parameters: ProvisionalFCPTParameters,
) -> float:
    distance = hypot(
        destination.x_mm - source.x_mm,
        destination.y_mm - source.y_mm,
    )
    cost = parameters.intercept + parameters.slope * log2(
        1.0 + distance / parameters.target_width_mm,
    )
    if not isfinite(cost):
        raise ArithmeticError("FCPT movement cost is not finite")
    return cost


def _partial_objective(
    placements: Mapping[str, int],
    corpus: Sequence[CorpusTransition],
    parameters: ProvisionalFCPTParameters,
) -> float:
    weighted_cost = 0.0
    for transition in corpus:
        if transition.source not in placements or transition.symbol not in placements:
            continue
        source = _CELLS_BY_ID[placements[transition.source]]
        destination = _CELLS_BY_ID[placements[transition.symbol]]
        weighted_cost += transition.weight * _movement_cost(
            source,
            destination,
            parameters,
        )
    if not isfinite(weighted_cost):
        raise ArithmeticError("FCPT corpus cost is not finite")
    return weighted_cost


def evaluate_layout(
    placements: Mapping[str, int],
    corpus: Sequence[CorpusTransition],
    *,
    parameters: ProvisionalFCPTParameters = DEFAULT_PARAMETERS,
) -> CostObjective:
    """Evaluate the corpus-weighted model cost of a complete assignment."""

    parameters = _validated_parameters(parameters)
    symbols = _ordered_symbols(tuple(placements))
    ordered_placements = _validated_placements(placements, symbols)
    transitions = _validated_corpus(corpus, symbols)
    corpus_symbols = {
        name
        for transition in transitions
        for name in (transition.source, transition.symbol)
    }
    if corpus_symbols != set(symbols):
        raise ValueError("layout keys must exactly match the corpus symbol inventory")
    weighted_cost = _partial_objective(ordered_placements, transitions, parameters)
    total_weight = sum(transition.weight for transition in transitions)
    if not isfinite(total_weight):
        raise ArithmeticError("FCPT corpus weight is not finite")
    mean_cost = weighted_cost / total_weight
    if not isfinite(weighted_cost) or not isfinite(mean_cost):
        raise ArithmeticError("FCPT objective is not finite")
    return CostObjective(
        mean_model_cost=mean_cost,
        total_weighted_cost=weighted_cost,
        total_weight=total_weight,
        transition_count=len(transitions),
    )


def _result(
    method: AssignmentMethod,
    placements: Mapping[str, int],
    corpus: Sequence[CorpusTransition],
    parameters: ProvisionalFCPTParameters,
) -> LayoutAssignment:
    result = LayoutAssignment(
        method=method,
        placements=tuple(sorted(placements.items())),
        objective=evaluate_layout(placements, corpus, parameters=parameters),
    )
    result.validate()
    return result


def exhaustive_layout(
    symbols: Sequence[str],
    corpus: Sequence[CorpusTransition],
    *,
    parameters: ProvisionalFCPTParameters = DEFAULT_PARAMETERS,
) -> LayoutAssignment:
    """Find the minimum-cost bijection for a deliberately small table."""

    ordered_symbols = _ordered_symbols(symbols)
    parameters = _validated_parameters(parameters)
    if len(ordered_symbols) > MAX_EXHAUSTIVE_SYMBOLS:
        raise ValueError(
            f"exhaustive search is bounded to {MAX_EXHAUSTIVE_SYMBOLS} symbols"
        )
    transitions = _validated_corpus(corpus, ordered_symbols)
    best: dict[str, int] | None = None
    best_cost = float("inf")
    for cell_ids in permutations(range(CELL_COUNT), len(ordered_symbols)):
        candidate = dict(zip(ordered_symbols, cell_ids, strict=True))
        candidate_cost = _partial_objective(candidate, transitions, parameters)
        if candidate_cost < best_cost:
            best = candidate
            best_cost = candidate_cost
    if best is None:
        raise RuntimeError("exhaustive search produced no assignment")
    return _result("exhaustive", best, transitions, parameters)


def greedy_layout(
    symbols: Sequence[str],
    corpus: Sequence[CorpusTransition],
    *,
    parameters: ProvisionalFCPTParameters = DEFAULT_PARAMETERS,
) -> LayoutAssignment:
    """Build a deterministic minimum-partial-cost assignment one cell at a time."""

    ordered_symbols = _ordered_symbols(symbols)
    parameters = _validated_parameters(parameters)
    transitions = _validated_corpus(corpus, ordered_symbols)
    placements: dict[str, int] = {}
    used_cells: set[int] = set()
    while len(placements) < len(ordered_symbols):
        best_pair: tuple[str, int] | None = None
        best_cost = float("inf")
        for symbol in ordered_symbols:
            if symbol in placements:
                continue
            for cell_id in range(CELL_COUNT):
                if cell_id in used_cells:
                    continue
                candidate = {**placements, symbol: cell_id}
                candidate_cost = _partial_objective(candidate, transitions, parameters)
                if candidate_cost < best_cost:
                    best_pair = (symbol, cell_id)
                    best_cost = candidate_cost
        if best_pair is None:
            raise RuntimeError("greedy search ran out of available cells")
        symbol, cell_id = best_pair
        placements[symbol] = cell_id
        used_cells.add(cell_id)
    return _result("greedy", placements, transitions, parameters)


def optimize_layout(
    symbols: Sequence[str],
    corpus: Sequence[CorpusTransition],
    *,
    method: AssignmentMethod = "greedy",
    parameters: ProvisionalFCPTParameters = DEFAULT_PARAMETERS,
) -> LayoutAssignment:
    """Dispatch to the bounded exhaustive or deterministic greedy search."""

    if method == "exhaustive":
        return exhaustive_layout(symbols, corpus, parameters=parameters)
    if method == "greedy":
        return greedy_layout(symbols, corpus, parameters=parameters)
    raise ValueError("method must be 'exhaustive' or 'greedy'")


__all__ = [
    "ASSUMPTION_ONLY",
    "CELL_COUNT",
    "CELL_PITCH_MM",
    "DEFAULT_PARAMETERS",
    "ENVELOPE_HEIGHT_MM",
    "ENVELOPE_WIDTH_MM",
    "GRID_COLUMNS",
    "GRID_ROWS",
    "MAX_EXHAUSTIVE_SYMBOLS",
    "TARGET_GEOMETRY",
    "AssignmentMethod",
    "CorpusTransition",
    "CostObjective",
    "LayoutAssignment",
    "ProvisionalFCPTParameters",
    "TargetCell",
    "build_target_geometry",
    "evaluate_layout",
    "exhaustive_layout",
    "greedy_layout",
    "optimize_layout",
]
