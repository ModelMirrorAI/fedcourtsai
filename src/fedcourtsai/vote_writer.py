"""Stamp per-Justice vote records onto committed outcomes from the Court's documents.

The writer half of the two registered vote sources
(:mod:`fedcourtsai.pipeline.vote_sources`). The readers are read-only and
already exist — :mod:`fedcourtsai.pipeline.opinion_lineups` for a merits
opinion's syllabus lineup, :mod:`fedcourtsai.pipeline.order_lineups` for the
notations and separate-writing headers of the Court's orders. This module maps
a reading onto the committed ``outcome.json`` it describes and writes
``votes``, ``vote_provenance`` and ``writing_roles`` there, and nothing else.

**Where outcomes live.** Only in the ledger: ``outcome.json`` under
``data/cases/<court>/<docket>/events/<event>/``. The corpus holds no outcome,
only the case row, and the writer reads it for one column: the case's docket
number (``24-43``, ``25A443``), which is how a ledger case — keyed by its
CourtListener docket id — is found in the Court's documents. So the writer
reads the corpus, writes only the ledger, and never writes the corpus.

**Two passes, one per source**, because the two populations, fetch plans and
record shapes share nothing but the stamping:

- :func:`stamp_opinion_votes` — merits-stage outcomes resolved in an October
  Term the opinions listing links per opinion (from
  :data:`OPINION_VOTE_TERM_FLOOR`). A record is a whole bench
  (``complete: true``) or nothing. The opinion is found through the Term's
  listing, and the Term's Granted & Noted list both maps a consolidated case's
  other dockets onto the one listed opinion and cross-checks the reading: a
  lead author, decision date or separate writer the list prints differently
  holds the record back.
- :func:`stamp_order_votes` — cert- and interim-stage outcomes resolved in
  :data:`ORDER_VOTE_TERMS`. The record is read from every document the Court
  lists for the outcome's ``resolved_at`` — the date of the order disposing of
  the petition or application — so a notation on a later rehearing or motion
  order is never attached to it, and a docket whose order text on that date
  mentions a rehearing is held back. Its votes are partial by construction
  (``complete: false``): only the Justices who noted a vote, or who took no
  part, are there. ``writing_roles`` is stamped only where the reading
  observed every participating Justice's writing, and only once the order is
  :data:`SETTLING_DAYS` old — the Court can publish a writing respecting an
  order after the order itself, so a same-week reading could record a
  Justice as having written nothing who has not written *yet*. Dates inside
  the window are not read at all.

**Never overwrites silently.** An outcome already carrying the identical
record is left alone (``unchanged``), which is what makes a re-run a no-op. An
outcome carrying a *different* vote record is held back and reported unless
the caller passes ``replace_differing`` — a grammar bump, a corrected reading —
and each replacement counts toward the bound like a new stamp.

**Scoring.** Nothing here scores or is scored differently: vote scoring is
gated on a declared merits moment and on ``vote_provenance.complete``
(:func:`fedcourtsai.pipeline.evaluate.bench_vote_accuracy`), so an
orders-source record never enters a vote figure, and ``writing_roles`` is read
by no scorer. A merits record is what that gate was registered to read.

Dry run by default; ``apply`` refuses above ``max_stamps``. With the population
empty no network request is made at all.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Final

import httpx
from pydantic import ValidationError

from .corpus import ReadConnection
from .pipeline import granted_noted, moments, opinion_lineups, order_lineups
from .pipeline.lineup import WritingKind
from .pipeline.vote_sources import SUPREMECOURT_OPINIONS, SUPREMECOURT_ORDERS
from .schemas import (
    GrammarStamp,
    JusticeVote,
    JusticeWriting,
    Outcome,
    PredictableEvent,
    Stage,
    VoteProvenance,
    VoteValue,
)
from .serialize import read_model, write_json
from .supremecourt import october_term_year
from .validate import vote_record_problems

#: The first October Term whose opinions listing links a PDF per opinion; the
#: Terms before it link whole volumes, which the reader does not read.
OPINION_VOTE_TERM_FLOOR: Final = 2020

#: The October Terms the order-list pass reads: the two most recent complete
#: Terms. Both sat the same nine-Justice bench, both grammars were checked
#: against real OT2025 orders, and every interim outcome in the ledger as of
#: 2026-09-30 is among them.
ORDER_VOTE_TERMS: Final = (2024, 2025)

#: Days after an order date before its writings are read as complete. A writing
#: respecting an order is ordinarily published with it, but not always, and a
#: Justice observed to have written nothing must not merely not have written yet.
SETTLING_DAYS: Final = 7

_NOT_SITTING: Final = frozenset({VoteValue.recused, VoteValue.did_not_participate})
_TERM_DOCKET_RE: Final = re.compile(r"\b\d{2}-\d+\b")
_APPLICATION_RE: Final = re.compile(r"^\d{2}A\d+$")


@dataclass(frozen=True)
class VoteRecord:
    """What one reading would stamp onto an outcome."""

    votes: tuple[JusticeVote, ...]
    provenance: VoteProvenance
    writing_roles: tuple[JusticeWriting, ...] | None


@dataclass(frozen=True)
class OutcomeTarget:
    """One committed outcome in a pass's population."""

    path: Path
    case_id: str
    event_id: str
    stage: str
    outcome: Outcome

    @property
    def ref(self) -> str:
        return f"{self.case_id}/{self.event_id}"


