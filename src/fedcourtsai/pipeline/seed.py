"""``run-seed``: pull a docket from CourtListener and start tracking it.

Deterministic — no agent required. Writes the canonical docket record and a
``case.yaml``, then leaves an initial dated snapshot so predictors have a fixed
input to reason from.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

from .. import ids
from ..courtlistener import CourtListenerClient
from ..paths import CasePaths
from ..schemas import CaseStatus, TrackedCase
from ..serialize import write_raw_json, write_yaml


def seed_case(
    client: CourtListenerClient,
    data_root: Path,
    court_id: str,
    docket_id: int,
) -> TrackedCase:
    docket = client.get_docket(docket_id)
    entries = client.iter_docket_entries(docket_id)
    docket_with_entries = {**docket, "docket_entries": entries}

    paths = CasePaths(data_root, court_id, docket_id)
    write_raw_json(paths.docket, docket_with_entries)
    today = date.today().isoformat()
    write_raw_json(paths.snapshot(today), docket_with_entries)

    case = TrackedCase(
        case_id=ids.case_id(court_id, docket_id),
        court_id=court_id,
        docket_id=docket_id,
        docket_number=str(docket.get("docket_number", "")),
        case_name=str(docket.get("case_name", "")),
        courtlistener_url=docket.get("absolute_url"),
        status=CaseStatus.active,
        tracked_since=date.today(),
        last_pulled=datetime.now(UTC),
    )
    write_yaml(paths.case_file, case)
    return case
