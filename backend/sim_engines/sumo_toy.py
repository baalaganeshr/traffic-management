"""
Lightweight 4-approach Poisson-arrival simulator for demo purposes.
Implements a simple 1-second tick model with two phases: NS and EW.
"""
from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
import random

try:
    # When executed as a package
    from urbanflow360.backend.sim_api import SimulationEngine  # type: ignore
except Exception:  # pragma: no cover - fallback for direct runs
    from ..sim_api import SimulationEngine  # type: ignore


class SumoToy(SimulationEngine):
    """Toy simulator with Poisson arrivals and fixed service rate."""

    approaches: List[str] = ["North", "East", "South", "West"]

    def __init__(self, demand: str = "Typical", seed: int = 42) -> None:
        random.seed(seed)
        np.random.seed(seed)
        self.phases: Dict[int, List[str]] = {0: ["North", "South"], 1: ["East", "West"]}
        base = {"Off-peak": 0.15, "Typical": 0.35, "Rush": 0.6}[demand]
        self.lam: Dict[str, float] = {
            a: max(0.05, float(np.random.normal(base, base * 0.15))) for a in self.approaches
        }
        self.yellow = 3
        self.all_red = 1
        self.transition = 0
        self.cur_phase = 0
        self.t_in_phase = 0
        self.time = 0
        self._served_hist: List[int] = []
        self._wait_hist: List[float] = []
        self._reset_state()

    def _reset_state(self) -> None:
        self.state: Dict[str, Dict[str, float]] = {
            a: {"q": 0.0, "last_arrival": 0.0, "max_wait": 0.0} for a in self.approaches
        }

    def reset(self) -> Dict[str, Any]:
        self.transition = 0
        self.cur_phase = 0
        self.t_in_phase = 0
        self.time = 0
        self._served_hist.clear()
        self._wait_hist.clear()
        self._reset_state()
        return self._snapshot()

    def _snapshot(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "cur_phase": self.cur_phase,
            "t_in_phase": float(self.t_in_phase),
            "phases": self.phases,
            "approaches": self.state,
        }

    def step(self, action: str | int | None = None) -> Dict[str, Any]:
        dt = 1
        self.time += dt
        # arrivals
        for a in self.approaches:
            arrivals = int(np.random.poisson(self.lam[a]))
            self.state[a]["q"] += arrivals
            self.state[a]["last_arrival"] = 0.0 if arrivals > 0 else self.state[a]["last_arrival"] + dt
            self.state[a]["max_wait"] = self.state[a]["max_wait"] + dt if self.state[a]["q"] > 0 else 0.0

        # serve if not in transition
        served = {a: 0 for a in self.approaches}
        if self.transition == 0:
            rate = 2  # veh/s capacity per phase, split across approaches in phase
            for a in self.phases[self.cur_phase]:
                s = min(int(self.state[a]["q"]), rate)
                self.state[a]["q"] -= s
                served[a] = s
                if self.state[a]["q"] <= 0:
                    self.state[a]["q"] = 0
                    self.state[a]["max_wait"] = 0.0
            self.t_in_phase += dt
        else:
            self.transition -= dt
            if self.transition <= 0:
                self.t_in_phase = 0

        # record metrics for throughput/wait
        self._served_hist.append(int(sum(served.values())))
        avg_wait_proxy = float(sum(v["max_wait"] for v in self.state.values())) / max(
            1, int(sum(v["q"] for v in self.state.values()))
        )
        self._wait_hist.append(avg_wait_proxy)
        return self._snapshot() | {"served": served}

    def switch_phase(self) -> Dict[str, Any]:
        self.transition = self.yellow + self.all_red
        self.cur_phase = 1 - self.cur_phase
        return self._snapshot()

    def metrics(self) -> Dict[str, Any]:
        total_queue = int(sum(int(v["q"]) for v in self.state.values()))
        avg_wait = float(sum(self._wait_hist) / max(1, len(self._wait_hist)))
        # throughput vehicles/hour scaled from per-second served history
        veh_per_sec = float(sum(self._served_hist) / max(1, len(self._served_hist)))
        throughput = int(veh_per_sec * 3600)
        return {
            "avg_wait": avg_wait,
            "throughput": throughput,
            "total_queue": total_queue,
        }
