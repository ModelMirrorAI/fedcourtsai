"""Census what the finer interim reading names, and confirm nothing moves now.

The registered interim reading
(:func:`fedcourtsai.pipeline.interim_signals.match_interim_disposition`)
collapses a mixed partial disposition denial-first and reads a dismissal or
denial as moot by its verb. That reading is what the corpus stores, what
outcomes record, what claims and base rates score against and what a cell can
retrieve, and it is unchanged. The finer reading
(:func:`~fedcourtsai.pipeline.interim_signals.read_interim_disposition`) names
the two collapsed forms — ``granted-in-part`` and ``dismissed-moot`` — and is
descriptive only (``docs/freeze-record.md``, the 2026-10-16 interim
partial-grant and moot entry).

This census is that entry's measurement, and it writes nothing. It reports two
populations, and keeps them apart because they are different:

- **The statpack's.** Every SCOTUS application number in the strict
  ``YYAnnn`` form, once each, as the statpack's interim section counts it:
  substantive resolved and granted per application Term
  (:attr:`InterimTermCounts.statpack_resolved`), the counts the interim base
  rate pools.
- **The re-read one.** Of those, the rows application-parsed, resolved and in
  the live slice, whose latest live-shaped snapshot is re-read twice: under the
  registered reading, to confirm the stored label is what it gives
  (:attr:`InterimReadingCensus.registered_disagreements`), and under the finer
  one, to list the rows it names partial or moot. Rows with no snapshot
  (``unobservable``) and resolved rows outside the live slice (``non_live``)
  are counted and not re-read, so the re-read counts are a subset of the
  statpack's and the gap is stated per Term.

It also probes the registered reading's known misreading — an application
granted while a side request is denied as moot, which the registered denial
pattern reads ``denied`` — by counting stored ``denied`` rows whose disposing
entry holds an application clause that grants with no denial in it
(:attr:`InterimReadingCensus.registered_plain_grant_misreads`), and lists the
committed interim outcomes on the rows the finer reading names, which stay
exactly as recorded.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..corpus import CorpusRow
from ..schemas import Disposition, Outcome, Stage
from ..serialize import read_model
from . import moments
from .ingest import interim_disposing_text, interim_reading, interim_resolution
from .interim_signals import ApplicationKind, InterimReading, clause_reads_plain_grant
from .outcome import granted_flag, is_machine_readable
from .prefetch import prefetch_by_case

#: The two forms the finer reading adds over the registered one.
FINER_LABELS: frozenset[InterimReading] = frozenset(
    {InterimReading.granted_in_part, InterimReading.dismissed_moot}
)


class InterimReadingRow(BaseModel):
    """One stored application row the finer reading names partial or moot."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    term: int | None
    application_kind: str
    stored: Disposition = Field(description="The stored, registered label — unchanged")
    reading: InterimReading = Field(description="The finer reading of the same docket")
    same_entry: bool = Field(
        description="Whether the finer reading dates its disposing entry on the stored "
        "disposition date — false means it read a different entry"
    )


class InterimTermCounts(BaseModel):
    """One application Term's substantive counts across the two populations."""

    model_config = ConfigDict(extra="forbid")

    statpack_resolved: int = Field(
        default=0, description="`substantive_resolved` as the statpack counts it"
    )
    statpack_granted: int = Field(
        default=0, description="`substantive_granted` as the statpack counts it"
    )
    reread_resolved: int = Field(
        default=0, description="Of those resolved, the rows re-read from a snapshot"
    )
    reread_granted: int = Field(default=0, description="Of those, granted (registered)")
    reread_partial: int = Field(
        default=0, description="Re-read rows the finer reading names granted-in-part"
    )
    reread_partial_stored_ungranted: int = Field(
        default=0, description="Of those, rows stored on the ungranted side"
    )
    reread_moot: int = Field(
        default=0, description="Re-read rows the finer reading names dismissed-moot"
    )
    unobservable: int = Field(default=0, description="Resolved rows with no snapshot")
    non_live: int = Field(default=0, description="Resolved rows outside the live slice")


