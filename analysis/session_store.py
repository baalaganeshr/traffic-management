"""
SessionStore for appending per-run metrics to a persistent CSV and exporting
timestamped session logs for download from the UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Mapping
import os
import time
import pandas as pd


@dataclass
class SessionStore:
    """Persist and export session logs.

    - path: main CSV file for cumulative logs (append-only)
    """

    path: str = "logs/sessions.csv"

    def __post_init__(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def append(self, rows: Iterable[Mapping[str, object]]) -> pd.DataFrame:
        """Append rows to the session log CSV and return the concatenated DataFrame."""
        df = pd.DataFrame(list(rows))
        if os.path.exists(self.path):
            df_prev = pd.read_csv(self.path)
            df = pd.concat([df_prev, df], ignore_index=True)
        df.to_csv(self.path, index=False)
        return df

    def export_timestamped(self, df: pd.DataFrame | None = None) -> str:
        """Export a timestamped CSV file and return its filepath.

        If df is None, export the current cumulative file contents.
        """
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_path = f"logs/sessions_{ts}.csv"
        if df is None:
            if os.path.exists(self.path):
                df = pd.read_csv(self.path)
            else:
                df = pd.DataFrame()
        df.to_csv(out_path, index=False)
        return out_path

