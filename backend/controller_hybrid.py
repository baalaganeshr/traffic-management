"""
Hybrid adaptive signal controller combining gap-out extension and max-pressure selection
with a fairness guard. Typed and documented for testability.

This module exposes:
- HybridParams: dataclass of configuration parameters
- HybridController: controller that decides HOLD or SWITCH with a target phase
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Mapping, Tuple


Action = Literal["HOLD", "SWITCH"]


@dataclass(frozen=True)
class HybridParams:
    """Parameters for the hybrid controller.

    - min_green: minimum green time (s) before any switch
    - max_green: maximum green time (s) allowed before forcing a switch
    - gap: extension window (s); if arrivals continue within this gap, extend green
    - max_wait: fairness guard; if any approach exceeds this wait, prioritize its phase
    - yellow: yellow interval (s) when switching (for engines that model transitions)
    - all_red: all-red interval (s) when switching (for engines that model transitions)
    """

    min_green: int = 7
    max_green: int = 40
    gap: int = 3
    max_wait: int = 90
    yellow: int = 3
    all_red: int = 1


class HybridController:
    """Hybrid controller with gap-out + max-pressure and fairness.

    The `decide` method expects a lightweight state mapping:
    state = {
        "phases": {0: ["North","South"], 1: ["East","West"]},
        "approaches": {"North": {"q": int, "max_wait": float}, ...},
        "approaches_since_last_arrival": float,
    }
    """

    def __init__(self, params: HybridParams) -> None:
        self.p = params

    def decide(
        self,
        state: Mapping[str, object],
        current_phase: int,
        t_in_phase: float,
    ) -> Tuple[Action, int]:
        """Return (action, target_phase) based on the given state.

        If action is HOLD, target_phase equals current_phase.
        If action is SWITCH, target_phase is the desired next phase.
        """
        phases: Mapping[int, List[str]] = state["phases"]  # type: ignore[assignment]
        approaches: Mapping[str, Mapping[str, float]] = state["approaches"]  # type: ignore[assignment]
        since_last_arrival: float = float(state.get("approaches_since_last_arrival", 0.0))

        # 1) Respect minimum green
        if t_in_phase < self.p.min_green:
            return ("HOLD", current_phase)

        # 2) Gap-out: if there is still demand on current phase and recent arrivals, extend
        active = phases[current_phase]
        active_has_queue = any(approaches[a]["q"] > 0 for a in active)
        if active_has_queue and since_last_arrival < self.p.gap and t_in_phase < self.p.max_green:
            return ("HOLD", current_phase)

        # 3) Fairness: if any approach wait exceeds max_wait, switch to its phase (if different)
        overdue_phase = next(
            (
                pid
                for pid, group in phases.items()
                if any(approaches[a]["max_wait"] > self.p.max_wait for a in group)
            ),
            None,
        )
        if overdue_phase is not None and overdue_phase != current_phase:
            return ("SWITCH", overdue_phase)

        # 4) Max-pressure: choose phase with largest total queue
        pressures: Dict[int, int] = {
            pid: int(sum(approaches[a]["q"] for a in group)) for pid, group in phases.items()
        }
        target = max(pressures, key=pressures.get)
        return ("HOLD", current_phase) if target == current_phase else ("SWITCH", target)