@dataclass(frozen=True)
class VoteStamp:
    """One outcome the pass stamps (or would, on a dry run)."""

    target: OutcomeTarget
    record: VoteRecord
    #: True when the outcome carried a different record this one replaces.
    replaces: bool = False


@dataclass
class VoteWriteResult:
    """What a pass stamped, left, held back and could not read."""

    source: str
    applied: bool = False
    #: True when ``apply`` was asked for but the bound refused it; nothing is written.
    refused: bool = False
    stamps: list[VoteStamp] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    #: ``(ref, reason)``: a differing record left in place, or a reading not trusted.
    held_back: list[tuple[str, str]] = field(default_factory=list)
    #: ``(ref, reason)``: nothing to stamp — no reading, or nothing observed.
    skipped: list[tuple[str, str]] = field(default_factory=list)
    #: A listing or list that could not be fetched; the pass is not trustworthy.
    failures: list[str] = field(default_factory=list)
    population: int = 0


def _blank(outcome: Outcome) -> bool:
    return outcome.vote_provenance is None and not outcome.votes and outcome.writing_roles is None


def _same(outcome: Outcome, record: VoteRecord) -> bool:
    return (
        outcome.vote_provenance == record.provenance
        and list(outcome.votes) == list(record.votes)
        and (outcome.writing_roles is None) == (record.writing_roles is None)
        and list(outcome.writing_roles or ()) == list(record.writing_roles or ())
    )


def stamped(outcome: Outcome, record: VoteRecord) -> Outcome:
    """``outcome`` with ``record``'s three fields written, validated whole.

    Raises ``pydantic.ValidationError`` on a record the model refuses.
    """
    return Outcome.model_validate(
        {
            **outcome.model_dump(mode="json"),
            "votes": [v.model_dump(mode="json") for v in record.votes],
            "vote_provenance": record.provenance.model_dump(mode="json"),
            "writing_roles": (
                None
                if record.writing_roles is None
                else [r.model_dump(mode="json") for r in record.writing_roles]
            ),
        }
    )


def _conformance(target: OutcomeTarget, record: VoteRecord) -> str | None:
    """Why the stamped outcome would fail the ledger's vote check, or ``None``.

    The same check ``validate`` holds every committed outcome to
    (:func:`fedcourtsai.validate.vote_record_problems`), run before the record
    is planned — in the dry run as in the apply — so a record the ledger would
    refuse is held back and reported rather than committed to ``main``.
    """
    try:
        outcome = stamped(target.outcome, record)
    except ValidationError as exc:
        return f"the record does not validate: {exc.errors()[0]['msg']}"
    problems = vote_record_problems(outcome, target.path.parent)
    if problems:
        return "the record departs from its source's registration: " + "; ".join(problems)
    return None


