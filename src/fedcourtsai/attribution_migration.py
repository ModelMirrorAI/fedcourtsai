"""Reopen committed outcomes copied from a sibling case-baseline event.

The case-level disposition attaches to exactly one event, and the routing that
picks it (:func:`fedcourtsai.pipeline.outcome._cert_disposition_target`) is
narrow: the one event staged ``cert``, or a *lone* open stage-less case-baseline
event. The committed ledger holds records no such rule produces — a petition's
disposition duplicated onto a sibling event that never had it.

What identifies such a record is the duplication itself: the outcome repeats a
case-baseline sibling's ``(actual_disposition, resolved_at, actual_granted)``
exactly. That is falsifiable from the committed ledger alone, and it does not
rely on date ordering — an outcome resolving before its own event opened is a
faithful upstream shape on this docket source, not evidence of fabrication, so
it is deliberately not the discriminator.

Only a **non-case-baseline** event is repaired, because only there does the
repair converge. Reopening a case-baseline event hands it straight back to the
stage-less fallback — a reopened lone baseline is exactly that rule's target, so
the next resolution pass rewrites the outcome that was just deleted, and the
sweep churns instead of correcting. A case whose duplication sits between two
case-baseline events is therefore reported for triage rather than repaired: it
needs a routing or minting change, not a deletion.

Repair is deletion plus reopening, never re-derivation: the ledger does not
carry the source order text, so a motion's true disposition is not recoverable
here, and an open event is the honest state. Nothing resolves such an event
afterwards — no rule attributes a cert docket's disposition to a motion — so it
stays open: a quiet no-op on every later pass where a case-baseline event
already carries the case-level disposition, and otherwise an entry on the
resolution pass's ``unrecorded`` triage queue. Either way it is never written
again. That is the intended end state — visible and unattributed, instead of
confidently wrong.

Both stores move together, since the corpus event row is the source of truth for
openness and a ledger-only fix would leave the event closed to re-detection. The
corpus flips **first**, so an interrupted repair leaves an open event beside a
stale outcome — a shape the next run detects and finishes — rather than an event
the corpus still calls resolved with no ``outcome.json`` beside it, which is
both invisible to a re-run (detection keys on the outcome file) and the shape
that would mint an evaluate cell with no ground truth. Deterministic, offline,
idempotent — a second run finds every repaired event already open and carrying
no outcome.

An event the corpus does not know is never repaired: the stage exemption below
reads the corpus row, and :func:`fedcourtsai.corpus.set_event_resolved` no-ops
on an unknown ``(case_id, event_id)``, so acting on one would delete a
legitimate outcome while reporting a reopen that never happened.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import corpus
from .paths import EventPaths
from .pipeline.outcome import CASE_BASELINE_ID_PREFIXES
from .schemas import Outcome, PredictableEvent, Stage
from .serialize import read_model, write_yaml

# The stages whose events carry a disposition of their own rather than the cert
# one — an interim application's motion baseline, a granted case's merits
# judgment. Their outcomes are legitimate off the case-baseline ids, so a
# duplicate reading is never applied to them.
_SELF_RESOLVING_STAGES = frozenset({Stage.interim, Stage.merits})

_BASELINE_PAIR_REASON = (
    "duplicate sits between two case-baseline events; reopening re-arms the "
    "stage-less fallback, so this needs a routing fix rather than a deletion"
)
_AGENT_OUTPUT_REASON = "committed predict/evaluate output under it"
_UNKNOWN_EVENT_REASON = (
    "the corpus holds no row for this event, so its stage cannot be read and the "
    "reopen would silently no-op"
)


@dataclass
class MisattributionRepairResult:
    """What the misattribution repair changed (or would change on a dry run)."""

    applied: bool = False
    reopened: list[str] = field(default_factory=list)  # "<case_id>/<event_id>" repaired
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (case_id/event_id, reason)


@dataclass(frozen=True)
class _Recorded:
    """One committed event that carries an outcome, with both documents read."""

    paths: EventPaths
    event: PredictableEvent
    outcome: Outcome
    stage: Stage | None
    known_to_corpus: bool

    @property
    def ref(self) -> str:
        return f"{self.event.case_id}/{self.event.event_id}"

    @property
    def is_baseline(self) -> bool:
        return self.event.event_id.startswith(CASE_BASELINE_ID_PREFIXES)

    @property
    def fingerprint(self) -> tuple[str, str, int]:
        """The outcome triple a copy reproduces exactly."""
        return (
            str(self.outcome.actual_disposition),
            str(self.outcome.resolved_at),
            self.outcome.actual_granted,
        )


def _recorded_events(conn: sqlite3.Connection, case_dir: Path) -> list[_Recorded]:
    """Every event under one case directory that carries a committed outcome.

    The stage comes from the corpus event row rather than the committed
    ``event.yaml``: the corpus is the source of truth for stage everywhere the
    pipeline reads it, so the exemption keys on the same value the router does.
    """
    events_dir = case_dir / "events"
    if not events_dir.is_dir():
        return []
    recorded = []
    stages: dict[str, Stage | None] | None = None
    for event_dir in sorted(p for p in events_dir.iterdir() if p.is_dir()):
        paths = EventPaths(event_dir)
        if not (paths.outcome.is_file() and paths.event_file.is_file()):
            continue
        event = read_model(paths.event_file, PredictableEvent)
        if stages is None:
            stages = {
                row.event_id: Stage(row.stage) if row.stage is not None else None
                for row in corpus.events_for_case(conn, event.case_id)
            }
        recorded.append(
            _Recorded(
                paths=paths,
                event=event,
                outcome=read_model(paths.outcome, Outcome),
                stage=stages.get(event.event_id),
                known_to_corpus=event.event_id in stages,
            )
        )
    return recorded


def _carries_agent_artifacts(paths: EventPaths) -> bool:
    """Whether a predict or evaluate cell has any committed directory under this event.

    Directory presence, not a ``prediction.json`` / ``evaluation.json`` read: an
    empty leftover directory then blocks the delete rather than risking a
    stranded evaluation, which is the safe direction to err in.
    """
    return paths.predictions_dir.exists() or paths.evaluations_dir.exists()


def _misattributed(recorded: list[_Recorded]) -> tuple[list[_Recorded], list[tuple[str, str]]]:
    """Split one case's recorded events into the repairable ones and triage notes."""
    baselines = [entry for entry in recorded if entry.is_baseline]
    fingerprints = {entry.fingerprint for entry in baselines}

    repairable = [
        entry
        for entry in recorded
        if not entry.is_baseline
        and entry.stage not in _SELF_RESOLVING_STAGES
        and entry.fingerprint in fingerprints
    ]
    skipped = [
        (entry.ref, _BASELINE_PAIR_REASON)
        for entry in baselines
        if sum(other.fingerprint == entry.fingerprint for other in baselines) > 1
    ]
    return repairable, skipped


