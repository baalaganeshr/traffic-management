from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable

import pandas as pd

APPROACH_GROUPS = {
    "NS": ("North", "South"),
    "EW": ("East", "West"),
}


@dataclass(slots=True)
class ControllerConfig:
    cycle_length: float = 80.0
    min_green: float = 12.0
    max_green: float = 55.0
    baseline_green: float = 40.0
    responsiveness: float = 0.6  # how aggressively we bias towards heavier demand


@dataclass(slots=True)
class PhasePlan:
    ns_green: float
    ew_green: float
    reason: str
    predicted_delay_reduction: float


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def compute_phase_plan(counts: Dict[str, float], queues: Dict[str, float], config: ControllerConfig | None = None) -> PhasePlan:
    config = config or ControllerConfig()
    ns_demand = sum(counts.get(axis, 0.0) for axis in APPROACH_GROUPS["NS"]) + sum(
        0.5 * queues.get(axis, 0.0) for axis in APPROACH_GROUPS["NS"]
    )
    ew_demand = sum(counts.get(axis, 0.0) for axis in APPROACH_GROUPS["EW"]) + sum(
        0.5 * queues.get(axis, 0.0) for axis in APPROACH_GROUPS["EW"]
    )
    total_demand = ns_demand + ew_demand

    if total_demand == 0:
        return PhasePlan(
            ns_green=config.baseline_green,
            ew_green=config.baseline_green,
            reason="No demand detected; keeping baseline split.",
            predicted_delay_reduction=0.0,
        )

    ns_ratio = ns_demand / total_demand
    ns_green = _clamp(
        config.cycle_length * (config.responsiveness * ns_ratio + (1 - config.responsiveness) * 0.5),
        config.min_green,
        config.max_green,
    )
    ew_green = config.cycle_length - ns_green
    if ew_green < config.min_green:
        adjustment = config.min_green - ew_green
        ew_green += adjustment
        ns_green = max(config.min_green, ns_green - adjustment)

    # Estimate improvement over baseline fixed split (40/40)
    baseline_delay = _estimate_delay(ns_demand, config.baseline_green, config.cycle_length) + _estimate_delay(
        ew_demand, config.baseline_green, config.cycle_length
    )
    adaptive_delay = _estimate_delay(ns_demand, ns_green, config.cycle_length) + _estimate_delay(
        ew_demand, ew_green, config.cycle_length
    )
    reduction_pct = 0.0
    if baseline_delay > 0:
        reduction_pct = max(0.0, (baseline_delay - adaptive_delay) / baseline_delay * 100)

    reason = (
        f"NS demand {int(ns_demand)} vs EW {int(ew_demand)} -> {ns_green:.0f}s/{ew_green:.0f}s split"
    )
    return PhasePlan(ns_green=ns_green, ew_green=ew_green, reason=reason, predicted_delay_reduction=reduction_pct)


def _estimate_delay(demand: float, green: float, cycle_length: float) -> float:
    if demand == 0:
        return 0.0
    green_ratio = green / cycle_length
    # simplified delay proxy: vehicles experiencing red proportionally to (1 - green_ratio)
    return demand * max(0.0, 1 - green_ratio) * cycle_length / 2


def evaluate_sequence(df: pd.DataFrame, config: ControllerConfig | None = None) -> pd.DataFrame:
    config = config or ControllerConfig()
    grouped = df.groupby("cycle")
    results = []
    for cycle, group in grouped:
        counts = group.set_index("approach")["vehicles"].to_dict()
        queues = group.set_index("approach")["queue"].to_dict()
        plan = compute_phase_plan(counts, queues, config=config)
        results.append(
            {
                "cycle": cycle,
                "ns_green": plan.ns_green,
                "ew_green": plan.ew_green,
                "reason": plan.reason,
                "predicted_delay_reduction_pct": plan.predicted_delay_reduction,
            }
        )
    return pd.DataFrame(results)
