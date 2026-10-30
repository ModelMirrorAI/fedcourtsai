"""Back-fill the three withheld cert columns ``sal-v5`` reads, on rows already ingested.

``call_for_response_at``, ``distributed_after_call`` and ``opening_writ`` are
written by the live poll's cert branch at ingest
(:func:`~fedcourtsai.pipeline.ingest.map_live_docket`) and fill-in latched by the
upsert, so a row carries them only once the poll has read its docket since each
column existed. The rotation skips a resolved petition, so resolved history keeps
NULL in every column it predates, and ``sal-v5``'s relist rule
(``distributed_after_call``) and writ scope (``opening_writ``) would read past
Terms as ``sal-v4`` reads them (``docs/salience.md``, the ``sal-v5`` section).
This pass is that fill: it re-parses each row's newest stored live snapshot with
the pure functions ingest calls and writes each reading the row does not yet
carry. Corpus only — no committed artifact carries these columns, and all three
are withheld from the retrieval surface (``corpus.RETRIEVAL_WITHHELD_COLUMNS``).

**The population is the cert branch's**: live-slice SCOTUS rows whose stored
docket number parses as a Term-form number
(:func:`~fedcourtsai.pipeline.cert_amicus_rederive.is_cert_form`), the test the
poll applies before a cert fetch — the rows ingest writes these columns on.

**The readings are ingest's, call for call**:
:func:`~fedcourtsai.pipeline.cert_signals.call_for_response_date`,
:func:`~fedcourtsai.pipeline.cert_signals.distributions_after_call` and
:func:`~fedcourtsai.pipeline.cert_signals.opening_writ`, each over the snapshot's
whole payload, so a NULL this pass fills holds what a poll of the same snapshot
would have written there.

**The write fills NULLs only, and is stricter than ingest.** Ingest's upsert
latches these columns as ``COALESCE(excluded.col, cases.col)``
(:func:`fedcourtsai.corpus._update_clause`): a fresh non-NULL reading replaces
the stored one, and only a NULL reading keeps it. This pass never replaces
anything. A column already holding a value is ``already_set`` and never written
or compared, whatever the snapshot now reads, and the statement is
``COALESCE(cases.col, new)``, so a value a poll stamps between the read and the
write is kept rather than overwritten. A stored value that disagrees with the
newest snapshot is the next poll's to correct, not this pass's.

**The call-for-response pair stays consistent.** ``distributed_after_call``
counts conferences after the call the payload itself dates. Where
``call_for_response_at`` is already stored and the newest snapshot dates the call
differently, a count filled from that snapshot would hang off a call the row does
not record, so the row is counted ``pair_mismatch`` and the count is not filled.

Per column a NULL row is otherwise one of two things (three, for
``distributed_after_call``, with ``pair_mismatch`` above): ``unparseable`` — the row
has no live-shaped snapshot, or its snapshot discloses no proceedings, so no
reading could be taken — or ``no_reading`` — the proceedings were read and name
no call for response, or no opening petition entry, so the reading is NULL and
there is nothing to write. A row whose three columns are all set is not read at
all: nothing on it can be written.

Like its ``set_*`` and decision-record siblings, the write is a direct guarded
``UPDATE`` of the index, never the casestore mirror: an upsert re-asserts the
whole row and mirrors its ``case.json`` per row for three scalars, from a
split-mode blob that carries no opinion body. A store-side rebuild from
``case.json`` would therefore bring back NULL on a row the rotation no longer
polls; re-running the pass fills it again.

**The control is idempotence.** A filled column is ``already_set`` on the next
run, so a second pass over a filled corpus reports ``total_fills = 0``; a row the
poll reads between the two runs is written by ingest with the same readings.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .. import corpus
from .cert_amicus_rederive import is_cert_form
from .cert_signals import (
    call_for_response_date,
    distributions_after_call,
    opening_writ,
    snapshot_carries_proceedings,
)
from .prefetch import prefetch_by_case

#: The three columns, in the order the ledger prints them.
Column = Literal["call_for_response_at", "distributed_after_call", "opening_writ"]
COLUMNS: tuple[Column, ...] = ("call_for_response_at", "distributed_after_call", "opening_writ")


def _call_for_response(payload: Mapping[str, Any]) -> str | None:
    called = call_for_response_date(payload)
    return called.isoformat() if called is not None else None


#: Each column's ingest reading, in the stored form ingest writes it.
_READERS: Mapping[Column, Callable[[Mapping[str, Any]], str | int | None]] = {
    "call_for_response_at": _call_for_response,
    "distributed_after_call": distributions_after_call,
    "opening_writ": opening_writ,
}


class ColumnLedger(BaseModel):
    """One column's classification over the walked rows. The five counts sum to ``eligible``."""

    model_config = ConfigDict(extra="forbid")

    would_fill: int = Field(
        default=0, ge=0, description="NULL rows whose snapshot yields a reading: the fills"
    )
    already_set: int = Field(
        default=0,
        ge=0,
        description="Rows already carrying a value — latched, never written or compared",
    )
    no_reading: int = Field(
        default=0,
        ge=0,
        description="NULL rows whose proceedings were read and yield no value (no call for "
        "response, no opening petition entry): nothing to write",
    )
    unparseable: int = Field(
        default=0,
        ge=0,
        description="NULL rows with no live-shaped snapshot, or one disclosing no "
        "proceedings: no reading could be taken, left untouched",
    )
    pair_mismatch: int = Field(
        default=0,
        ge=0,
        description="`distributed_after_call` only: NULL rows whose stored "
        "`call_for_response_at` differs from the call date the newest snapshot reads, so "
        "the snapshot's count would hang off a call the row does not record — not filled",
    )
    filled_values: dict[str, int] = Field(
        default_factory=dict,
        description="The values the fills write, keyed by value — a date by its calendar "
        "year, a count or a writ by itself — the shape of the back-filled history",
    )


