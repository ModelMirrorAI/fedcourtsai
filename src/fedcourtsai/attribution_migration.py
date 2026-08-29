"""Repair ledger records the current extraction and attribution rules cannot produce.

Three shapes: :func:`reopen_misattributed_outcomes` for an outcome copied from a
sibling case-baseline event, :func:`remove_unmintable_baseline_events` for a
SCOTUS entry-pinned event carrying a case-baseline id — the shape that makes
such a copy possible — and :func:`remove_ungranted_merits_events` for an open
merits event on a docket the corpus records no cert grant for. All three are
deterministic, offline, dry-run by default, and idempotent.

## Outcomes copied from a sibling case-baseline event

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

## Unmintable SCOTUS case-baseline events

A SCOTUS docket carries its petition and appeal request kinds only as the
case-level baseline (:func:`fedcourtsai.pipeline.events.extract_events` mints no
entry-pinned event for either), so an **entry-pinned** row whose id carries a
case-baseline prefix is one no re-ingest reproduces. Such a row is the cause of
the copied outcome above rather than another instance of it: a second
case-baseline id is exactly what ``_cert_disposition_target`` cannot
disambiguate. Removal, not a reopen — the event names nothing the docket
supports, so leaving it open would park a permanent phantom on the case and, on
a cert docket, keep it forecastable.

## Merits events on a docket carrying no cert grant

A merits event is born from a grant: every path that mints one — the live
resolution pass and the corpus-convergence backfill alike — routes through
:func:`fedcourtsai.corpus.opens_merits_proceeding`, which requires the row's
``date_cert_granted``, and the grant moment is dated from that column. So an
**open merits-stage** SCOTUS event on a row whose ``date_cert_granted`` is NULL
is a second unmintable shape: the grant that would justify it is not in the
record, and no re-ingest or convergence pass reproduces the event. The shape
arises where a grant a merits event was already minted from stops being read out
of the docket text. The **live re-poll** is what clears the column:
:func:`fedcourtsai.pipeline.ingest._live_resolution` re-derives the disposition
and its dates from the proceedings on every poll, and ``date_cert_granted`` is
in none of the upsert's latch families (:func:`fedcourtsai.corpus._update_clause`),
so a poll that no longer matches a grant overwrites the stored date with NULL.
The disposition convergence's ``disowned-grant`` arm is the ledger-side sibling
reading the same guard; it writes no corpus column of its own.

Removal, not a reopen — and the warrant is *not* that the event stays
forecastable, because the fan-out already refuses it: a merits event is
order-kind, outside :data:`fedcourtsai.store._FORECASTABLE_KINDS`, so it can only
be admitted by :func:`fedcourtsai.store._merits_forecastable`, which requires
:func:`fedcourtsai.corpus.opens_merits_proceeding` and so the very column that is
NULL here. :func:`fedcourtsai.store.unforecastable_listed_events` already names
this exact shape in its refusal. The warrant is what the row does *instead*: it
is unmintable, it is permanently unresolvable (merits outcome detection reads
the same grant-gated columns, so nothing ever closes it), and it therefore parks
forever on the listed-unforecastable triage surface — a permanent dangling row
that every later reader has to re-adjudicate, not a cell that would be
mispredicted.

The population is deliberately narrow. Only **open** events: a resolved merits
event carries an observed judgment, a real record this sweep has no standing to
adjudicate. Only rows the corpus holds — a merits event whose case row is absent
is outside the population, since unmintability is established from a column that
cannot then be read. An event whose ledger directory holds a committed
``outcome.json`` is skipped and reported rather than removed, however the corpus
row reads: the two stores disagreeing about openness is a triage question, not a
licence to delete an observation.

Narrow in a third way that is easy to mistake for an oversight. The predicate
also requires the row's ``disposition`` to be outside
:data:`fedcourtsai.schemas.MERITS_PROCEEDING_DISPOSITIONS`, so it says *the grant
is not in the record* rather than *only its date is missing*. On a row still
labelled granted the removal would be irreversible: the granted leg of
:func:`fedcourtsai.corpus.live_rotation` retains a docket only while an **open
merits-stage event** exists, so deleting that event drops the row out of the very
rotation whose next poll would restore the date, and ``backfill-merits-events``
needs the date to re-mint. The class is empty today, so the narrowing costs
nothing and buys back the one shape where a mistake could not be undone.

The predicate is likewise **not** the whole unmintable-merits population, and
should not be widened to one. A row re-labelled ``gvr`` keeps its grant date
while ceasing to open a merits proceeding, so its merits event is equally
unmintable and equally refused by
:func:`fedcourtsai.store._merits_listing_refusal` — and is deliberately out of
scope here. This sweep removes the NULL-grant class only; the ``gvr`` class is a
different question about a row whose grant genuinely happened.

One skip is narrowable, because a phantom that reached the fan-out before it was
recognized carries the failure records of the cells that ran against it. An
event whose only committed output is ``attempt.json`` records — no
``prediction.json``, no ``evaluation.json``, no ``evaluations/`` directory —
holds a history of spend on an event that names nothing the docket supports.
Removing it trades that history for a ledger with no dangling phantom paths;
which is worth more is a judgement about the record rather than something the
sweep can read off it, so the removal is an explicit caller opt-in and the skip
stays the default. The opt-in never widens past that shape: one predicted or
graded artifact under the event keeps it skipped.
"""

