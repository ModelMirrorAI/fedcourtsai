"""The merits decision record: when a granted case was argued, and how it was decided.

The merits pair (``merits_judgment`` / ``merits_decided``, :mod:`.judgment`)
says *what* the Court did to the judgment below, over the population whose grant
opens a merits proceeding. A Term's decision record needs two facts beside it,
over **every** granted row — the GVRs and summary reversals included, since a
Term index counts the cases decided without argument as well as the argued ones:

- **when the case was argued** (``merits_argued``), the date of the docket's last
  argument entry on or after the grant (:func:`~.merits_signals.argued_date`);
- **how it was decided** (``merits_decision_method``, a
  :class:`~fedcourtsai.schemas.MeritsDecisionMethod`), read from the same last
  judgment-shaped entry the merits pair is parsed from, the grant date, and the
  argued date (:func:`decision_method`).

What happened to the judgment below needs no third column. It is the merits
judgment where one is latched, and on a row whose disposition rides the cert
order it is the label's own meaning — a GVR vacates, a summary reversal reverses
(:func:`decision_judgment`). So the record carries one disposition vocabulary,
:class:`~fedcourtsai.schemas.Judgment`, and the stat-pack labels are projections
of the pair: a GVR is a summary method beside ``vacated``, a GRR or summary
reversal a summary method beside ``reversed``.

Two writers fill the columns through the functions here, so the reading is
single-sourced: the live poll at ingest (:func:`fedcourtsai.pipeline.ingest.map_live_docket`)
and :func:`backfill_decision_record`, which re-reads each unclassified granted
row's newest stored live-shaped snapshot. Neither writer ever clears a reading:
the live upsert lets a fresh non-null reading replace the stored one (a
reargument, a decision landing on a pending case), while the back-fill only
fills a NULL and never overwrites.

**This is where the historical merits decision record lives**: corpus-side, on
the case row. No outcome is written to the git ledger for a case the pipeline
never forecast, so the prediction ledger holds only what was actually
forecast, and a reader of the historical record — a stat-pack figure, a
per-Justice vote writer — would target these rows.

**Nothing a cell sees reads these columns.** They are withheld from the
retrieval surface (:data:`fedcourtsai.corpus.RETRIEVAL_WITHHELD_COLUMNS`), no
outcome, mint, or provisioning gate reads them, and the merits pair they sit
beside is untouched. :func:`decision_census` is their reader: a read-only count
per October Term.
"""

from __future__ import annotations

import sqlite3
from collections import Counter
from collections.abc import Mapping
from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..config import require_sweep_slice
from ..schemas import (
    CERT_ORDER_DISPOSITIONS,
    GRANTED_DISPOSITIONS,
    Disposition,
    Judgment,
    MeritsDecisionMethod,
)
from ..supremecourt import october_term_year
from .cert_signals import proceedings_entries
from .judgment import (
    JudgmentEntry,
    judgment_rode_the_grant_order,
    last_judgment_entry_text,
    per_curiam_opinion,
    signed_opinion,
)
from .merits_signals import argued_date
from .prefetch import prefetch_by_case

_CERT_ORDER_VALUES = frozenset(d.value for d in CERT_ORDER_DISPOSITIONS)
_GRANTED_VALUES = frozenset(d.value for d in GRANTED_DISPOSITIONS)
_GRANTED_SQL = ", ".join(f"'{v}'" for v in sorted(_GRANTED_VALUES))

#: What a cert-order label says about the judgment below, where the label alone
#: decides it: a GVR vacates and a summary reversal reverses, in the order that
#: grants the petition.
_LABEL_JUDGMENT: dict[str, Judgment] = {
    Disposition.gvr.value: Judgment.vacated,
    Disposition.summary_reversal.value: Judgment.reversed,
}


