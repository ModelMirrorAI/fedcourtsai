"""``run-pull``: refresh tracked dockets and detect new activity.

Deterministic — no agent required. Re-fetches the docket, writes a fresh dated
snapshot, updates ``case.yaml``'s ``last_pulled``, and reports whether the
docket changed since the last snapshot (the signal that downstream
``run-predict`` should be triggered for this case).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from ..courtlistener import CourtListenerClient
from ..paths import CasePaths
from ..schemas import TrackedCase
from ..serialize import read_model, write_raw_json, write_yaml


@dataclass
class PullResult:
    case_id: str
    changed: bool
    snapshot: Path


def _latest_snapshot(paths: CasePaths) -> Path | None:
    snap_dir = paths.record / "snapshots"
    if not snap_dir.exists():
        return None
    snaps = sorted(snap_dir.glob("*.json"))
    return snaps[-1] if snaps else None


def pull_case(
    client: CourtListenerClient,
    data_root: Path,
    court_id: str,
    docket_id: int,
) -> PullResult:
    paths = CasePaths(data_root, court_id, docket_id)
    case = read_model(paths.case_file, TrackedCase)

    docket = client.get_docket(docket_id)
    entries = client.iter_docket_entries(docket_id)
    fresh = {**docket, "docket_entries": entries}

    prior = _latest_snapshot(paths)
    changed = True
    if prior is not None:
        changed = json.loads(prior.read_text()) != fresh

    today = date.today().isoformat()
    write_raw_json(paths.snapshot(today), fresh)
    write_raw_json(paths.docket, fresh)

    case.last_pulled = datetime.now(UTC)
    write_yaml(paths.case_file, case)

    return PullResult(case_id=case.case_id, changed=changed, snapshot=paths.snapshot(today))