class CertColumnFill(BaseModel):
    """One row's planned fills; a column left ``None`` is not written."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    call_for_response_at: str | None = None
    distributed_after_call: int | None = None
    opening_writ: str | None = None


class SalienceCertBackfillResult(BaseModel):
    """What one back-fill pass wrote (or would write on a dry run).

    A model so the command serializes it whole: the workflow tees it into the run
    summary as the ledger a maintainer reads before the apply.
    """

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(
        default=False, description="Whether the pass ran in apply mode (False = dry-run)"
    )
    refused: bool = Field(
        default=False,
        description="Whether the blast-radius bound stopped the apply — nothing was written",
    )
    corpus_sha256: str = Field(
        default="", description="sha256 of the corpus database the pass read"
    )
    eligible: int = Field(
        default=0,
        ge=0,
        description="Cert-form live-slice SCOTUS rows walked — the rows the live cert "
        "branch writes these columns on",
    )
    read: int = Field(
        default=0,
        ge=0,
        description="Rows whose newest live snapshot was fetched and discloses proceedings",
    )
    unobservable: int = Field(
        default=0,
        ge=0,
        description="Fetched rows with no live-shaped snapshot, or one disclosing no "
        "proceedings. Read this FIRST: against an index-only pull, with no content store "
        "addressed, every fetched row lands here and an empty ledger is a wrong-blob "
        "reading rather than a filled corpus",
    )
    all_set: int = Field(
        default=0,
        ge=0,
        description="Rows already carrying all three columns — not fetched, nothing to write",
    )
    columns: dict[str, ColumnLedger] = Field(
        default_factory=dict, description="The per-column ledger, keyed by column name"
    )
    fills: list[CertColumnFill] = Field(
        default_factory=list,
        # Kept off the serialized ledger: over the cert history it runs to
        # thousands of rows, past what a run summary holds.
        exclude=True,
        description="Every row the apply writes, in `case_id` order",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="Column fills across all three columns. The bound is read against this"
    )
    @property
    def total_fills(self) -> int:
        """Column fills across all three columns."""
        return sum(ledger.would_fill for ledger in self.columns.values())


def _value_key(column: Column, value: str | int) -> str:
    # A date's year is enough to show the history's shape; a count or a writ
    # is its own key.
    return str(value)[:4] if column == "call_for_response_at" else str(value)


def _readings(
    payload: Mapping[str, Any],
    stored: Mapping[Column, object],
    ledgers: Mapping[Column, ColumnLedger],
) -> dict[str, str | int]:
    """Classify one read row's NULL columns into ``ledgers``; return the fills."""
    stored_call = stored["call_for_response_at"]
    readings: dict[str, str | int] = {}
    for column in COLUMNS:
        if stored[column] is not None:
            continue
        if (
            column == "distributed_after_call"
            and stored_call is not None
            and (snapshot_call := call_for_response_date(payload)) is not None
            and snapshot_call != stored_call
        ):
            ledgers[column].pair_mismatch += 1
            continue
        value = _READERS[column](payload)
        if value is None:
            ledgers[column].no_reading += 1
            continue
        ledgers[column].would_fill += 1
        key = _value_key(column, value)
        ledgers[column].filled_values[key] = ledgers[column].filled_values.get(key, 0) + 1
        readings[column] = value
    return readings