def _classify(
    target: OutcomeTarget,
    record: VoteRecord,
    result: VoteWriteResult,
    *,
    replace_differing: bool,
) -> None:
    """File one reading against its outcome: new, unchanged, replacement, or held."""
    outcome = target.outcome
    if _same(outcome, record):
        result.unchanged.append(target.ref)
        return
    if (why := _conformance(target, record)) is not None:
        result.held_back.append((target.ref, why))
        return
    if _blank(outcome):
        result.stamps.append(VoteStamp(target, record))
    elif replace_differing:
        result.stamps.append(VoteStamp(target, record, replaces=True))
    else:
        result.held_back.append(
            (
                target.ref,
                "carries a different vote record; pass replace-differing to replace it",
            )
        )


def _term(day: date) -> int:
    return october_term_year(day)


def _targets(
    data_root: Path, *, stages: frozenset[str], keep: Callable[[date], bool]
) -> list[OutcomeTarget]:
    """Every committed SCOTUS outcome on one of ``stages`` whose ``resolved_at`` passes ``keep``.

    The stage is the committed ``event.yaml``'s, or where it records none — the
    cert baselines carry none of their own — the declared moment's
    (:func:`fedcourtsai.pipeline.moments.event_stage`), the reading the
    ``validate`` conformance check makes. It is read only for outcomes the date
    filter admits.
    """
    found: list[OutcomeTarget] = []
    for path in sorted((data_root / "cases").glob("scotus/*/events/*/outcome.json")):
        outcome = read_model(path, Outcome)
        if not keep(outcome.resolved_at):
            continue
        event_file = path.parent / "event.yaml"
        if not event_file.is_file():
            continue
        event = read_model(event_file, PredictableEvent)
        stage = moments.event_stage(event.stage, event.event_id)
        if stage is None or str(stage) not in stages:
            continue
        found.append(OutcomeTarget(path, outcome.case_id, outcome.event_id, str(stage), outcome))
    return found


def docket_numbers(conn: ReadConnection, case_ids: Iterable[str]) -> dict[str, str]:
    """Each case's docket number as the Court prints it, from the corpus case row."""
    wanted = sorted(set(case_ids))
    numbers: dict[str, str] = {}
    for start in range(0, len(wanted), 500):
        chunk = wanted[start : start + 500]
        marks = ",".join("?" for _ in chunk)
        for row in conn.execute(
            f"SELECT case_id, docket_number FROM cases WHERE case_id IN ({marks})",
            chunk,
        ):
            if row["docket_number"]:
                numbers[str(row["case_id"])] = " ".join(str(row["docket_number"]).split()).upper()
    return numbers


def _sitting_roles(votes: Sequence[JusticeVote]) -> tuple[JusticeWriting, ...]:
    return tuple(
        JusticeWriting(justice=v.justice, writing=v.writing)
        for v in votes
        if v.vote not in _NOT_SITTING
    )


# --- The merits pass: opinions ------------------------------------------------


def _listed_dockets(entry: opinion_lineups.OpinionListing) -> set[str]:
    """Every Term-form docket number the listing row's docket cell prints."""
    return {m.upper() for m in _TERM_DOCKET_RE.findall(entry.docket)}


def opinion_record(
    reading: opinion_lineups.OpinionLineupReading,
    entry: granted_noted.GrantedNotedEntry | None,
) -> tuple[VoteRecord | None, str | None]:
    """The record one opinion reading yields, or why it yields none.

    A reading yields one only when it produced a complete vote record and the
    Granted & Noted list prints the same lead author, decision date and
    separate writers. ``writing_roles`` is stamped where the syllabus observed
    every participating Justice's writing.
    """
    if reading.votes is None or reading.vote_provenance is None:
        reason = reading.reason or "; ".join(reading.problems) or "the lineup is incomplete"
        return None, f"no complete lineup ({reading.status}): {reason}"
    if entry is None:
        return None, "the Granted & Noted list prints no entry for the docket to check against"
    summary = granted_noted.summarize(
        [(WritingKind(w.kind), tuple(w.authors)) for w in reading.writings]
    )
    found = granted_noted.disagreements(
        entry, summary, bench=reading.bench, decided=reading.decided
    )
    if found:
        return None, "Granted & Noted disagrees: " + "; ".join(found)
    roles = _sitting_roles(reading.votes) if reading.writings_complete else None
    return VoteRecord(tuple(reading.votes), reading.vote_provenance, roles), None


