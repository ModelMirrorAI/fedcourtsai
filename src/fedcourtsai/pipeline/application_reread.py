"""Re-read stored interim applications and fill the columns later readings add.

The live channel's application branch writes each reading of an application's
docket at ingest, so a row carries a reading only once the poll has read the
docket since that reading existed. The live rotation skips a resolved
application, so resolved history keeps whatever its last poll wrote, and a
column added later stays NULL there. This pass is the fill: it re-reads each
stored application from its latest stored live snapshot with ingest's own
function and writes what ingest would have written. Corpus only — no committed
outcome or prediction is opened, because ``outcome.json`` is written once, at
resolution, and an outcome recorded before a column existed keeps what it
recorded.

**The column it fills: ``interim_reading``**, the finer interim reading
(:func:`fedcourtsai.pipeline.ingest.stored_interim_reading`, the function the
application branch stores) beside the registered ``disposition``, which this
pass never reads into and never writes. The statpack's finer interim counts and
the finer interim pool (:func:`fedcourtsai.pipeline.base_rates.interim_base_rate`
with ``reading="finer"``) read it, and the pool refuses a rate over any Term
the pass has not covered in full (``finer_unread``), so the apply is what turns
the finer pool on.

**The second column it fills: ``application_kind_wide``**, the ask under the
widened vocabulary (:func:`fedcourtsai.pipeline.ingest.stored_application_kinds`,
the function the application branch stores), beside ``application_kind``, which
this pass never writes. The statpack's wide interim counts read it, and the
OT2027 interim pool (:func:`fedcourtsai.pipeline.base_rates.interim_base_rate`)
refuses a rate over any Term with a resolved application it has not read
(``wide_unread``). Its ledger counts the two columns apart, and the bound is
read over both.

**The population is the resolved application slice**: live-slice SCOTUS rows
that were application-parsed (``application_kind`` set) and carry a registered
disposition label. A pending application reads no disposition, so it has no
reading to fill, and the live channel writes one when it resolves. A row with no
live-shaped snapshot, or one whose snapshot discloses no proceedings, is
``unobservable``: counted, and left as it is.

**A stored value that differs is overwritten, and listed.** The pass reads the
same snapshot with the same function as ingest, so a differing value is a
reading the code has since corrected, or a snapshot that moved without its
column. Both reach the ledger as one ``was -> now`` in ``moves``, read before an
apply.

**The control is idempotence.** A second pass over a filled corpus finds every
readable row ``unchanged`` and reports ``total_changes = 0``.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .. import corpus
from .cert_signals import snapshot_carries_proceedings
from .ingest import stored_application_kinds, stored_interim_reading
from .prefetch import prefetch_by_case


class ApplicationRereadMove(BaseModel):
    """One stored value that differs from its re-read, with both values."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    docket_number: str
    was: str = Field(description="The stored value")
    now: str = Field(description="The re-read from the latest live snapshot")


class ApplicationRereadResult(BaseModel):
    """What one application re-read pass wrote (or would write on a dry run).

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
        description="Resolved application rows walked: live-slice SCOTUS rows with an "
        "`application_kind` and a registered disposition",
    )
    read: int = Field(
        default=0,
        ge=0,
        description="Rows whose latest live snapshot discloses a proceedings list",
    )
    unobservable: int = Field(
        default=0,
        ge=0,
        description="Rows with no live-shaped snapshot, or one disclosing no proceedings — "
        "counted and left untouched. Read this FIRST: against an index-only pull, with no "
        "content store addressed, every row lands here and an empty ledger is a wrong-blob "
        "reading rather than a filled corpus",
    )
    no_reading: int = Field(
        default=0,
        ge=0,
        description="Read rows whose snapshot yields no finer reading at all (no disposing "
        "entry the reader matches) — left untouched, and counted `finer_unread` by the "
        "statpack, so a non-zero value here holds the finer pool off its Term",
    )
    unchanged: int = Field(
        default=0, ge=0, description="Read rows whose stored reading equals the re-read"
    )
    filled: int = Field(
        default=0, ge=0, description="Read rows stored NULL that the pass fills (NULL → value)"
    )
    moved: int = Field(
        default=0, ge=0, description="Read rows whose stored reading differs from the re-read"
    )
    filled_readings: dict[str, int] = Field(
        default_factory=dict,
        description="The readings the fills write, keyed by reading",
    )
    finer_vs_registered: dict[str, int] = Field(
        default_factory=dict,
        description="Every read row's re-read beside its registered label, keyed "
        "`registered -> finer` — where the two readings part, by how many rows",
    )
    moves: list[ApplicationRereadMove] = Field(
        default_factory=list,
        description="Every moved row with its stored and re-read value, in `case_id` order",
    )
    kind_unchanged: int = Field(
        default=0,
        ge=0,
        description="Read rows whose stored `application_kind_wide` equals the re-read",
    )
    kind_filled: int = Field(
        default=0,
        ge=0,
        description="Read rows whose `application_kind_wide` is stored NULL and is filled",
    )
    kind_moved: int = Field(
        default=0,
        ge=0,
        description="Read rows whose stored `application_kind_wide` differs from the re-read",
    )
    wide_vs_registered: dict[str, int] = Field(
        default_factory=dict,
        description="Every read row's widened ask beside its stored `application_kind`, "
        "keyed `registered -> wide` — the rows the widened vocabulary moves, by how many",
    )
    kind_moves: list[ApplicationRereadMove] = Field(
        default_factory=list,
        description="Every row whose stored `application_kind_wide` moved, in `case_id` order",
    )
    no_reading_rows: list[str] = Field(
        default_factory=list,
        description="The `no_reading` rows' case ids, in `case_id` order",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="The column values the apply writes: fills plus moves, over both "
        "columns. The bound is read against this"
    )
    @property
    def total_changes(self) -> int:
        """The column values the apply writes: fills plus moves, over both columns."""
        return self.filled + self.moved + self.kind_filled + self.kind_moved


def _is_resolved_application(row: corpus.CorpusRow) -> bool:
    """Whether the row is in the pass's population (see the module docstring)."""
    return row.application_kind is not None and row.disposition is not None