from __future__ import annotations

import shutil
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from . import corpus
from .paths import CasePaths, EventPaths
from .pipeline import moments
from .pipeline.outcome import CASE_BASELINE_ID_PREFIXES
from .schemas import MERITS_PROCEEDING_DISPOSITIONS, Outcome, PredictableEvent, Stage
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
# The only files an event directory holds; the cell output lives in subdirectories.
_EVENT_DOCUMENTS = frozenset({"event.yaml", "outcome.json"})
_UNKNOWN_EVENT_REASON = (
    "the corpus holds no row for this event, so its stage cannot be read and the "
    "reopen would silently no-op"
)
_RECORDED_MERITS_REASON = (
    "the corpus row is open but the ledger carries an outcome.json; the stores "
    "disagree about a recorded judgment, which is triage rather than a phantom"
)
# The document a failed cell leaves behind: an attempt record, with no
# prediction or evaluation beside it. `remove_ungranted_merits_events` can be
# asked to treat a directory holding nothing else as removable.
_ATTEMPT_DOCUMENT = "attempt.json"

# The dispositions whose grant opens a merits proceeding, rendered for the
# ungranted-merits predicate's disposition leg. Read from the constant
# `corpus.opens_merits_proceeding` itself reads, so the sweep's notion of "the
# grant is not in the record" cannot drift from the mint's. Safe to inline: the
# values are closed-enum code constants, never user input.
_MERITS_PROCEEDING_SQL = ", ".join(f"'{d.value}'" for d in sorted(MERITS_PROCEEDING_DISPOSITIONS))


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
        """Baseline-prefixed AND not a declared later moment.

        A declared moment sharing the baseline's prefix (the cert arrival
        event) resolves with an outcome identical to the baseline's by
        design — one disposition fans across the stage — so treating it as a
        second baseline would report every resolved arrival-cohort case as a
        permanent baseline-pair triage. Stage routing disambiguates declared
        moments; this triage exists for the *undeclared* twin.
        """
        if not self.event.event_id.startswith(CASE_BASELINE_ID_PREFIXES):
            return False
        spec = moments.spec_for(self.event.event_id)
        return spec is None or spec.ordinal == 0

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


@dataclass
class UnmintableEventResult:
    """What an unmintable-event removal dropped (or would drop on a dry run).

    Shared by both removal sweeps — the entry-pinned case-baseline event and the
    open merits event on an ungranted docket — which differ only in the
    predicate that selects the population, never in what they report.
    """

    applied: bool = False
    removed: list[str] = field(default_factory=list)  # "<case_id>/<event_id>" dropped
    skipped: list[tuple[str, str]] = field(default_factory=list)  # (case_id/event_id, reason)


def remove_unmintable_baseline_events(
    conn: sqlite3.Connection, data_root: Path, *, apply: bool
) -> UnmintableEventResult:
    """Drop each entry-pinned SCOTUS event carrying a case-baseline id, in both stores.

    Dry run by default; ``apply`` removes the event's ledger directory and then
    deletes the corpus row through :func:`fedcourtsai.corpus.delete_event`.
    **Ledger first**, which is the convergent order for a corpus-driven scan:
    the corpus row is this sweep's detection handle, so deleting it first and
    stopping would strand the ledger directory where no later run can see it,
    while stopping after the directory goes leaves the row for the next run to
    re-find and finish as a row-only delete.

    Three shapes are skipped and reported rather than removed: an event carrying
    committed predict/evaluate output (a scored cell is evidence the event was
    treated as real, and the removal would strand it); an event whose committed
    outcome is *not* a copy of a case-baseline sibling's, since a distinct
    outcome is a real observation this sweep has no discriminator for; and a
    ledger directory holding anything beyond those two documents, which is an
    unrecognized shape rather than a phantom. See the module docstring for why
    removal rather than a reopen.
    """
    result = UnmintableEventResult(applied=apply)
    rows = conn.execute(
        "SELECT case_id, event_id FROM events "
        "WHERE court = 'scotus' AND docket_entry_id IS NOT NULL ORDER BY case_id, event_id"
    ).fetchall()
    for row in rows:
        case_id, event_id = str(row["case_id"]), str(row["event_id"])
        if not event_id.startswith(CASE_BASELINE_ID_PREFIXES):
            continue
        ref = f"{case_id}/{event_id}"
        paths = _ledger_event_paths(data_root, case_id, event_id)
        reason = _removal_blocker(paths, data_root, case_id) if paths is not None else None
        if reason is not None:
            result.skipped.append((ref, reason))
            continue
        result.removed.append(ref)
        if apply:
            _drop_event(conn, paths, case_id, event_id)
    return result