def _opinion_target(  # noqa: PLR0911 - one return per reason an outcome gets no record
    target: OutcomeTarget,
    number: str | None,
    listing: Sequence[opinion_lineups.OpinionListing],
    entries: Mapping[str, granted_noted.GrantedNotedEntry],
    fetcher: opinion_lineups.OpinionFetcher,
    readings: dict[str, opinion_lineups.OpinionLineupReading],
) -> tuple[VoteRecord | None, str | None, bool]:
    """One merits outcome's record, or why none and whether that is a hold-back.

    ``readings`` caches one reading per opinion URL across a Term, since a
    consolidated case's dockets share an opinion.
    """
    if number is None:
        return None, "the corpus holds no docket number", False
    entry = entries.get(number)
    group = set(entry.dockets) if entry is not None else {number}
    # The docket's own row where the listing prints one; a consolidated
    # group's row only where the docket has none of its own. Either way
    # exactly one opinion, or the record is held back: a group-mate's opinion
    # must never stand in for one the listing prints for this docket.
    own = [row for row in listing if number in _listed_dockets(row)]
    rows = own or [row for row in listing if _listed_dockets(row) & group]
    if not rows:
        return None, f"no opinion on the listing names the docket: {number}", False
    if len({row.url for row in rows}) > 1:
        return None, f"several opinions on the listing name the docket: {number}", True
    row = rows[0]
    if (reason := opinion_lineups.skip_reason(row)) is not None:
        return None, f"the listing's opinion is not read: {reason}", False
    reading = readings.get(row.url)
    if reading is None:
        reading = opinion_lineups.read_entry(row, fetcher)
        readings[row.url] = reading
    record, why = opinion_record(reading, entry)
    if record is None:
        return None, why, reading.votes is not None
    if reading.decided != target.outcome.resolved_at:
        return (
            None,
            f"the opinion's date is not the outcome's: {reading.decided} against "
            f"{target.outcome.resolved_at}",
            True,
        )
    return record, None, False


def stamp_opinion_votes(
    conn: ReadConnection,
    data_root: Path,
    fetcher: opinion_lineups.OpinionFetcher,
    granted_noted_text: Callable[[int], str | None],
    *,
    apply: bool,
    max_stamps: int | None = None,
    replace_differing: bool = False,
) -> VoteWriteResult:
    """Stamp merits outcomes with the syllabus lineup of the opinion deciding them.

    ``granted_noted_text(term)`` returns the extracted text of the Term's
    Granted & Noted list (two-digit Term), or ``None`` when it cannot be read.
    """
    result = VoteWriteResult(source=SUPREMECOURT_OPINIONS, applied=apply)
    targets = _targets(
        data_root,
        stages=frozenset({Stage.merits.value}),
        keep=lambda day: _term(day) >= OPINION_VOTE_TERM_FLOOR,
    )
    result.population = len(targets)
    numbers = docket_numbers(conn, (t.case_id for t in targets))
    by_term: dict[int, list[OutcomeTarget]] = defaultdict(list)
    for target in targets:
        by_term[_term(target.outcome.resolved_at)].append(target)
    for term, members in sorted(by_term.items()):
        yy = term % 100
        try:
            listing = fetcher.listing(yy)
        except httpx.HTTPError as exc:
            result.failures.append(f"OT{yy:02d} opinions listing: {exc}")
            result.skipped.extend(
                (t.ref, f"the opinions listing could not be read: OT{yy:02d}") for t in members
            )
            continue
        text = granted_noted_text(yy)
        if text is None:
            result.failures.append(f"OT{yy:02d} Granted & Noted list could not be read")
        entries = granted_noted.by_docket(granted_noted.parse_granted_noted(text or ""))
        readings: dict[str, opinion_lineups.OpinionLineupReading] = {}
        for target in members:
            record, reason, held = _opinion_target(
                target, numbers.get(target.case_id), listing, entries, fetcher, readings
            )
            if record is not None:
                _classify(target, record, result, replace_differing=replace_differing)
            elif reason is not None:
                (result.held_back if held else result.skipped).append((target.ref, reason))
    return _finish(result, apply=apply, max_stamps=max_stamps)


