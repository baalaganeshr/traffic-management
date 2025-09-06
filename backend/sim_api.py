"""
Common interface for simulation engines used in the gamified dashboard.

All engines advance in 1-second ticks and must implement the API below.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class SimulationEngine(ABC):
    """Abstract simulation engine API for 1-second stepping.

    Implementations should maintain an internal clock (seconds), queues per approach,
    current phase, and any transition timers as needed.
    """

    @abstractmethod
    def reset(self) -> Dict[str, Any]:
        """Reset the simulation and return the initial state snapshot."""

    @abstractmethod
    def step(self, action: Optional[str | int] = None) -> Dict[str, Any]:
        """Advance the simulation by 1 second and return the state snapshot.

        The returned mapping should include keys such as:
        - time: int (seconds)
        - cur_phase: int
        - t_in_phase: float
        - phases: mapping of phase id to list of approaches
        - approaches: mapping of approach name to metrics like q, last_arrival, max_wait
        - served: mapping of approach name to vehicles served in this tick
        """

    @abstractmethod
    def metrics(self) -> Dict[str, Any]:
        """Return aggregate KPIs such as avg_wait, throughput (veh/h), total_queue, etc."""

    def render_snapshot(self) -> Optional["np.ndarray"]:  # pragma: no cover - optional
        """Optional image snapshot for UI overlays (not required)."""
        return None

