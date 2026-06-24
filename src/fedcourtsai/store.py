"""Filesystem queries over the tracked-case tree and the packed corpus.

Used by the orchestration layer (``run-pull`` / ``run-predict`` / ``run-evaluate``)
to enumerate what exists on disk without an agent in the loop, and by the
ingestion core to locate and stream the packed raw-fact corpus.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from .paths import CasePaths

CORPUS_FILENAME = "corpus.jsonl"


def corpus_path(corpus_root: Path) -> Path:
    """Path to the packed raw-fact corpus under ``corpus_root``.

    One packed artifact per the *pack, don't proliferate* rule — seed and pull
    both write here through the ingestion core. The file is DVC-tracked; only a
    pointer lives in git.
    """
    return corpus_root / CORPUS_FILENAME


def iter_corpus_records(path: Path) -> Iterator[dict[str, Any]]:
    """Stream raw JSON objects from a packed corpus file (one per line).

    Schema-agnostic by design: the ingestion core validates each record against
    the corpus model, so this module stays free of any model dependency.
    """
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if stripped:
            record: dict[str, Any] = json.loads(stripped)
            yield record


def iter_tracked_cases(data_root: Path) -> list[tuple[str, int]]:
    """Return ``(court_id, docket_id)`` for every case with a ``case.yaml``."""
    cases_dir = data_root / "cases"
    found: list[tuple[str, int]] = []
    if not cases_dir.exists():
        return found
    for case_file in sorted(cases_dir.glob("*/*/case.yaml")):
        court_id = case_file.parent.parent.name
        docket_raw = case_file.parent.name
        if docket_raw.isdigit():
            found.append((court_id, int(docket_raw)))
    return found


def open_events(data_root: Path, court_id: str, docket_id: int) -> list[str]:
    """Event ids that are unresolved (``resolved: false`` and no ``outcome.json``).

    These are the events ``run-predict`` should target.
    """
    events_dir = CasePaths(data_root, court_id, docket_id).events_dir
    if not events_dir.exists():
        return []
    open_ids: list[str] = []
    for event_file in sorted(events_dir.glob("*/event.yaml")):
        data = yaml.safe_load(event_file.read_text()) or {}
        resolved = bool(data.get("resolved", False))
        outcome = event_file.parent / "outcome.json"
        if not resolved and not outcome.exists():
            open_ids.append(event_file.parent.name)
    return open_ids


def resolved_events(data_root: Path, court_id: str, docket_id: int) -> list[str]:
    """Event ids that have an ``outcome.json`` (ready for ``run-evaluate``)."""
    events_dir = CasePaths(data_root, court_id, docket_id).events_dir
    if not events_dir.exists():
        return []
    return [outcome.parent.name for outcome in sorted(events_dir.glob("*/outcome.json"))]