def decision_method(  # noqa: PLR0911 - one return per rule in the docstring
    *,
    disposition: str | None,
    granted_on: date | None,
    argued: date | None,
    entry: JudgmentEntry | None,
) -> MeritsDecisionMethod | None:
    """How a granted case was decided, or ``None`` where the record cannot say.

    ``entry`` is the docket's last judgment-shaped entry
    (:func:`~.judgment.last_judgment_entry_text`), ``argued`` the argued date
    (:func:`~.merits_signals.argued_date`). The rules, in order:

    1. No grant, or no judgment-shaped entry: ``None`` — pending, terminated
       without a disposition, or a decision this reader cannot see.
    2. A DIG is ``dig`` whether or not the case was argued; the argued date
       beside it says which.
    3. A decision that rode the cert order — a cert-order label (GVR, summary
       reversal), or a judgment dated on or before the grant
       (:func:`~.judgment.judgment_rode_the_grant_order`, which catches the
       summary reversal recorded as plain ``granted``) — is ``summary-opinion``
       where the entry carries an opinion, signed or per curiam, and
       ``summary-order`` where it does not (the ordinary GVR).
    4. An argued case is ``argued-per-curiam`` where the entry notes its own
       opinion as per curiam or the judgment is an affirmance by an equally
       divided Court — checked first, because "Opinion per curiam." is the
       Court stating its own form while a separate writing can also be
       recited as a Justice delivering an opinion — and ``argued-signed``
       where a named Justice delivered the opinion of the Court. An argued
       case whose entry recites neither is ``None``.
    5. A case decided after its grant without argument is ``summary-opinion``
       where the opinion is per curiam, else ``None``. A *signed* opinion with
       no argument entry is ``None`` rather than a summary: it almost always
       means the argument entry was missed (a payload gap, or a spelling the
       argument reader does not anchor on), and the dry run's unplaced residue
       is where that belongs, not a confident wrong method. An entry both
       signed and per curiam is refused here too, where rule 4 lets the per
       curiam notation win: with no argument on the record there is no
       anchor to say which recital is the Court's.

    Conservative in the same direction as the judgment parser: an entry this
    reader cannot place stays unclassified rather than guessed.
    """
    if granted_on is None or entry is None:
        return None
    if entry.judgment is Judgment.dig:
        return MeritsDecisionMethod.dig
    signed = signed_opinion(entry.text)
    per_curiam = per_curiam_opinion(entry.text)
    rode_the_order = disposition in _CERT_ORDER_VALUES or (
        entry.decided is not None and judgment_rode_the_grant_order(entry.decided, granted_on)
    )
    if rode_the_order:
        if signed or per_curiam:
            return MeritsDecisionMethod.summary_opinion
        return MeritsDecisionMethod.summary_order
    if argued is not None and (entry.decided is None or argued <= entry.decided):
        if per_curiam or entry.judgment is Judgment.equally_divided:
            return MeritsDecisionMethod.argued_per_curiam
        if signed:
            return MeritsDecisionMethod.argued_signed
        return None
    if per_curiam and not signed:
        return MeritsDecisionMethod.summary_opinion
    return None