class InterimOutcomeLine(BaseModel):
    """One committed interim outcome on a row the finer reading names."""

    model_config = ConfigDict(extra="forbid")

    ref: str
    recorded: Disposition
    reading: InterimReading
    predictions: int = Field(ge=0)


class InterimReadingCensus(BaseModel):
    """The census, serialized whole by the command."""

    model_config = ConfigDict(extra="forbid")

    corpus_sha256: str = ""
    eligible: int = Field(
        default=0,
        description="Resolved, application-parsed, live-slice application rows — the "
        "re-read population",
    )
    observable: int = 0
    unobservable: int = Field(
        default=0,
        description="Of those, rows with no live-shaped snapshot. Read this FIRST: "
        "against an index-only pull every row lands here",
    )
    non_live: int = Field(
        default=0,
        description="Resolved, application-parsed application rows outside the live "
        "slice — counted by the statpack, not re-read",
    )
    registered_disagreements: list[str] = Field(
        default_factory=list,
        description="Case ids whose stored label the registered reading does not "
        "reproduce from the snapshot — pre-existing drift, not this reading's",
    )
    registered_plain_grant_misreads: list[str] = Field(
        default_factory=list,
        description="Case ids stored `denied` whose disposing entry holds an "
        "application clause that grants with no denial in it — the registered "
        "reading's known side-motion misreading, of unmeasured prevalence until this "
        "list is read",
    )
    rows: list[InterimReadingRow] = Field(default_factory=list)
    by_term: dict[str, dict[str, dict[str, int]]] = Field(
        default_factory=dict,
        description="The rows above by application Term, then ask, then finer label",
    )
    terms: dict[str, InterimTermCounts] = Field(
        default_factory=dict,
        description="Per application Term, the statpack's substantive counts beside the "
        "re-read subset's and the gap between them",
    )
    committed_outcomes: list[InterimOutcomeLine] = Field(
        default_factory=list,
        description="Committed interim outcomes on the rows above — unchanged",
    )
    stored_labels_written: int = Field(
        default=0,
        description="Always 0: the census writes nothing, and no stored, scored or "
        "cell-facing label moves under the current process label",
    )


def _term_key(term: int | None) -> str:
    return f"OT{term}" if term is not None else "unknown"


def _kind(row: CorpusRow) -> str | None:
    """The ask as the statpack buckets it (an out-of-vocabulary kind reads unknown)."""
    if row.application_kind is None:
        return None
    known = {kind.value for kind in ApplicationKind}
    return row.application_kind if row.application_kind in known else ApplicationKind.unknown.value


def _stored(row: CorpusRow) -> Disposition:
    assert row.disposition is not None  # only resolved rows reach here
    return Disposition(row.disposition)


def _substantive(row: CorpusRow) -> bool:
    """Whether the statpack counts the row in `substantive_resolved`."""
    return _kind(row) == ApplicationKind.substantive.value and is_machine_readable(_stored(row))


_Terms = dict[str, InterimTermCounts]
_ByTerm = dict[str, dict[str, dict[str, int]]]


def _statpack_walk(
    conn: sqlite3.Connection, result: InterimReadingCensus, terms: _Terms
) -> list[CorpusRow]:
    """Count the statpack's population per Term and return the rows to re-read.

    The statpack counts each application number once
    (:func:`corpus.duplicate_application_case_ids`), so a second row for a
    number is skipped here too — it is neither counted nor re-read.
    """
    reread: list[CorpusRow] = []
    twins = corpus.duplicate_application_case_ids(conn)
    for row in corpus.iter_rows(conn, court="scotus", resolved=True):
        term = corpus.scotus_application_term_year(row.docket_number)
        if term is None or row.case_id in twins:
            continue
        counts = terms[_term_key(term)]
        substantive = _substantive(row)
        if substantive:
            counts.statpack_resolved += 1
            counts.statpack_granted += granted_flag(_stored(row))
        if row.application_kind is None:
            continue
        if not corpus.is_live_slice(row):
            result.non_live += 1
            counts.non_live += int(substantive)
            continue
        reread.append(row)
    return reread


