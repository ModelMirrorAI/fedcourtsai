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
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .. import ids
from ..courtlistener import CourtListenerClient
from ..paths import CasePaths
from ..serialize import write_raw_json
from ..store import open_events
from .ingest import from_api_docket, upsert_to_corpus
from .outcome import ReconcileRequest, resolve_case


@dataclass
class PullResult:
    case_id: str
    changed: bool
    snapshot: Path
    # Outcome detection (`pull`'s third job): events resolved deterministically
    # this refresh, and those that appear decided but need an agent to reconcile.
    resolved: list[str]
    reconcile: list[ReconcileRequest]


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

    today = date.today()
    write_raw_json(paths.snapshot(today.isoformat()), fresh)

    row = from_api_docket(fresh)
    # Stamp the corpus tracking state so the budget governor can rotate this case
    # to the back of the oldest-`last_pulled`-first queue on the next run.
    upsert_to_corpus(corpus_db_path, [row], last_pulled=today)

    # Detect resolution of any open events: write outcome.json deterministically
    # when the disposition is machine-readable, else flag for agent reconcile.
    resolution = resolve_case(data_root, row, court_id, docket_id)

    return PullResult(
        case_id=ids.case_id(court_id, docket_id),
        changed=changed,
        snapshot=paths.snapshot(today.isoformat()),
        resolved=sorted(resolution.outcomes),
        reconcile=list(resolution.reconciles),
    )


@dataclass
class PullQueues:
    """The three downstream handoffs a ``pull-all`` run produces.

    Each entry is a JSON-serializable mapping shaped exactly as the ``run-pull``
    workflow consumes it (the ``jq`` fields in ``run-pull.yml``): ``predict`` and
    ``evaluate`` entries carry ``court`` / ``docket`` / ``events``; ``reconcile``
    adds the agent-facing ``reason``.
    """

    predict: list[dict[str, object]] = field(default_factory=list)
    evaluate: list[dict[str, object]] = field(default_factory=list)
    reconcile: list[dict[str, object]] = field(default_factory=list)


def pull_cases(
    client: CourtListenerClient,
    corpus_db_path: Path,
    data_root: Path,
    due: Iterable[tuple[str, int]],
) -> PullQueues:
    """Refresh each due case and sort it into the predict / evaluate / reconcile queues.

    The per-case half of ``pull-all``: for every ``(court, docket)`` the rotation
    governor selected, refresh the docket (:func:`pull_case`, which also detects
    resolution), then route the result — a *changed* case with open events to
    ``predict``, a case that gained an ``outcome.json`` this run to ``evaluate``,
    and a case that appears decided but could not be recorded deterministically to
    ``reconcile``. Case selection (discovery + rotation) stays with the caller, so
    this seam composes the same way the CLI's ``pull-all`` does.
    """
    queues = PullQueues()
    for court, docket in due:
        result = pull_case(client, corpus_db_path, data_root, court, docket)
        events = open_events(data_root, court, docket)
        if result.changed and events:
            queues.predict.append({"court": court, "docket": docket, "events": events})
        if result.resolved:
            queues.evaluate.append({"court": court, "docket": docket, "events": result.resolved})
        if result.reconcile:
            queues.reconcile.append(
                {
                    "court": court,
                    "docket": docket,
                    "events": [r.event_id for r in result.reconcile],
                    "reason": result.reconcile[0].reason,
                }
            )
    return queues