class DecisionRecord(BaseModel):
    """The two decision-record readings one docket payload yields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    argued: date | None = Field(default=None, description="The argued date, or None")
    method: MeritsDecisionMethod | None = Field(
        default=None, description="How the case was decided, or None when unclassified"
    )


def read_decision_record(
    payload: Mapping[str, Any], *, disposition: str | None, granted_on: date | None
) -> DecisionRecord:
    """Both readings off one docket payload — the single entry point both writers call.

    Empty unless the docket carries a grant date **and** a granted label, the
    population every reader of the columns (the back-fill, the census) keys on.
    """
    if granted_on is None or disposition not in _GRANTED_VALUES:
        return DecisionRecord()
    argued = argued_date(payload, granted_on=granted_on)
    method = decision_method(
        disposition=disposition,
        granted_on=granted_on,
        argued=argued,
        entry=last_judgment_entry_text(payload),
    )
    return DecisionRecord(argued=argued, method=method)


def decision_judgment(row: corpus.CorpusRow) -> Judgment | None:
    """What the Court did to the judgment below, in the one :class:`Judgment` vocabulary.

    The latched merits judgment where there is one; else, on a row whose
    cert-order label decides it, the label's own meaning (a GVR vacates, a
    summary reversal reverses); else ``None``. A stored value outside the
    vocabulary reads as ``None`` rather than failing the row, the blob-tolerant
    reading every TEXT enum column gets.
    """
    if row.merits_judgment is not None:
        try:
            return Judgment(row.merits_judgment)
        except ValueError:
            return None
    return _LABEL_JUDGMENT.get(row.disposition or "")


def decision_date(row: corpus.CorpusRow) -> date | None:
    """When the case was decided: the merits judgment's date, else a cert-order label's grant."""
    if row.merits_decided is not None:
        return row.merits_decided
    if row.disposition in _CERT_ORDER_VALUES:
        return row.date_cert_granted
    return None


def decision_term(row: corpus.CorpusRow) -> int | None:
    """The October Term a granted case belongs to in a Term index, or ``None`` if pending.

    The Term it was argued in where it was argued, else the Term it was decided
    in — the axis a Term's merits statistics are cut on, which is not the
    docket-number prefix: a 24- docket granted after the January cutoff is
    argued and decided in the Term its 25- neighbours are, so a docket-prefix
    cut splits one Term's decisions across two rows. Nor is it the statpack
    merits section's axis, which is the **grant** Term.
    """
    anchor = row.merits_argued or decision_date(row)
    return october_term_year(anchor) if anchor is not None else None


# --- the back-fill -------------------------------------------------------------

# Every granted modern cert docket in the live slice whose decision is not yet
# classified and that is not known to have terminated without one. A classified
# row never comes back: an argued date precedes the decision it sits beside, so
# once the method is read both columns are final. An undecided grant stays
# selected until its decision lands — the population is the pending docket plus
# the residue the reader cannot place, both visible in the dry run.
_REVISIT_SQL = (
    f"court = 'scotus' AND {corpus.LIVE_SLICE_SQL} AND date_cert_granted IS NOT NULL "
    f"AND disposition IN ({_GRANTED_SQL}) "
    "AND merits_decision_method IS NULL AND merits_terminated IS NULL"
)


class DecisionFill(BaseModel):
    """What one row gains: only the readings the row does not already carry."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    argued: date | None = None
    method: MeritsDecisionMethod | None = None


