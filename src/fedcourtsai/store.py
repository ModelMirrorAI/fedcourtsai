"""Filesystem queries over the packed corpus and the derived-ledger tree.

Used by the orchestration layer (``run-pull`` / ``run-predict`` / ``run-evaluate``)
to enumerate what exists — which dockets the corpus tracks, which events are open
or resolved in the git ledger — without an agent in the loop.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from . import corpus
from .paths import CasePaths


def iter_tracked_cases(corpus_db_path: Path) -> list[tuple[str, int]]:
    """Return ``(court_id, docket_id)`` for every case in the packed corpus.

    The corpus is the set of tracked dockets — a case enters it the first time
    ``pull`` ingests its docket. Returns nothing if the corpus does not exist
    yet (rather than creating an empty one as a side effect of reading).
    """
    if not corpus_db_path.exists():
        return []
    found: list[tuple[str, int]] = []
    with corpus.connect(corpus_db_path) as conn:
        for row in corpus.iter_rows(conn):
            court_id, _, docket_raw = row.case_id.partition("/")
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