def remove_ungranted_merits_events(
    conn: sqlite3.Connection,
    data_root: Path,
    *,
    apply: bool,
    include_failed_attempts: bool = False,
) -> UnmintableEventResult:
    """Drop each open SCOTUS merits event whose row carries no cert grant, in both stores.

    Dry run by default; ``apply`` removes the event's ledger directory and then
    the corpus row, through the same :func:`_drop_event` seam and so in the same
    ledger-first order as :func:`remove_unmintable_baseline_events` — see that
    function on why the order is the convergent one for a corpus-driven scan.

    The population joins ``events`` to ``cases``, so a merits event whose case
    row is absent is out of scope rather than removed: the grant column that
    establishes unmintability cannot be read for it. The disposition leg beside
    the NULL-grant one keeps a row still labelled granted out of the sweep,
    where the removal would be irreversible — see the module docstring, which
    also carries why the warrant is the permanent dangling row rather than a
    forecastable one (the fan-out already refuses this shape), and why the
    predicate is not widened to every unmintable merits event.

    Three shapes are skipped and reported — an event carrying committed
    predict/evaluate output, one whose ledger directory holds a committed
    ``outcome.json`` (the stores disagree about a recorded judgment), and a
    directory holding anything beyond the two event documents.

    ``include_failed_attempts`` narrows the first of those skips. A phantom that
    was fanned out to cells before it was recognized carries their
    ``attempt.json`` failure records, and nothing else — no ``prediction.json``,
    no ``evaluation.json``, no ``evaluations/`` directory. Such a record
    documents spend on an event that names nothing the docket supports; removing
    it trades that failure history for a ledger with no dangling phantom paths.
    Which of the two is worth more is a judgement about the record rather than
    something the sweep can read off the ledger, so it is an explicit caller
    opt-in and the skip is the default. The opt-in is bounded by
    :func:`_only_failed_attempts`: any predicted or graded artifact under the
    event keeps it skipped whatever the flag says.
    """
    result = UnmintableEventResult(applied=apply)
    rows = conn.execute(
        "SELECT e.case_id AS case_id, e.event_id AS event_id FROM events e "
        "JOIN cases c ON c.case_id = e.case_id "
        "WHERE e.court = 'scotus' AND e.stage = ? AND e.resolved = 0 "
        "AND c.date_cert_granted IS NULL "
        f"AND (c.disposition IS NULL OR c.disposition NOT IN ({_MERITS_PROCEEDING_SQL})) "
        "ORDER BY e.case_id, e.event_id",
        (Stage.merits.value,),
    ).fetchall()
    for row in rows:
        case_id, event_id = str(row["case_id"]), str(row["event_id"])
        ref = f"{case_id}/{event_id}"
        paths = _ledger_event_paths(data_root, case_id, event_id)
        reason = (
            _ungranted_merits_blocker(paths, include_failed_attempts=include_failed_attempts)
            if paths is not None
            else None
        )
        if reason is not None:
            result.skipped.append((ref, reason))
            continue
        result.removed.append(ref)
        if apply:
            _drop_event(conn, paths, case_id, event_id)
    return result


def _drop_event(
    conn: sqlite3.Connection, paths: EventPaths | None, case_id: str, event_id: str
) -> None:
    """Delete one event from both stores, ledger directory first.

    The single write seam both removal sweeps use, so the order lives in one
    place: the corpus row is each sweep's detection handle, and an interrupted
    run must leave that handle behind for the next pass to re-find and finish.
    ``paths`` is ``None`` for a case id off the ``<court>/<docket>`` form, which
    has no ledger directory to drop.

    The whole directory goes, subdirectories included. The caller's blocker is
    the seam that vets the shape, and it vets each child by **name** plus a
    file/directory check — so what reaches here is a directory whose children
    the blocker enumerated and accepted, not one this function re-verifies.
    """
    if paths is not None and paths.base.is_dir():
        shutil.rmtree(paths.base)
    corpus.delete_event(conn, case_id, event_id)