class DecisionBackfillResult(BaseModel):
    """What one decision-record back-fill did (or would do on a dry run)."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the corpus (False = dry-run)")
    candidates: int = Field(default=0, ge=0, description="Rows the revisit predicate selected")
    no_snapshot: int = Field(
        default=0, ge=0, description="Candidates with no stored live-shaped snapshot to read"
    )
    no_proceedings: int = Field(
        default=0, ge=0, description="Candidates whose snapshot discloses no proceedings list"
    )
    unchanged: int = Field(
        default=0,
        ge=0,
        description="Candidates read with nothing new to fill — mostly the pending "
        "docket, which stays a candidate until its decision lands",
    )
    filled: list[DecisionFill] = Field(default_factory=list)
    methods: dict[str, int] = Field(
        default_factory=dict,
        description="The method distribution over the fills, MeritsDecisionMethod -> rows",
    )
    refused: bool = Field(
        default=False,
        description="Apply was asked for but the fills exceed the bound; nothing written",
    )
    deferred: int = Field(
        default=0,
        ge=0,
        description="Fillable rows past the per-run slice (`limit`), left for a later "
        "run; `filled` plus this is every row the read found something to fill on",
    )


def backfill_decision_record(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    max_fills: int | None = None,
    limit: int | None = None,
    ceiling: int | None = None,
) -> DecisionBackfillResult:
    """Read each unclassified granted row's newest live snapshot for its decision record.

    The offline twin of the ingest-time reading, over the same pure functions.
    Fill-in only — a row gains a reading where its column is NULL, and a stored
    one is never overwritten — so the pass converges and a re-run over an
    unchanged corpus fills nothing. ``max_fills`` is the blast-radius bound:
    over it nothing is written and ``refused`` is set. Dry-run unless ``apply``.

    ``limit`` is the standing sweep's per-window slice, a different instrument:
    every candidate is still read, but only the first ``limit`` fills in
    ``case_id`` order are the plan, the rest counted in ``deferred`` rather than
    refused. A filled column is never overwritten and a classified row leaves the
    candidates, so successive slices drain the class.

    ``ceiling`` is the sweep's own refusal, read against the whole class before
    the slice: an apply that finds more than ``ceiling`` writes nothing and sets
    ``refused``, because a class that size is a widened predicate rather than a
    backlog for successive slices to drain.

    The sweep passes ``limit`` and ``ceiling`` without a blast-radius bound (the
    command refuses the mix). A code caller passing both a slice and a bound gets
    the slice first and the bound checked against it, so the bound refuses only a
    slice larger than itself.

    Like its ``set_*`` siblings the write is a direct ``UPDATE`` of the index and
    never the casestore mirror.
    """
    require_sweep_slice(limit, ceiling)
    result = DecisionBackfillResult(applied=apply)
    records = conn.execute(
        "SELECT case_id, disposition, date_cert_granted, merits_argued FROM cases "
        f"WHERE {_REVISIT_SQL} ORDER BY case_id"
    ).fetchall()
    rows = [
        (
            str(record[0]),
            str(record[1]) if record[1] is not None else None,
            date.fromisoformat(str(record[2])),
            record[3] is not None,
        )
        for record in records
    ]
    result.candidates = len(rows)
    methods: Counter[str] = Counter()
    with prefetch_by_case(
        [case_id for case_id, *_ in rows],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="decision-backfill",
    ) as fetched:
        for (case_id, disposition, granted_on, had_argued), (_, snapshot) in zip(
            rows, fetched, strict=True
        ):
            if snapshot is None:
                result.no_snapshot += 1
                continue
            payload = snapshot[1]
            if not proceedings_entries(payload):
                result.no_proceedings += 1
                continue
            reading = read_decision_record(payload, disposition=disposition, granted_on=granted_on)
            fill = DecisionFill(
                case_id=case_id,
                argued=None if had_argued else reading.argued,
                method=reading.method,
            )
            if fill.argued is None and fill.method is None:
                result.unchanged += 1
                continue
            result.filled.append(fill)
    # The sweep's refusing guard, checked on the whole class before the slice:
    # a class past ``ceiling`` is a widened predicate, not a backlog to drain.
    if apply and ceiling is not None and len(result.filled) > ceiling:
        result.refused = True
        result.applied = False
    if limit is not None and len(result.filled) > limit:
        result.deferred = len(result.filled) - limit
        del result.filled[limit:]
    for fill in result.filled:
        if fill.method is not None:
            methods[fill.method.value] += 1
    result.methods = dict(sorted(methods.items()))
    if result.refused:
        return result
    if apply and max_fills is not None and len(result.filled) > max_fills:
        result.refused = True
        result.applied = False
        return result
    if not apply:
        return result
    with conn:
        conn.executemany(
            "UPDATE cases SET merits_argued = COALESCE(merits_argued, ?), "
            "merits_decision_method = COALESCE(merits_decision_method, ?) WHERE case_id = ?",
            [
                (
                    fill.argued.isoformat() if fill.argued else None,
                    fill.method.value if fill.method else None,
                    fill.case_id,
                )
                for fill in result.filled
            ],
        )
    return result


# --- the census ----------------------------------------------------------------


class DecisionTermCensus(BaseModel):
    """One October Term's decision record, as the corpus index holds it."""

    model_config = ConfigDict(extra="forbid")

    term: int = Field(description="The October Term (`decision_term`)")
    assigned: int = Field(
        ge=0,
        description="Granted modern cert dockets **assigned** to the Term — argued "
        "in it, or decided in it without an argued date on the row. Not the "
        "grants made in the Term: a pending or terminated grant is in no Term. "
        "Where `merits_argued` is unfilled the Term comes from the decided date, "
        "so `decided` equals `assigned` there by construction and is no evidence "
        "of completeness. One row per docket: a consolidated set counts once per "
        "docket",
    )
    argued: int = Field(ge=0, description="Rows carrying `merits_argued`")
    decided: int = Field(ge=0, description="Rows with a decided date (`decision_date`)")
    order_riding: int = Field(
        ge=0,
        description="Rows whose disposition rode the cert order: a cert-order "
        "label (GVR, summary reversal), or a judgment dated on or before the "
        "grant (`judgment_rode_the_grant_order`). Needs no method column, so the "
        "split holds on Terms whose method is unclassified",
    )
    methods: dict[str, int] = Field(
        description="`merits_decision_method` distribution; `unclassified` = NULL"
    )
    dispositions: dict[str, int] = Field(
        description="`decision_judgment` distribution over every assigned row, "
        "GVRs included; `none` = no disposition read. Not a reversal rate: "
        "read `plenary_dispositions` for that"
    )
    plenary_dispositions: dict[str, int] = Field(
        description="`decision_judgment` distribution over the rows that did "
        "**not** ride the cert order — the argued and plenary docket a stat "
        "pack's affirm/reverse figures are taken over"
    )


