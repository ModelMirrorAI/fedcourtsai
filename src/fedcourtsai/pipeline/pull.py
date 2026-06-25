"""``run-pull``: the single-docket REST helper — onboard or refresh one docket.

Deterministic — no agent required. Fetches a docket from the CourtListener REST
API, normalizes it through the shared ingestion core, and upserts the resulting
row into the unified corpus (:mod:`fedcourtsai.corpus`). It reports whether the
docket changed since the last pull — the signal that downstream ``run-predict``
should be triggered for this case.

The first pull of a docket onboards it (no prior snapshot → ``changed``);
later pulls refresh it. The normalized raw fact goes to the corpus, never to
per-case git files; the dated full-docket snapshot is retained transitionally in
git for change detection (the normalized corpus row does not capture every
docket-entry change). Both ``seed`` and ``pull`` drive this function.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .. import ids
from ..courtlistener import CourtListenerClient
from ..paths import CasePaths
from ..serialize import write_raw_json
from .ingest import from_api_docket, upsert_to_corpus


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
    corpus_db_path: Path,
    data_root: Path,
    court_id: str,
    docket_id: int,
) -> PullResult:
    paths = CasePaths(data_root, court_id, docket_id)

    docket = client.get_docket(docket_id)
    entries = client.iter_docket_entries(docket_id)
    fresh = {**docket, "docket_entries": entries}

    prior = _latest_snapshot(paths)
    changed = prior is None or json.loads(prior.read_text()) != fresh

    today = date.today().isoformat()
    write_raw_json(paths.snapshot(today), fresh)

    upsert_to_corpus(corpus_db_path, [from_api_docket(fresh)])

    return PullResult(
        case_id=ids.case_id(court_id, docket_id),
        changed=changed,
        snapshot=paths.snapshot(today),
    )