def _write(conn: sqlite3.Connection, fills: list[CertColumnFill]) -> None:
    """Land the planned fills in one transaction, or raise and roll back."""
    # Stored values win in the statement itself: a value stamped between the
    # read and the write is kept, not overwritten.
    written = 0
    with conn:
        for fill in fills:
            cursor = conn.execute(
                "UPDATE cases SET "
                "call_for_response_at = COALESCE(call_for_response_at, ?), "
                "distributed_after_call = COALESCE(distributed_after_call, ?), "
                "opening_writ = COALESCE(opening_writ, ?) WHERE case_id = ?",
                (
                    fill.call_for_response_at,
                    fill.distributed_after_call,
                    fill.opening_writ,
                    fill.case_id,
                ),
            )
            written += cursor.rowcount
        if written != len(fills):
            # A planned row no longer exists: the plan and the corpus disagree.
            # Raised inside the transaction, so the batch rolls back; in the
            # writer lane the step runs under `set -euo pipefail`, so this also
            # stops the job before `corpus-push` and the runner's blob is
            # discarded with it.
            raise RuntimeError(
                f"planned {len(fills)} sal-v5 cert row write(s) but the UPDATE "
                f"touched {written} row(s) — the plan and the corpus disagree"
            )


def backfill_salience_cert_columns(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    corpus_sha256: str = "",
    max_fills: int | None = None,
) -> SalienceCertBackfillResult:
    """Fill the three ``sal-v5`` cert columns from each row's newest live snapshot.

    One pass per invocation: the plan reported is the write set, so a dry run and
    the apply inside one call cannot describe different work. ``max_fills`` is the
    blast-radius bound over :attr:`SalienceCertBackfillResult.total_fills`; above it
    nothing is written and ``refused`` comes back true. ``None`` is unbounded, and a
    dry run never consults it. See the module docstring for the population, the
    readings, and why only NULLs are filled.
    """
    result = SalienceCertBackfillResult(applied=apply, corpus_sha256=corpus_sha256)
    ledgers = {column: ColumnLedger() for column in COLUMNS}
    # Materialized before any snapshot read: `iter_rows` is a cursor on `conn`,
    # and stepping it while the prefetch's workers read would put two readers on
    # one connection.
    rows = [
        row for row in corpus.iter_rows(conn, court="scotus", live_slice=True) if is_cert_form(row)
    ]
    result.eligible = len(rows)
    stored: dict[str, dict[Column, object]] = {
        row.case_id: {column: getattr(row, column) for column in COLUMNS} for row in rows
    }
    for values in stored.values():
        for column in COLUMNS:
            if values[column] is not None:
                ledgers[column].already_set += 1
    pending = [
        case_id
        for case_id, values in stored.items()
        if any(value is None for value in values.values())
    ]
    result.all_set = len(rows) - len(pending)
    with prefetch_by_case(
        pending,
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="salience-cert-backfill",
    ) as fetched:
        for case_id, found in fetched:
            missing = [column for column in COLUMNS if stored[case_id][column] is None]
            if found is None or not snapshot_carries_proceedings(found[1]):
                result.unobservable += 1
                for column in missing:
                    ledgers[column].unparseable += 1
                continue
            result.read += 1
            readings = _readings(found[1], stored[case_id], ledgers)
            if readings:
                result.fills.append(CertColumnFill.model_validate({"case_id": case_id, **readings}))
    for ledger in ledgers.values():
        ledger.filled_values = dict(sorted(ledger.filled_values.items()))
    result.columns = {str(column): ledger for column, ledger in ledgers.items()}
    result.fills.sort(key=lambda fill: fill.case_id)

    if not apply:
        return result
    if max_fills is not None and result.total_fills > max_fills:
        result.refused = True
        return result
    _write(conn, result.fills)
    return result