class DecisionCensus(BaseModel):
    """The per-Term decision-record census over a range of October Terms."""

    model_config = ConfigDict(extra="forbid")

    terms: list[DecisionTermCensus]
    pending: int = Field(
        ge=0,
        description="Granted rows neither argued nor decided on the record (no "
        "Term to assign) and not marked terminated. Mostly the pending docket, "
        "but a stale grant whose decision the record never read lands here too",
    )
    terminations: dict[str, int] = Field(
        default_factory=dict,
        description="Granted rows carrying `merits_terminated`, by "
        "`MeritsTermination` value — outside every Term row. Not all are docket "
        "facts: `judgment-issued` means the disposition parser missed an entry "
        "that exists, so those are decided cases missing from their Term",
    )


def _rode_the_order(row: corpus.CorpusRow) -> bool:
    """Whether the row's disposition rode the order that granted the petition."""
    if row.disposition in _CERT_ORDER_VALUES:
        return True
    return (
        row.merits_decided is not None
        and row.date_cert_granted is not None
        and judgment_rode_the_grant_order(row.merits_decided, row.date_cert_granted)
    )


def _judgment_counts(rows: list[corpus.CorpusRow]) -> dict[str, int]:
    counts = Counter(
        (judgment.value if (judgment := decision_judgment(row)) else "none") for row in rows
    )
    return dict(sorted(counts.items()))


def decision_census(
    conn: corpus.ReadConnection, *, first_term: int, last_term: int
) -> DecisionCensus:
    """Count the decision record per October Term, from the index alone.

    Read-only, and it reads no snapshot: what it counts is what the columns
    hold, so a NULL is a gap in the record, not a fact about the case. The
    population is every SCOTUS modern cert docket with a cert-grant date and a
    granted label, assigned to its :func:`decision_term`; a row carrying
    `merits_terminated` is counted apart by reason, in no Term.
    """
    by_term: dict[int, list[corpus.CorpusRow]] = {t: [] for t in range(first_term, last_term + 1)}
    pending = 0
    terminations: Counter[str] = Counter()
    rows = (
        row
        for disposition in sorted(GRANTED_DISPOSITIONS)
        for row in corpus.iter_rows(conn, court="scotus", disposition=disposition)
    )
    for row in rows:
        if row.date_cert_granted is None or not corpus.is_modern_cert(row):
            continue
        if row.merits_terminated is not None:
            terminations[row.merits_terminated] += 1
            continue
        term = decision_term(row)
        if term is None:
            pending += 1
        elif term in by_term:
            by_term[term].append(row)
    terms = []
    for term, members in by_term.items():
        methods = Counter(row.merits_decision_method or "unclassified" for row in members)
        plenary = [row for row in members if not _rode_the_order(row)]
        terms.append(
            DecisionTermCensus(
                term=term,
                assigned=len(members),
                argued=sum(row.merits_argued is not None for row in members),
                decided=sum(decision_date(row) is not None for row in members),
                order_riding=len(members) - len(plenary),
                methods=dict(sorted(methods.items())),
                dispositions=_judgment_counts(members),
                plenary_dispositions=_judgment_counts(plenary),
            )
        )
    return DecisionCensus(
        terms=terms, pending=pending, terminations=dict(sorted(terminations.items()))
    )
