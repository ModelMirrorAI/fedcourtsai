"""Stamp per-Justice vote records onto committed outcomes from the Court's documents.

The writer half of the two registered vote sources
(:mod:`fedcourtsai.pipeline.vote_sources`). The readers are read-only and
already exist — :mod:`fedcourtsai.pipeline.opinion_lineups` for a merits
opinion's syllabus lineup, :mod:`fedcourtsai.pipeline.order_lineups` for the
notations and separate-writing headers of the Court's orders. This module maps
a reading onto the committed ``outcome.json`` it describes and writes
``votes``, ``vote_provenance`` and ``writing_roles`` there, and on a merits
outcome ``merits_author``, and nothing else.

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
  holds the record back. Apart from the lineup, every outcome whose listing
  row is dated its ``resolved_at`` is stamped with ``merits_author``, the
  author code the row prints (a Justice, or ``per-curiam``): the row prints it
  for every decision, signed or per curiam, so which outcomes carry an author
  never depends on who wrote, and a lineup held back or unread leaves an
  author-only stamp. The author is not held to the Granted & Noted
  comparison, which runs only on a lineup the syllabus was read for, a signed
  decision: holding it back there would mask signed decisions a per curiam is
  never masked for.
- :func:`stamp_order_votes` — cert- and interim-stage outcomes resolved from
  :data:`ORDER_VOTE_TERM_FLOOR` through the current October Term
  (:func:`order_vote_terms`). The record is read from every document the Court
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
empty no network request is made at all. The orders pass also runs as a
**standing sweep** (``sweep=``): instead of a maintainer's bound it writes at most
a per-window cap of new records and refuses only a class above a ceiling, which
is how run-seed's daily window stamps each settled order list without a dispatch.

**Split across a credential boundary.** On run-repair the pass runs as three
jobs, so the step parsing the Court's documents holds no credential: a
read-only job writes :class:`VoteDocketNumbers` (the only corpus fact the
writer reads, :func:`vote_docket_numbers`); a credential-free job reads the
documents against that projection and writes a :class:`VoteStampPlan`
(:func:`vote_plan`); and on an apply a writer job re-validates every planned
record against the ledger it is about to write and stamps it
(:func:`apply_vote_plan`), reading no corpus and fetching nothing. Run in one
process — a dev checkout over a pulled corpus — the same functions compose as
they always have.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Annotated, Final, Literal

import httpx
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)

from .corpus import ReadConnection
from .handoff import HandoffRefused
from .pipeline import granted_noted, moments, opinion_lineups, order_lineups
from .pipeline.base_rates import PER_CURIAM_LABEL
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

#: The first October Term the order-list pass reads. OT2024 and OT2025 sat the
#: same nine-Justice bench and both grammars were checked against real OT2025
#: orders; every interim outcome in the ledger as of 2026-09-30 is among them.
ORDER_VOTE_TERM_FLOOR: Final = 2024


def order_vote_terms(today: date) -> tuple[int, ...]:
    """The October Terms the order-list pass reads ``today``: the floor through the current one.

    The current Term is included so that its orders are stamped as they settle,
    which is what the standing sweep is for. A Term whose orders the reader has
    not yet seen is protected the way every reading is: the notation grammar
    makes a name off the bench, an object it does not read and any leftover
    sentence shaped like a Justice's act a problem, and a docket with a problem
    is held back rather than stamped, so a new phrasing shows as a held-back
    count rather than a wrong record. A notation that names no Justice's act at
    all is beyond that guard and reads as none. Nothing scores these records.
    """
    return tuple(range(ORDER_VOTE_TERM_FLOOR, october_term_year(today) + 1))


#: Days after an order date before its writings are read as complete. A writing
#: respecting an order is ordinarily published with it, but not always, and a
#: Justice observed to have written nothing must not merely not have written yet.
SETTLING_DAYS: Final = 7

_NOT_SITTING: Final = frozenset({VoteValue.recused, VoteValue.did_not_participate})
_TERM_DOCKET_RE: Final = re.compile(r"\b\d{2}-\d+\b")
_APPLICATION_RE: Final = re.compile(r"^\d{2}A\d+$")


@dataclass(frozen=True)
class VoteRecord:
    """What one reading would stamp onto an outcome.

    Two parts, either of which may be absent: the vote part (``votes``,
    ``provenance``, ``writing_roles``), present only where a whole lineup was
    read, and the opinions pass's ``merits_author``, read off the listing row
    for every decision it finds. A record carries at least one.
    """

    votes: tuple[JusticeVote, ...]
    provenance: VoteProvenance | None
    writing_roles: tuple[JusticeWriting, ...] | None
    merits_author: str | None = None


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


@dataclass(frozen=True)
class SweepSlice:
    """A standing sweep's two instruments, in place of a maintainer's bound.

    ``cap`` is a **slice**: a window writes at most this many records, oldest
    order date first, and leaves the rest for the next window. ``ceiling``
    **refuses**: a class found larger than it is written not at all, because a
    class that size is a widened population rather than a backlog to drain.
    """

    cap: int
    ceiling: int

    def __post_init__(self) -> None:
        if self.cap < 1 or self.ceiling < self.cap:
            raise ValueError(f"a sweep needs 1 <= cap <= ceiling, got {self.cap}/{self.ceiling}")


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
    #: On a sweep, the records found past the window's cap, left for the next one.
    deferred: int = 0
    #: ``(ref, reason)``: a record carrying the author alone, and why no vote part was
    #: read; a vote part held back is filed under ``held_back`` instead.
    votes_unread: list[tuple[str, str]] = field(default_factory=list)


def _votes_blank(outcome: Outcome) -> bool:
    return outcome.vote_provenance is None and not outcome.votes and outcome.writing_roles is None


def _votes_same(outcome: Outcome, record: VoteRecord) -> bool:
    return (
        outcome.vote_provenance == record.provenance
        and list(outcome.votes) == list(record.votes)
        and (outcome.writing_roles is None) == (record.writing_roles is None)
        and list(outcome.writing_roles or ()) == list(record.writing_roles or ())
    )


def _same(outcome: Outcome, record: VoteRecord) -> bool:
    """Whether every part ``record`` carries is already on ``outcome``."""
    return (record.provenance is None or _votes_same(outcome, record)) and (
        record.merits_author is None or outcome.merits_author == record.merits_author
    )


def _fillable(outcome: Outcome, record: VoteRecord) -> bool:
    """Whether each part ``record`` carries is blank on ``outcome`` or already the same."""
    votes = record.provenance is None or _votes_blank(outcome) or _votes_same(outcome, record)
    author = record.merits_author is None or outcome.merits_author in (None, record.merits_author)
    return votes and author


def _differing(outcome: Outcome, record: VoteRecord) -> str:
    """Which part of ``outcome`` keeps ``record`` from filling it."""
    votes = record.provenance is not None and not (
        _votes_blank(outcome) or _votes_same(outcome, record)
    )
    author = record.merits_author is not None and outcome.merits_author not in (
        None,
        record.merits_author,
    )
    return " and ".join(
        part for part, differs in (("vote record", votes), ("merits author", author)) if differs
    )


def stamped(outcome: Outcome, record: VoteRecord) -> Outcome:
    """``outcome`` with the parts ``record`` carries written, validated whole.

    Raises ``pydantic.ValidationError`` on a record the model refuses.
    """
    payload = outcome.model_dump(mode="json")
    if record.provenance is not None:
        payload["votes"] = [v.model_dump(mode="json") for v in record.votes]
        payload["vote_provenance"] = record.provenance.model_dump(mode="json")
        payload["writing_roles"] = (
            None
            if record.writing_roles is None
            else [r.model_dump(mode="json") for r in record.writing_roles]
        )
    if record.merits_author is not None:
        payload["merits_author"] = record.merits_author
    return Outcome.model_validate(payload)


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
    if _fillable(outcome, record):
        result.stamps.append(VoteStamp(target, record))
    elif replace_differing:
        result.stamps.append(VoteStamp(target, record, replaces=True))
    else:
        result.held_back.append(
            (
                target.ref,
                f"carries a different {_differing(outcome, record)}; "
                "pass replace-differing to replace it",
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


#: Where a pass reads each case's docket number from: the corpus, or the
#: public projection of it a read-only job wrote (:class:`VoteDocketNumbers`).
DocketNumbers = ReadConnection | Mapping[str, str]


def _numbers_for(source: DocketNumbers, case_ids: Iterable[str]) -> Mapping[str, str]:
    if isinstance(source, Mapping):
        return source
    return docket_numbers(source, case_ids)


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


def _listing_row(
    number: str,
    listing: Sequence[opinion_lineups.OpinionListing],
    entry: granted_noted.GrantedNotedEntry | None,
) -> tuple[opinion_lineups.OpinionListing | None, str | None, bool]:
    """The one listing row deciding ``number``, or why none and whether that is a hold-back.

    The docket's own row where the listing prints one; a consolidated group's
    row only where the docket has none of its own. Either way exactly one
    opinion, or the record is held back: a group-mate's opinion must never
    stand in for one the listing prints for this docket.
    """
    group = set(entry.dockets) if entry is not None else {number}
    own = [row for row in listing if number in _listed_dockets(row)]
    rows = own or [row for row in listing if _listed_dockets(row) & group]
    if not rows:
        return None, f"no opinion on the listing names the docket: {number}", False
    if len({row.url for row in rows}) > 1:
        return None, f"several opinions on the listing name the docket: {number}", True
    return rows[0], None, False


def listed_author(row: opinion_lineups.OpinionListing) -> str | None:
    """The deciding opinion's author as the listing row prints it, or ``None`` off the roster.

    A Justice's roster name, or ``per-curiam`` for the per curiam code.
    """
    if row.author_code == opinion_lineups.PER_CURIAM_CODE:
        return PER_CURIAM_LABEL
    return opinion_lineups.LISTING_AUTHOR_CODES.get(row.author_code)


def _with_author(
    target: OutcomeTarget,
    row: opinion_lineups.OpinionListing | None,
    record: VoteRecord | None,
) -> VoteRecord | None:
    """``record`` with the listing row's author added, where the row decides the outcome.

    The author is read off the row alone, so it is stamped for every decision
    the listing prints, signed or per curiam, whether or not its lineup was
    read: which outcomes carry it never depends on who wrote. Only a row
    dated the outcome's own ``resolved_at`` names its author.
    """
    author = (
        listed_author(row)
        if row is not None and row.decided == target.outcome.resolved_at
        else None
    )
    if author is None:
        return record
    if record is None:
        return VoteRecord((), None, None, merits_author=author)
    return VoteRecord(record.votes, record.provenance, record.writing_roles, merits_author=author)


def _opinion_target(
    target: OutcomeTarget,
    number: str | None,
    listing: Sequence[opinion_lineups.OpinionListing],
    entries: Mapping[str, granted_noted.GrantedNotedEntry],
    fetcher: opinion_lineups.OpinionFetcher,
    readings: dict[str, opinion_lineups.OpinionLineupReading],
) -> tuple[VoteRecord | None, str | None, bool]:
    """One merits outcome's record, or why none and whether that is a hold-back.

    The vote part comes from the opinion's lineup, the author from the listing
    row (:func:`_with_author`); the reason and hold-back describe the vote part
    and stand only where neither part was read. ``readings`` caches one reading
    per opinion URL across a Term, since a consolidated case's dockets share an
    opinion.
    """
    if number is None:
        return None, "the corpus holds no docket number", False
    row, why, held = _listing_row(number, listing, entries.get(number))
    record, why, held = (
        (None, why, held)
        if row is None
        else _row_votes(target, row, entries.get(number), fetcher, readings)
    )
    return _with_author(target, row, record), why, held


def _row_votes(
    target: OutcomeTarget,
    row: opinion_lineups.OpinionListing,
    entry: granted_noted.GrantedNotedEntry | None,
    fetcher: opinion_lineups.OpinionFetcher,
    readings: dict[str, opinion_lineups.OpinionLineupReading],
) -> tuple[VoteRecord | None, str | None, bool]:
    """The vote part one listing row yields for ``target``, or why none."""
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


def _opinion_targets(data_root: Path) -> list[OutcomeTarget]:
    """The merits pass's population: merits outcomes resolved from the floor Term on."""
    return _targets(
        data_root,
        stages=frozenset({Stage.merits.value}),
        keep=lambda day: _term(day) >= OPINION_VOTE_TERM_FLOOR,
    )


