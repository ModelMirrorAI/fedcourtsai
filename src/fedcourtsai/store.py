"""Filesystem queries over the tracked-case tree.

Used by the orchestration layer (``run-pull`` / ``run-predict`` / ``run-evaluate``)
to enumerate what exists on disk without an agent in the loop.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .paths import CasePaths


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
