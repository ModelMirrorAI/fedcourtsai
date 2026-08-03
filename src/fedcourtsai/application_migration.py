"""Converge application-docket baseline events onto the motion/interim form.

A SCOTUS ``YYAnnn`` application docket (a stay or injunction application) is a
motion governed by the interim standard, not a cert petition, so its case-level
baseline event is ``evt-motion-disposition`` with ``kind = motion`` /
``stage = interim`` (:func:`fedcourtsai.pipeline.ingest.default_event`). This
migration renames any cert-shaped baseline (``evt-petition-disposition`` /
``kind = petition`` / ``stage = cert``) still sitting on an application docket
to that form via :func:`fedcourtsai.corpus.rename_event`, carrying every field
and the ``resolved`` latch. Deterministic, offline, idempotent — a second run
finds every application docket already on the motion baseline and renames
nothing.

Two shapes are skipped and reported rather than renamed, because folding them
would falsify the record: a case whose git ledger holds committed artifacts
under the old identity (the rename would orphan them against the corpus — the
referential validation's no-orphan-judgments check), and a case whose existing
``evt-motion-disposition`` row is pinned to a docket entry (that row is some
*filing's* event, not the case baseline; folding the baseline onto it would
write one filing's ``resolved`` latch and entry pin onto another). Both land on
the dry-run report for maintainer triage.

After the relabel an application docket's lone event is motion-kind, which the
case-baseline resolution guard (:mod:`fedcourtsai.pipeline.outcome`)
deliberately declines to attribute a case-level disposition to — reinforced by
the form-keyed application guard there, which keeps every application spelling
out of the cert rule regardless of its baseline's current shape. Interim
outcome recording is stage-keyed and ships with the interim predict path; note
that a decided application's baseline still latches ``resolved`` on
re-extraction (:func:`fedcourtsai.pipeline.ingest.default_event` marks a
decided row's baseline resolved), so the future interim recording must
backfill keyed on the row's disposition, not on open events.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import corpus, ids
from .paths import CasePaths
from .schemas import EventKind, Stage
from .supremecourt import parse_scotus_application_number

# The two baseline identities the relabel moves between.
PETITION_BASELINE_EVENT_ID = ids.event_id(EventKind.petition.value, "disposition")
MOTION_BASELINE_EVENT_ID = ids.event_id(EventKind.motion.value, "disposition")


@dataclass
class ApplicationRelabelResult:
    """What the application-baseline relabel changed (or would change on a dry run)."""

    applied: bool = False
    renamed: list[str] = field(default_factory=list)  # case ids renamed (or to rename)
    already_relabeled: int = 0  # application dockets already on the motion baseline
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (case_id, reason) for triage


def _ledger_blocks(data_root: Path, case_id: str) -> bool:
    """Whether the git ledger holds artifacts under the old identity for this case."""
    court, _, docket = case_id.partition("/")
    if not docket.isdigit():
        return False
    event_dir = CasePaths(data_root, court, int(docket)).event(PETITION_BASELINE_EVENT_ID).base
    return event_dir.exists()


def relabel_application_baseline_events(
    conn: sqlite3.Connection, data_root: Path, *, apply: bool
) -> ApplicationRelabelResult:
    """Rename each application docket's cert-shaped baseline to motion/interim.

    Dry run by default (finds the rows, writes nothing); ``apply`` renames each
    matching event through :func:`fedcourtsai.corpus.rename_event` (atomic per
    case, ``resolved`` latch preserved, casestore mirror included). A docket
    counts as an application by its docket number's strict ``YYAnnn`` form
    (:func:`fedcourtsai.supremecourt.parse_scotus_application_number`) — the
    same key :func:`fedcourtsai.pipeline.ingest.default_event` mints on, so a
    re-discovered docket reproduces exactly the migrated event id. ``data_root``
    is the git ledger root, consulted read-only for the committed-artifact skip
    (see the module docstring for both skip shapes).
    """
    result = ApplicationRelabelResult(applied=apply)
    records = conn.execute(
        "SELECT case_id, docket_number FROM cases WHERE court = 'scotus' ORDER BY case_id"
    ).fetchall()
    for record in records:
        if parse_scotus_application_number(record["docket_number"]) is None:
            continue
        case_id = str(record["case_id"])
        events = {e.event_id: e for e in corpus.events_for_case(conn, case_id)}
        old = events.get(PETITION_BASELINE_EVENT_ID)
        if old is None:
            if MOTION_BASELINE_EVENT_ID in events:
                result.already_relabeled += 1
            continue
        if _ledger_blocks(data_root, case_id):
            result.skipped.append(
                (case_id, "committed ledger artifacts under the old identity; rename would orphan")
            )
            continue
        existing_motion = events.get(MOTION_BASELINE_EVENT_ID)
        if existing_motion is not None and existing_motion.docket_entry_id is not None:
            result.skipped.append(
                (case_id, "existing evt-motion-disposition row is entry-pinned, not the baseline")
            )
            continue
        result.renamed.append(case_id)
        if apply:
            corpus.rename_event(
                conn,
                case_id,
                PETITION_BASELINE_EVENT_ID,
                # Re-validated (not model_copy) so every carried field normalizes
                # and a future CorpusEvent field travels by construction.
                corpus.CorpusEvent.model_validate(
                    {
                        **old.model_dump(),
                        "event_id": MOTION_BASELINE_EVENT_ID,
                        "kind": EventKind.motion,
                        "stage": Stage.interim,
                    }
                ),
            )
    return result
