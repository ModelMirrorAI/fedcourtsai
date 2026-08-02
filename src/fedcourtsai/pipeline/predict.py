"""``run-predict`` helpers.

The prediction itself is produced by a coding agent (Claude Code or Codex) from
the prompt template named in ``config/predictors.yaml``. These helpers only
resolve where the agent should write and validate what it wrote, so malformed
output fails fast in CI rather than landing in ``data/``.
"""

from __future__ import annotations

from pathlib import Path

from ..schemas import Prediction
from ..serialize import read_model


def validate_prediction(path: Path) -> Prediction:
    """Validate a prediction.json an agent produced; raises on bad data."""
    return read_model(path, Prediction)