def reopen_misattributed_outcomes(
    conn: sqlite3.Connection, data_root: Path, *, apply: bool
) -> MisattributionRepairResult:
    """Delete each copied outcome and reopen its event, in both stores.

    Dry run by default (finds the records, writes nothing); ``apply`` removes
    the ``outcome.json``, rewrites ``event.yaml`` with ``resolved = false``, and
    flips the corpus event row open through
    :func:`fedcourtsai.corpus.set_event_resolved`. ``data_root`` is the git
    ledger root. See the module docstring for what identifies a copy, why only
    non-case-baseline events are repaired, and why nothing is re-derived.
    """
    result = MisattributionRepairResult(applied=apply)
    for case_dir in sorted((data_root / "cases").glob("*/*")):
        repairable, skipped = _misattributed(_recorded_events(conn, case_dir))
        result.skipped.extend(skipped)
        for entry in repairable:
            if not entry.known_to_corpus:
                result.skipped.append((entry.ref, _UNKNOWN_EVENT_REASON))
                continue
            if _carries_agent_artifacts(entry.paths):
                result.skipped.append((entry.ref, _AGENT_OUTPUT_REASON))
                continue
            result.reopened.append(entry.ref)
            if apply:
                # Corpus first: see the module docstring on the interrupted-repair shape.
                corpus.set_event_resolved(
                    conn, entry.event.case_id, entry.event.event_id, resolved=False
                )
                entry.paths.outcome.unlink()
                write_yaml(
                    entry.paths.event_file, entry.event.model_copy(update={"resolved": False})
                )
    result.reopened.sort()
    result.skipped.sort()
    return result