def _reread(
    row: CorpusRow,
    payload: dict[str, Any],
    result: InterimReadingCensus,
    counts: InterimTermCounts,
    by_term: _ByTerm,
) -> None:
    """Read one stored snapshot under both readings and record what each says."""
    stored = _stored(row)
    registered, _ = interim_resolution(payload)
    if registered != stored.value:
        result.registered_disagreements.append(row.case_id)
    if stored is Disposition.denied:
        disposing = interim_disposing_text(payload)
        if disposing is not None and clause_reads_plain_grant(disposing):
            result.registered_plain_grant_misreads.append(row.case_id)
    reading, decided = interim_reading(payload)
    if _substantive(row):
        counts.reread_resolved += 1
        counts.reread_granted += granted_flag(stored)
        if reading is InterimReading.granted_in_part:
            counts.reread_partial += 1
            counts.reread_partial_stored_ungranted += int(not granted_flag(stored))
        elif reading is InterimReading.dismissed_moot:
            counts.reread_moot += 1
    if reading is None or reading not in FINER_LABELS:
        return
    term = corpus.scotus_application_term_year(row.docket_number)
    kind = _kind(row) or ApplicationKind.unknown.value
    result.rows.append(
        InterimReadingRow(
            case_id=row.case_id,
            docket_number=row.docket_number,
            term=term,
            application_kind=kind,
            stored=stored,
            reading=reading,
            same_entry=decided == corpus.resolution_date(row),
        )
    )
    by_term[_term_key(term)][kind][reading.value] += 1


def _committed_outcomes(data_root: Path, rows: list[InterimReadingRow]) -> list[InterimOutcomeLine]:
    """The committed interim outcomes on the named rows, read and left as they are."""
    lines: list[InterimOutcomeLine] = []
    for line in rows:
        court, _, docket = line.case_id.partition("/")
        events = data_root / "cases" / court / docket / "events"
        for path in sorted(events.glob("*/outcome.json")):
            outcome = read_model(path, Outcome)
            if not moments.declares(outcome.event_id, Stage.interim):
                continue
            lines.append(
                InterimOutcomeLine(
                    ref=f"{outcome.case_id}/{outcome.event_id}",
                    recorded=outcome.actual_disposition,
                    reading=line.reading,
                    predictions=len(list(path.parent.glob("predictions/*/*/prediction.json"))),
                )
            )
    return lines


def interim_reading_census(
    conn: sqlite3.Connection, data_root: Path, *, corpus_sha256: str = ""
) -> InterimReadingCensus:
    """Run the census (see the module docstring). Reads only."""
    result = InterimReadingCensus(corpus_sha256=corpus_sha256)
    terms: _Terms = defaultdict(InterimTermCounts)
    reread = _statpack_walk(conn, result, terms)
    result.eligible = len(reread)
    by_term: _ByTerm = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    # The walk above is materialized before any snapshot read, so the prefetch's
    # workers never share the row cursor on `conn`.
    with prefetch_by_case(
        [row.case_id for row in reread],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="interim-reading-census",
    ) as fetched:
        for row, (_, found) in zip(reread, fetched, strict=True):
            counts = terms[_term_key(corpus.scotus_application_term_year(row.docket_number))]
            if found is None:
                result.unobservable += 1
                counts.unobservable += int(_substantive(row))
                continue
            result.observable += 1
            _reread(row, found[1], result, counts, by_term)
    result.by_term = {
        term: {kind: dict(sorted(labels.items())) for kind, labels in sorted(kinds.items())}
        for term, kinds in sorted(by_term.items())
    }
    result.terms = dict(sorted(terms.items(), reverse=True))
    result.committed_outcomes = _committed_outcomes(data_root, result.rows)
    return result