# --- The cert and interim pass: orders ----------------------------------------


def order_record(  # noqa: PLR0911 - one return per reason a reading yields no record
    reading: order_lineups.OrderDocketReading, *, shared_across_stages: bool = False
) -> tuple[VoteRecord | None, str | None]:
    """The partial record one docket's order-date reading yields, or why none.

    Held back: any problem on the reading (the channel has already emptied its
    votes); an order or writing the docket shares with a docket of the other
    stage (``shared_across_stages`` — a cert petition grouped with an
    application, where a noted vote on the stay would otherwise be read onto
    the petition); no order text for the docket on the date (only a writing
    names it); or order text mentioning a rehearing — a noted act or a
    non-participation there attaches to the rehearing, not to the cert or
    application act. Nothing to stamp: no noted vote and writings not
    observed in full.
    """
    if reading.problems:
        return None, "the reading has problems: " + "; ".join(reading.problems)
    if shared_across_stages:
        return None, (
            "the docket shares its order or a writing with a docket of the other stage: "
            "a cert petition grouped with an application"
        )
    acts = [p for p in reading.parts if p.where != "header"]
    if not acts:
        return None, "only a writing names the docket on the date"
    if any("rehearing" in p.text.lower() for p in acts):
        return None, "the docket's order text mentions a rehearing"
    bench = list(reading.bench)
    votes = tuple(reading.votes)
    roles: tuple[JusticeWriting, ...] | None = None
    if reading.writings_complete:
        roles = tuple(
            JusticeWriting(justice=name, writing=reading.writing_roles[name])
            for name in bench
            if name in reading.writing_roles
        )
    if not votes and roles is None:
        return None, None
    absent = sum(1 for v in votes if v.vote in _NOT_SITTING)
    stamps = sorted({(p.grammar, p.grammar_version) for p in reading.parts})
    names = [grammar for grammar, _ in stamps]
    if len(set(names)) != len(names):
        return None, "the reading's pieces carry two versions of one grammar"
    try:
        provenance = VoteProvenance(
            source=SUPREMECOURT_ORDERS,
            documents=sorted(reading.documents),
            grammars=[GrammarStamp(grammar=g, version=v) for g, v in stamps],
            participating=len(bench) - absent,
            complete=False,
        )
    except ValueError as exc:
        return None, f"no valid provenance: {exc}"
    return VoteRecord(votes, provenance, roles), None


def _is_application(docket: str) -> bool:
    return _APPLICATION_RE.match(docket) is not None


def _shared_across_stages(dockets: Sequence[order_lineups.OrderDocketReading]) -> set[str]:
    """Dockets sharing a piece of order text or a writing with the other stage's form.

    An order-list entry groups the dockets one order disposes of, and an
    application docket (``24A500``) can sit in a cert petition's group. The
    channel reads each piece onto every docket it names, so a notation on the
    application's act would read onto the petition too. Pieces are matched by
    document, place and text.
    """
    by_piece: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for docket in dockets:
        for part in docket.parts:
            by_piece[(part.document, part.where, part.text)].add(docket.docket)
    mixed: set[str] = set()
    for group in by_piece.values():
        forms = {_is_application(d) for d in group}
        if len(forms) > 1:
            mixed |= group
    return mixed