def stamp_opinion_votes(
    conn: DocketNumbers,
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
    ``conn`` is the corpus, or the docket-number projection of it.
    """
    result = VoteWriteResult(source=SUPREMECOURT_OPINIONS, applied=apply)
    targets = _opinion_targets(data_root)
    result.population = len(targets)
    numbers = _numbers_for(conn, (t.case_id for t in targets))
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
                if record.provenance is None and reason is not None:
                    # The author stamps; the lineup's reason still says why no votes did.
                    (result.held_back if held else result.votes_unread).append((target.ref, reason))
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


def _order_targets(data_root: Path, terms: Sequence[int]) -> list[OutcomeTarget]:
    """The orders pass's population: cert and interim outcomes resolved in ``terms``."""
    wanted = frozenset(terms)
    return _targets(
        data_root,
        stages=frozenset({Stage.cert.value, Stage.interim.value}),
        keep=lambda day: _term(day) in wanted,
    )


def stamp_order_votes(  # noqa: PLR0913 - the pass's inputs, keyword-only beside the two readers
    conn: DocketNumbers,
    data_root: Path,
    fetcher: order_lineups.OrderFetcher,
    *,
    today: date,
    terms: Sequence[int] | None = None,
    apply: bool,
    max_stamps: int | None = None,
    replace_differing: bool = False,
    sweep: SweepSlice | None = None,
) -> VoteWriteResult:
    """Stamp cert and interim outcomes with their disposing order's notations and writings.

    ``conn`` is the corpus, or the docket-number projection of it. ``terms``
    defaults to :func:`order_vote_terms` for ``today``.
    """
    result = VoteWriteResult(source=SUPREMECOURT_ORDERS, applied=apply)
    targets = _order_targets(data_root, order_vote_terms(today) if terms is None else terms)
    result.population = len(targets)
    numbers = _numbers_for(conn, (t.case_id for t in targets))
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
    return _finish(result, apply=apply, max_stamps=max_stamps, sweep=sweep)


# --- Shared -------------------------------------------------------------------


def _finish(
    result: VoteWriteResult,
    *,
    apply: bool,
    max_stamps: int | None,
    sweep: SweepSlice | None = None,
) -> VoteWriteResult:
    """Apply the stamps, unless this is a dry run or the bound refuses them.

    On a sweep the cap slices the class first — oldest order date first, then
    by outcome, so successive windows drain it in a fixed order — and the
    ceiling stands in for the bound: a whole class above it refuses. A sweep
    never replaces a record; its caller refuses ``replace_differing``.

    Each outcome is re-read from disk and re-validated whole before it is
    written, so a record the model refuses raises before anything is written
    for it.
    """
    if sweep is not None:
        if any(stamp.replaces for stamp in result.stamps):
            raise ValueError("a sweep never replaces a record; replace_differing is dispatch-only")
        found = len(result.stamps)
        if apply and found > sweep.ceiling:
            result.refused = True
            result.applied = False
            result.deferred = found
            result.stamps = []
            return result
        ordered = sorted(
            result.stamps, key=lambda stamp: (stamp.target.outcome.resolved_at, stamp.target.ref)
        )
        result.stamps = ordered[: sweep.cap]
        result.deferred = found - len(result.stamps)
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


# --- The handoff: projection, plan, apply ----------------------------------------

VoteSourceName = Literal["supremecourt-opinions", "supremecourt-orders"]

_CaseId = Annotated[str, StringConstraints(pattern=r"^scotus/[0-9]{1,12}$")]
_EventId = Annotated[str, StringConstraints(pattern=r"^evt-[a-z0-9-]{1,80}$")]
#: A docket number as :func:`docket_numbers` prints it (``24-43``, ``25A443``,
#: an original's ``22O141`` or ``141, ORIG.``): bounded, and no character a
#: shell or a Markdown summary reads specially.
_DOCKET_NUMBER_RE: Final = re.compile(r"^[0-9A-Z][0-9A-Z.,\- ]{0,31}$")
_DocketNumber = Annotated[str, StringConstraints(pattern=_DOCKET_NUMBER_RE.pattern)]
#: A merits author as the listing names one: a roster Justice, or the per curiam label.
_Author = Literal[
    "per-curiam",
    "Roberts",
    "Kennedy",
    "Thomas",
    "Ginsburg",
    "Breyer",
    "Alito",
    "Sotomayor",
    "Kagan",
    "Gorsuch",
    "Kavanaugh",
    "Barrett",
    "Jackson",
]

#: The largest population or plan either pass could plausibly carry; a file
#: past it is refused before any row is read.
_MAX_ROWS: Final = 50_000


class VoteDocketNumbers(BaseModel):
    """The one corpus fact the vote writer reads, projected for the parse job.

    Each population case's docket number, keyed by its ledger case id. Both
    halves are public: the case id is the key every committed ``data/`` path
    already carries, and the docket number is the identifier the Court itself
    assigned and prints on every order and opinion — the same pair the qp-topic
    artifacts and the release dataset publish (``docs/data-sources.md``,
    *What we redistribute*). No other corpus column crosses.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/vote-docket-numbers"] = "fedcourts/vote-docket-numbers"
    version: Literal[1] = 1
    source: VoteSourceName
    numbers: dict[_CaseId, _DocketNumber] = Field(max_length=_MAX_ROWS)
    unprojected: int = Field(
        default=0,
        ge=0,
        description="Population cases whose stored number is not in the plain printed form "
        "(an annotated spelling) and so is left out; the parse files them as having none",
    )


class PlannedVoteStamp(BaseModel):
    """One record the parse job read for one outcome: what the writer would stamp.

    Public by construction: the ledger keys and the fields the writer commits
    to public git, each read off a Court order or opinion. The vote part
    (``votes``, ``vote_provenance``, ``writing_roles``) and the opinions pass's
    ``merits_author`` are each optional, and a stamp carries at least one.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    case_id: _CaseId
    event_id: _EventId
    resolved_at: date = Field(description="The outcome's resolved_at the record was read for")
    replaces: bool = Field(description="The outcome carried a different record when planned")
    votes: list[JusticeVote] = Field(default_factory=list, max_length=20)
    vote_provenance: VoteProvenance | None = None
    writing_roles: list[JusticeWriting] | None = Field(default=None, max_length=20)
    merits_author: _Author | None = None

    @model_validator(mode="after")
    def _carries_a_part(self) -> PlannedVoteStamp:
        if self.vote_provenance is None and self.merits_author is None:
            raise ValueError("a planned stamp carries neither a vote record nor an author")
        if self.vote_provenance is None and (self.votes or self.writing_roles is not None):
            raise ValueError("votes or writing roles with no vote_provenance")
        return self


class VoteStampPlan(BaseModel):
    """What one pass's parse would stamp: the file the writer job applies.

    ``failures`` carries forward every listing or list the parse could not
    read, so an apply of a plan read from a partial fetch is refused exactly
    as a one-process apply is.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    format: Literal["fedcourts/vote-stamp-plan"] = "fedcourts/vote-stamp-plan"
    version: Literal[2] = 2
    source: VoteSourceName
    population: int = Field(ge=0, le=_MAX_ROWS)
    failures: list[
        Annotated[str, StringConstraints(max_length=500, pattern=r"^[^\x00-\x1f]*$")]
    ] = Field(max_length=100)
    stamps: list[PlannedVoteStamp] = Field(max_length=_MAX_ROWS)


def _terms_for(terms: Sequence[int] | None, today: date | None) -> Sequence[int]:
    if terms is not None:
        return terms
    return order_vote_terms(today if today is not None else datetime.now(UTC).date())


def _population(
    source: VoteSourceName, data_root: Path, terms: Sequence[int]
) -> list[OutcomeTarget]:
    if source == SUPREMECOURT_OPINIONS:
        return _opinion_targets(data_root)
    return _order_targets(data_root, terms)


def vote_docket_numbers(
    conn: ReadConnection,
    data_root: Path,
    *,
    source: VoteSourceName,
    terms: Sequence[int] | None = None,
    today: date | None = None,
) -> VoteDocketNumbers:
    """The docket-number projection of the corpus for one pass's population.

    ``terms`` defaults to :func:`order_vote_terms` for ``today`` (the current UTC
    date when that is omitted too).
    """
    targets = _population(source, data_root, _terms_for(terms, today))
    numbers = docket_numbers(conn, (t.case_id for t in targets))
    carried = {k: v for k, v in numbers.items() if _DOCKET_NUMBER_RE.match(v)}
    return VoteDocketNumbers(
        source=source, numbers=carried, unprojected=len(numbers) - len(carried)
    )


def projected_numbers(projection: VoteDocketNumbers, source: VoteSourceName) -> dict[str, str]:
    """The projection's map, refused when it was written for the other pass."""
    if projection.source != source:
        raise HandoffRefused(
            f"the docket-number projection was written for {projection.source}, not {source}"
        )
    return dict(projection.numbers)


def vote_plan(result: VoteWriteResult) -> VoteStampPlan:
    """A dry run's stamps as the plan a writer job applies."""
    return VoteStampPlan(
        source=SUPREMECOURT_OPINIONS
        if result.source == SUPREMECOURT_OPINIONS
        else SUPREMECOURT_ORDERS,
        population=result.population,
        failures=[" ".join(failure.split())[:500] for failure in result.failures[:100]],
        stamps=[
            PlannedVoteStamp(
                case_id=stamp.target.case_id,
                event_id=stamp.target.event_id,
                resolved_at=stamp.target.outcome.resolved_at,
                replaces=stamp.replaces,
                votes=list(stamp.record.votes),
                vote_provenance=stamp.record.provenance,
                writing_roles=(
                    None if stamp.record.writing_roles is None else list(stamp.record.writing_roles)
                ),
                merits_author=stamp.record.merits_author,
            )
            for stamp in result.stamps
        ],
    )


def _plan_problem(  # noqa: PLR0911 - one return per reason a planned stamp is refused
    planned: PlannedVoteStamp, target: OutcomeTarget | None, source: VoteSourceName, today: date
) -> str | None:
    """Why a planned stamp cannot have come from an honest parse of this ledger."""
    if target is None:
        return "names no outcome in the pass's population"
    if planned.merits_author is not None and source != SUPREMECOURT_OPINIONS:
        return f"carries a merits author on the {source} pass, which reads none"
    provenance = planned.vote_provenance
    if provenance is None:
        return None
    if provenance.source != source:
        return f"carries a {provenance.source} record on the {source} pass"
    if source == SUPREMECOURT_ORDERS:
        if provenance.complete:
            return "claims a complete bench from the orders source, whose records are partial"
        if (today - planned.resolved_at).days < SETTLING_DAYS:
            return f"was read inside the {SETTLING_DAYS}-day settling window"
    elif not provenance.complete:
        return "carries a partial record from the opinions source, whose records are whole"
    return None


def apply_vote_plan(  # noqa: PLR0913 - the plan, the ledger and the write's keyword-only controls
    plan: VoteStampPlan,
    data_root: Path,
    *,
    source: VoteSourceName,
    today: date,
    terms: Sequence[int] | None = None,
    apply: bool,
    max_stamps: int | None = None,
    replace_differing: bool = False,
    sweep: SweepSlice | None = None,
) -> VoteWriteResult:
    """Re-validate a plan against the ledger it is about to write, then stamp it.

    The plan is untrusted input: it was written by a job that parsed
    third-party documents. Every planned stamp must name an outcome in this
    pass's population as the ledger stands now, appear once, carry a record
    of this pass's source and shape, and pass the same model and registration
    checks a one-process run applies (:func:`_conformance`); any departure
    refuses the whole plan with :class:`HandoffRefused` before anything is
    written. What moved honestly since the plan was read is filed as a
    one-process run files it: the same record already present is
    ``unchanged``, a different one present is held back unless
    ``replace_differing``, and an outcome whose ``resolved_at`` moved is held
    back. The bound and the carried-forward failures then refuse an apply
    exactly as :func:`_finish` does. Reads no corpus and makes no request.
    """
    if plan.source != source:
        raise HandoffRefused(f"the plan was written for {plan.source}, not {source}")
    population = _population(source, data_root, _terms_for(terms, today))
    by_ref = {target.ref: target for target in population}
    # The writer's own population, not the plan's word for it.
    result = VoteWriteResult(source=source, applied=apply, population=len(population))
    result.failures.extend(plan.failures)
    seen: set[str] = set()
    for planned in plan.stamps:
        ref = f"{planned.case_id}/{planned.event_id}"
        if ref in seen:
            raise HandoffRefused(f"the plan stamps {ref} twice")
        seen.add(ref)
        target = by_ref.get(ref)
        if (why := _plan_problem(planned, target, source, today)) is not None:
            raise HandoffRefused(f"the plan's stamp for {ref} {why}")
        assert target is not None  # _plan_problem refuses a missing target
        if planned.resolved_at != target.outcome.resolved_at:
            result.held_back.append(
                (
                    ref,
                    "the outcome's resolved_at moved since the plan was read: "
                    f"{planned.resolved_at} against {target.outcome.resolved_at}",
                )
            )
            continue
        record = VoteRecord(
            tuple(planned.votes),
            planned.vote_provenance,
            None if planned.writing_roles is None else tuple(planned.writing_roles),
            merits_author=planned.merits_author,
        )
        if not _same(target.outcome, record) and (why := _conformance(target, record)):
            raise HandoffRefused(f"the plan's stamp for {ref} fails the ledger's check: {why}")
        _classify(target, record, result, replace_differing=replace_differing)
    return _finish(result, apply=apply, max_stamps=max_stamps, sweep=sweep)
