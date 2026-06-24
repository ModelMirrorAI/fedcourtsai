"""On-disk layout for the packed historical corpus and pipeline metrics.

The active prediction targets live as reviewable per-case files under
``data/cases/`` (see :mod:`fedcourtsai.paths`). The historical *mass* is packed
into Parquet shards under ``corpus/`` and versioned with DVC — the data blobs
live in the DVC remote, while the ``.dvc`` pointer and the seed cursor stay in
git. Aggregate metrics (back-test results, leaderboards) live under ``metrics/``
and are wired through ``dvc metrics``.

This module is the single place that knows those locations, mirroring the role
:mod:`fedcourtsai.paths` plays for the case tree. See ``docs/data-pipeline.md``.
"""

from __future__ import annotations

from pathlib import Path

from . import ids


class CorpusLayout:
    """Resolves corpus / metrics / cursor locations relative to a repo root."""

    def __init__(self, root: Path = Path(".")) -> None:
        self.root = root
        self.corpus_dir = root / "corpus"
        self.shards_dir = self.corpus_dir / "shards"
        self.metrics_dir = root / "metrics"
        # The resumable backfill cursor (config/seed-progress.yaml); committed to
        # git alongside the DVC pointer so the corpus rebuilds from a fresh clone.
        self.cursor = root / "config" / "seed-progress.yaml"

    def shard(self, court_id: str) -> Path:
        """Parquet shard for one court, e.g. ``corpus/shards/ca9.parquet``."""
        return self.shards_dir / f"{ids.slugify(court_id)}.parquet"

    def metric(self, name: str) -> Path:
        """A metrics file wired through ``dvc metrics``, e.g. ``metrics/backtest.json``."""
        return self.metrics_dir / f"{name}.json"