def _stamp_order_day(
    day: date,
    refs: Sequence[order_lineups.OrderDocumentRef],
    members: Sequence[OutcomeTarget],
    numbers: Mapping[str, str],
    fetcher: order_lineups.OrderFetcher,
    result: VoteWriteResult,
    *,
    replace_differing: bool,
) -> None:
    """Read every document listed for one order date and file each outcome resolved on it."""
    documents = [fetcher.document(ref.url, ref) for ref in refs]
    covers = all(d.text is not None and not d.truncated for d in documents)
    reading = order_lineups.read_documents(documents, day=day, covers_the_day=covers)
    dockets = {d.docket: d for d in reading.dockets}
    mixed = _shared_across_stages(reading.dockets)
    for target in members:
        number = numbers.get(target.case_id)
        if number is None:
            result.skipped.append((target.ref, "the corpus holds no docket number"))
            continue
        found = dockets.get(number)
        if found is None:
            result.skipped.append(
                (target.ref, f"not named in the date's documents: {number} on {day}")
            )
            continue
        record, why = order_record(found, shared_across_stages=number in mixed)
        if record is not None:
            _classify(target, record, result, replace_differing=replace_differing)
        elif why is None:
            result.skipped.append(
                (target.ref, "nothing observed: no noted vote, writings not complete")
            )
        else:
            result.held_back.append((target.ref, why))


def stamp_order_votes(
    conn: ReadConnection,
    data_root: Path,
    fetcher: order_lineups.OrderFetcher,
    *,
    today: date,
    terms: Sequence[int] = ORDER_VOTE_TERMS,
    apply: bool,
    max_stamps: int | None = None,
    replace_differing: bool = False,
) -> VoteWriteResult:
    """Stamp cert and interim outcomes with their disposing order's notations and writings."""
    result = VoteWriteResult(source=SUPREMECOURT_ORDERS, applied=apply)
    wanted = frozenset(terms)
    targets = _targets(
        data_root,
        stages=frozenset({Stage.cert.value, Stage.interim.value}),
        keep=lambda day: _term(day) in wanted,
    )
    result.population = len(targets)
    numbers = docket_numbers(conn, (t.case_id for t in targets))
    by_term: dict[int, dict[date, list[OutcomeTarget]]] = defaultdict(lambda: defaultdict(list))
    for target in targets:
        day = target.outcome.resolved_at
        by_term[_term(day)][day].append(target)
    for term, days in sorted(by_term.items()):
        yy = term % 100
        try:
            listed = fetcher.listed(yy)
        except httpx.HTTPError as exc:
            result.failures.append(f"OT{yy:02d} orders listings: {exc}")
            for members in days.values():
                result.skipped.extend(
                    (t.ref, f"the orders listings could not be read: OT{yy:02d}") for t in members
                )
            continue
        for day, members in sorted(days.items()):
            if (today - day).days < SETTLING_DAYS:
                result.skipped.extend(
                    (t.ref, f"inside the {SETTLING_DAYS}-day settling window: {day}")
                    for t in members
                )
                continue
            refs = [ref for ref in listed if ref.day == day]
            if not refs:
                result.skipped.extend(
                    (t.ref, f"the Court lists no order document for the date: {day}")
                    for t in members
                )
                continue
            _stamp_order_day(
                day, refs, members, numbers, fetcher, result, replace_differing=replace_differing
            )
    return _finish(result, apply=apply, max_stamps=max_stamps)


# --- Shared -------------------------------------------------------------------


def _finish(result: VoteWriteResult, *, apply: bool, max_stamps: int | None) -> VoteWriteResult:
    """Apply the stamps, unless this is a dry run or the bound refuses them.

    Each outcome is re-read from disk and re-validated whole before it is
    written, so a record the model refuses raises before anything is written
    for it.
    """
    if not apply:
        return result
    if result.failures:
        result.refused = True
        result.applied = False
        return result
    if max_stamps is not None and len(result.stamps) > max_stamps:
        result.refused = True
        result.applied = False
        return result
    planned: list[tuple[Path, Outcome]] = []
    for stamp in result.stamps:
        current = read_model(stamp.target.path, Outcome)
        planned.append((stamp.target.path, stamped(current, stamp.record)))
    for path, outcome in planned:
        write_json(path, outcome)
    return result


def reason_counts(entries: Iterable[tuple[str, str]]) -> Mapping[str, int]:
    """How many entries give each reason, with the per-docket detail folded away."""
    counts: dict[str, int] = defaultdict(int)
    for _, reason in entries:
        counts[reason.split(": ", 1)[0]] += 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