def _plan_kind(
    result: ApplicationRereadResult,
    row: corpus.CorpusRow,
    wide: str,
    updates: list[tuple[str, str]],
) -> None:
    """Tally one read row's widened ask against its stored one, planning any write."""
    stored = row.application_kind_wide
    if stored == wide:
        result.kind_unchanged += 1
        return
    if stored is None:
        result.kind_filled += 1
    else:
        result.kind_moved += 1
        result.kind_moves.append(
            ApplicationRereadMove(
                case_id=row.case_id, docket_number=row.docket_number, was=stored, now=wide
            )
        )
    updates.append((row.case_id, wide))


def reread_applications(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    corpus_sha256: str = "",
    max_changes: int | None = None,
) -> ApplicationRereadResult:
    """Fill ``interim_reading`` and ``application_kind_wide`` from each latest live snapshot.

    One pass per invocation: the plan reported is the write set, so a dry run and
    the apply inside one call cannot describe different work. ``max_changes`` is
    the blast-radius bound over :attr:`ApplicationRereadResult.total_changes`;
    above it nothing is written and ``refused`` comes back true. ``None`` is
    unbounded, and a dry run never consults it.
    """
    result = ApplicationRereadResult(applied=apply, corpus_sha256=corpus_sha256)
    # Materialized before any snapshot read: `iter_rows` is a cursor on `conn`,
    # and stepping it while the prefetch's workers read would put two readers on
    # one connection.
    rows = [
        row
        for row in corpus.iter_rows(conn, court="scotus", resolved=True, live_slice=True)
        if _is_resolved_application(row)
    ]
    result.eligible = len(rows)
    updates: list[tuple[str, str]] = []
    kind_updates: list[tuple[str, str]] = []
    filled: dict[str, int] = defaultdict(int)
    pairs: dict[str, int] = defaultdict(int)
    kind_pairs: dict[str, int] = defaultdict(int)
    with prefetch_by_case(
        [row.case_id for row in rows],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="application-reread",
    ) as fetched:
        for row, (_, found) in zip(rows, fetched, strict=True):
            if found is None or not snapshot_carries_proceedings(found[1]):
                result.unobservable += 1
                continue
            result.read += 1
            _, wide = stored_application_kinds(found[1])
            kind_pairs[f"{row.application_kind} -> {wide}"] += 1
            _plan_kind(result, row, wide, kind_updates)
            reading = stored_interim_reading(found[1])
            pairs[f"{row.disposition} -> {reading}"] += 1
            if reading is None:
                result.no_reading += 1
                result.no_reading_rows.append(row.case_id)
                continue
            stored = row.interim_reading
            if stored is None:
                result.filled += 1
                filled[reading] += 1
                updates.append((row.case_id, reading))
            elif stored != reading:
                result.moved += 1
                result.moves.append(
                    ApplicationRereadMove(
                        case_id=row.case_id,
                        docket_number=row.docket_number,
                        was=stored,
                        now=reading,
                    )
                )
                updates.append((row.case_id, reading))
            else:
                result.unchanged += 1
    result.filled_readings = dict(sorted(filled.items()))
    result.finer_vs_registered = dict(sorted(pairs.items()))
    result.wide_vs_registered = dict(sorted(kind_pairs.items()))

    if not apply:
        return result
    if max_changes is not None and result.total_changes > max_changes:
        result.refused = True
        return result
    written = corpus.set_interim_readings(conn, updates)
    if written != len(updates):
        # In the writer lane the step runs under `set -euo pipefail`, so this
        # stops the job before `corpus-push` and the runner's blob is discarded.
        raise RuntimeError(
            f"planned {len(updates)} interim reading write(s) but the UPDATE touched "
            f"{written} row(s) — the plan and the corpus disagree"
        )
    written = corpus.set_application_kinds_wide(conn, kind_updates)
    if written != len(kind_updates):
        raise RuntimeError(
            f"planned {len(kind_updates)} widened ask write(s) but the UPDATE touched "
            f"{written} row(s) — the plan and the corpus disagree"
        )
    return result
