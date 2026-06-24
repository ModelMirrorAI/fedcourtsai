"""``run-predict`` helpers.

The prediction itself is produced by a coding agent (Claude Code or Codex) from
the prompt template named in ``config/predictors.yaml``. These helpers only
resolve where the agent should write and validate what it wrote, so malformed
output fails fast in CI rather than landing in ``data/``.
"""

from __future__ import annotations

from pathlib import Path

from ..paths import CasePaths
from ..schemas import Prediction
from ..serialize import read_model


def prediction_targets(
    data_root: Path,
    court_id: str,
    docket_id: int,
    event_id: str,
    predictor_id: str,
    run_id: str,
) -> tuple[Path, Path]:
    """Return ``(prediction.json, reasoning.md)`` paths an agent should write."""
    event = CasePaths(data_root, court_id, docket_id).event(event_id)
    return (
        event.prediction(predictor_id, run_id),
        event.reasoning(predictor_id, run_id),
    )


def validate_prediction(path: Path) -> Prediction:
    """Validate a prediction.json an agent produced; raises on bad data."""
    return read_model(path, Prediction)
