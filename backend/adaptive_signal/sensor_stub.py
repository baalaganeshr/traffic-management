from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

APPROACHES: tuple[str, ...] = ("North", "East", "South", "West")
DATA_DIR = Path(__file__).resolve().parents[2] / "demo" / "data"

SCENARIO_PRESETS: Dict[str, Dict[str, object]] = {
    "Morning peak": {
        "config": {
            "base_flow": {"North": 24, "South": 28, "East": 12, "West": 9},
            "variability": 0.25,
            "seed": 42,
        },
        "description": "Heavy north/south commuter surge with moderate cross traffic.",
        "recording": "morning_peak.csv",
    },
    "Evening balanced": {
        "config": {
            "base_flow": {"North": 12, "South": 14, "East": 16, "West": 17},
            "variability": 0.18,
            "seed": 21,
        },
        "description": "Post-rush steady volumes on all legs.",
        "recording": "evening_clear.csv",
    },
    "Incident eastbound": {
        "config": {
            "base_flow": {"North": 14, "South": 13, "East": 34, "West": 9},
            "variability": 0.30,
            "seed": 7,
        },
        "description": "Collision eastbound causing spill-back and queue growth.",
        "recording": "incident_east.csv",
    },
}


@dataclass(slots=True)
class SensorConfig:
    """Configuration for the synthetic sensor feed used in the demo."""

    base_flow: Dict[str, float] = field(default_factory=lambda: {
        "North": 12,
        "South": 14,
        "East": 10,
        "West": 9,
    })
    variability: float = 0.35
    seed: int | None = None

    def aligned_flow(self) -> Dict[str, float]:
        return {approach: float(self.base_flow.get(approach, 8.0)) for approach in APPROACHES}


class SyntheticSensor:
    """Produce lightweight synthetic readings for the adaptive-signal demo."""

    def __init__(self, config: SensorConfig):
        self.config = config
        self._rng = np.random.default_rng(config.seed)

    def snapshot(self, cycle_index: int) -> Dict[str, Dict[str, float]]:
        readings: Dict[str, Dict[str, float]] = {}
        base_flow = self.config.aligned_flow()
        for idx, approach in enumerate(APPROACHES):
            base = base_flow[approach]
            wave = 1 + self.config.variability * np.sin((cycle_index + idx) / 3)
            noise = self._rng.normal(scale=self.config.variability / 2)
            vehicles = max(0, int(round(base * max(0.2, wave + noise))))
            queue_estimate = max(0, vehicles - int(base * 0.8))
            readings[approach] = {
                "vehicles": vehicles,
                "queue": queue_estimate,
            }
        return readings

    def generate_cycles(self, cycles: int) -> pd.DataFrame:
        records: List[Dict[str, float]] = []
        for cycle in range(cycles):
            data = self.snapshot(cycle)
            for approach, values in data.items():
                records.append(
                    {
                        "cycle": cycle,
                        "approach": approach,
                        "vehicles": values["vehicles"],
                        "queue": values["queue"],
                    }
                )
        return pd.DataFrame(records)


def list_scenarios() -> Iterable[str]:
    return SCENARIO_PRESETS.keys()


def scenario_description(name: str) -> str:
    preset = SCENARIO_PRESETS.get(name)
    return preset.get("description", "") if preset else ""


def scenario_config(name: str) -> SensorConfig:
    preset = SCENARIO_PRESETS.get(name)
    if not preset:
        raise KeyError(f"Unknown scenario: {name}")
    config_dict = preset.get("config", {})
    return SensorConfig(**config_dict)


def load_recorded_counts(name: str) -> pd.DataFrame:
    preset = SCENARIO_PRESETS.get(name)
    if not preset:
        raise KeyError(f"Unknown scenario: {name}")
    filename = preset.get("recording")
    if not filename:
        raise FileNotFoundError(f"No recording configured for scenario '{name}'")
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Recorded data missing: {path}")
    return pd.read_csv(path)


def generate_sensor_data(config: SensorConfig, cycles: int = 12) -> pd.DataFrame:
    sensor = SyntheticSensor(config)
    return sensor.generate_cycles(cycles)