def _only_failed_attempts(paths: EventPaths) -> bool:
    """Whether every committed cell artifact under this event is an attempt record.

    True only for a ``predictions/`` tree whose every file is an
    ``attempt.json`` — a cell that failed and recorded the failure — with no
    ``evaluations/`` directory at all. A single ``prediction.json`` or
    ``evaluation.json`` anywhere under it makes this false, which is what keeps
    the opt-in below from ever reaching a predicted or graded event.
    """
    if paths.evaluations_dir.exists():
        return False
    if not paths.predictions_dir.is_dir():
        return False
    committed = [child for child in paths.predictions_dir.rglob("*") if child.is_file()]
    return bool(committed) and all(child.name == _ATTEMPT_DOCUMENT for child in committed)


def _ledger_shape_blocker(paths: EventPaths, *, allow_failed_attempts: bool = False) -> str | None:
    """Why this event's committed directory forbids removal, or ``None``.

    The two refusals every removal sweep shares: committed cell output under the
    event, and a directory holding anything beyond the two event documents —
    an unrecognized shape rather than a phantom.

    ``allow_failed_attempts`` lifts the first refusal for the one shape
    :func:`_only_failed_attempts` recognizes, and then admits ``predictions/``
    as a directory child so the second refusal does not re-block what the first
    just let through. It never widens what counts as that shape.

    A permitted name is only permitted in its expected form: the two event
    documents must be files and ``predictions/`` a directory. Name alone would
    let a *directory* called ``event.yaml`` through to a recursive delete, which
    is precisely the unrecognized shape this refusal exists to hold back.
    """
    attempts_only = allow_failed_attempts and _only_failed_attempts(paths)
    if _carries_agent_artifacts(paths) and not attempts_only:
        return _AGENT_OUTPUT_REASON
    if not paths.base.is_dir():
        return None  # corpus-only row: nothing committed to weigh
    unexpected = sorted(
        child.name
        for child in paths.base.iterdir()
        if not (
            (child.name in _EVENT_DOCUMENTS and child.is_file())
            or (attempts_only and child.name == paths.predictions_dir.name and child.is_dir())
        )
    )
    if unexpected:
        return f"unrecognized files under the event directory: {', '.join(unexpected)}"
    return None


def _ungranted_merits_blocker(paths: EventPaths, *, include_failed_attempts: bool) -> str | None:
    """Why this merits event must not be removed, or ``None`` when it is safe to drop.

    Stricter than the baseline arm's blocker on the one point where the two
    shapes differ: any committed outcome blocks the removal, rather than only
    one that fails to copy a sibling's. The baseline arm has a fingerprint to
    tell a copied outcome from a real observation; here the corpus row already
    claims the event is open, so an ``outcome.json`` beside it is a
    store disagreement with no such discriminator.

    ``include_failed_attempts`` is the caller's opt-in described on
    :func:`remove_ungranted_merits_events`; the outcome refusal below applies
    either way, so the flag can never reach an event carrying a recorded
    judgment.
    """
    shape = _ledger_shape_blocker(paths, allow_failed_attempts=include_failed_attempts)
    if shape is not None:
        return shape
    if paths.outcome.is_file():
        return _RECORDED_MERITS_REASON
    return None


def _removal_blocker(paths: EventPaths, data_root: Path, case_id: str) -> str | None:
    """Why this event must not be removed, or ``None`` when it is safe to drop."""
    shape = _ledger_shape_blocker(paths)
    if shape is not None:
        return shape
    if not paths.outcome.is_file():
        return None  # a phantom with no recorded observation
    outcome = read_model(paths.outcome, Outcome)
    triple = (str(outcome.actual_disposition), str(outcome.resolved_at), outcome.actual_granted)
    if triple not in _baseline_fingerprints(data_root, case_id, paths.base.name):
        return (
            f"its outcome {triple} copies no case-baseline sibling's, so it is a real observation"
        )
    return None


def _baseline_fingerprints(
    data_root: Path, case_id: str, exclude: str
) -> set[tuple[str, str, int]]:
    """The outcome triples this case's *other* case-baseline events carry."""
    court, _, docket = case_id.partition("/")
    events_dir = CasePaths(data_root, court, int(docket)).event(exclude).base.parent
    fingerprints = set()
    for event_dir in sorted(p for p in events_dir.iterdir() if p.is_dir()):
        if event_dir.name == exclude or not event_dir.name.startswith(CASE_BASELINE_ID_PREFIXES):
            continue
        outcome_path = EventPaths(event_dir).outcome
        if not outcome_path.is_file():
            continue
        outcome = read_model(outcome_path, Outcome)
        fingerprints.add(
            (str(outcome.actual_disposition), str(outcome.resolved_at), outcome.actual_granted)
        )
    return fingerprints


def _ledger_event_paths(data_root: Path, case_id: str, event_id: str) -> EventPaths | None:
    """The committed event directory for ``(case_id, event_id)``, or ``None`` off the form."""
    court, _, docket = case_id.partition("/")
    if not docket.isdigit():
        return None
    return CasePaths(data_root, court, int(docket)).event(event_id)
