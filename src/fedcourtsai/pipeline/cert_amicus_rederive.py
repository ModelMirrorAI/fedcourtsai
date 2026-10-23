"""Back-fill the corpus ``cert_amicus_briefs`` column over the cert live slice.

The cert-stage amicus count (:func:`fedcourtsai.pipeline.cert_amicus.cert_amicus_briefs`)
is written by the live poll's cert branch at ingest, so a row carries it only once
the poll has read the docket since the column existed. The poll's rotation skips a
resolved petition, so resolved history stays NULL, and the stat pack's amicus cut
(:func:`fedcourtsai.analytics.cert_amicus_section`) would read almost entirely
``(unknown)`` until something fills it. This pass is that fill: it recounts each
row from its latest stored live snapshot, exactly as ingest would count it, and
writes the count. Corpus only — no committed outcome or prediction carries a cert
amicus count, so there is no ledger half to re-freeze.

**The population is the one the live cert branch writes**: live-slice SCOTUS rows
whose stored docket number, with its display annotation stripped, parses as a
Term-form ``YY-NNNN`` number (:func:`~fedcourtsai.supremecourt.parse_scotus_docket_number`
over :func:`~fedcourtsai.corpus.strip_docket_annotation`). That is the test the
poll applies before fetching a docket in the cert form and handing its payload to
:func:`~fedcourtsai.pipeline.ingest.map_live_docket`'s cert branch, so paid and
IFP petitions are both in and an application, an original docket and an
unaddressable spelling are out — the same rows, by the same functions.

**The count is ingest's, call for call.** A snapshot that discloses a proceedings
list (:func:`~fedcourtsai.pipeline.cert_signals.snapshot_carries_proceedings`) is
counted by :func:`~fedcourtsai.pipeline.cert_amicus.cert_amicus_briefs` over
:func:`~fedcourtsai.pipeline.cert_signals.proceedings_entries` — the count at
disposition, with the Court's orders on amicus motions dropped. An empty list
counts 0, as it does at ingest. A row with no live-shaped snapshot, or one whose
snapshot discloses no proceedings, is ``unobservable``: counted, and left as it is.

**Open petitions are in.** The pass writes through the column's max latch (below),
so on an open row it writes exactly what the next poll of the same payload would,
and the next poll can only raise it. Leaving open rows to the poll would buy
nothing and leave the cut's open half NULL until the rotation reached each one.

**The write respects the max latch** (:func:`fedcourtsai.corpus.raise_cert_amicus_briefs`),
unlike the interim pass's direct ``UPDATE``. The interim re-derivation has to
lower rows, because its end-of-day cut drops entries an earlier, uncut reading
had counted. Nothing here is a change of reading: the cert column has carried
this one reading since its first write, and its cut is the first disposition
entry, which every read of the same docket finds in the same place. A recount
below the stored value therefore means the snapshot has lost entries, and
writing it would be the degraded-payload regression the latch exists to stop.
Such a row is reported as ``latch_held`` with both values, never written.

**The control is idempotence.** A second pass over a filled corpus finds every
readable row ``unchanged`` and reports ``total_changes = 0``: a docket polled
between the two runs is written by the poll with the same count, so it does not
reappear. A non-zero re-run is a row whose stored snapshot moved without its
column, and is worth reading. Durable for the same reason: the reading is
ingest's own, so a later poll of any row re-derives the same count or a higher
one.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .. import corpus
from ..supremecourt import parse_scotus_docket_number
from .cert_amicus import cert_amicus_briefs
from .cert_signals import (
    match_disposition_signal,
    proceedings_entries,
    snapshot_carries_proceedings,
)
from .prefetch import prefetch_by_case


class CertAmicusMove(BaseModel):
    """One stored count that differs from its recount, with both values."""

    model_config = ConfigDict(extra="forbid")

    case_id: str
    was: int = Field(ge=0, description="The stored count")
    now: int = Field(ge=0, description="The recount from the latest live snapshot")


class CertAmicusRederiveResult(BaseModel):
    """What one cert amicus back-fill pass wrote (or would write on a dry run).

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
        "branch writes, paid and IFP together",
    )
    read: int = Field(
        default=0,
        ge=0,
        description="Rows whose latest live snapshot discloses a proceedings list, so "
        "the count could be taken",
    )
    unobservable: int = Field(
        default=0,
        ge=0,
        description="Rows with no live-shaped snapshot, or one disclosing no "
        "proceedings — counted and left untouched. Read this FIRST: against an "
        "index-only pull, with no content store addressed, every row lands here and "
        "an empty ledger is a wrong-blob reading rather than a filled corpus",
    )
    open_petitions: int = Field(
        default=0,
        ge=0,
        description="Read rows whose snapshot carries no disposition entry yet: open "
        "petitions, whose count is a lower bound the live poll keeps raising",
    )
    unchanged: int = Field(
        default=0, ge=0, description="Read rows whose stored count equals the recount"
    )
    filled: int = Field(
        default=0, ge=0, description="Read rows stored NULL that the pass fills (NULL → value)"
    )
    raised: int = Field(
        default=0,
        ge=0,
        description="Read rows whose stored count is below the recount (value → higher value)",
    )
    latch_held: int = Field(
        default=0,
        ge=0,
        description="Read rows whose stored count is ABOVE the recount — the snapshot has "
        "lost entries the stored value counted. Never written: the latch holds them",
    )
    filled_distribution: dict[int, int] = Field(
        default_factory=dict,
        description="The values the fills write, keyed by value — the shape of the "
        "back-filled history, so a reader can see what the cut will bucket",
    )
    raised_moves: list[CertAmicusMove] = Field(
        default_factory=list,
        description="Every raised row with its old and new count, in `case_id` order",
    )
    latch_held_moves: list[CertAmicusMove] = Field(
        default_factory=list,
        description="Every latch-held row with its stored count and the lower recount, "
        "in `case_id` order — each is a degraded snapshot worth a look",
    )

    @computed_field(  # type: ignore[prop-decorator]
        description="The rows the apply writes: fills plus raises. The bound is read against this"
    )
    @property
    def total_changes(self) -> int:
        """The rows the apply writes: fills plus raises."""
        return self.filled + self.raised


def is_cert_form(row: corpus.CorpusRow) -> bool:
    """Whether the live poll addresses this SCOTUS row in the cert form.

    The test the poll applies before a cert fetch: the stored number, annotation
    stripped, parses as a Term-form number. Any such row the poll reads goes
    through the cert branch of ingest, which is the branch that writes
    ``cert_amicus_briefs``.
    """
    return (
        row.court == "scotus"
        and parse_scotus_docket_number(corpus.strip_docket_annotation(row.docket_number))
        is not None
    )


def rederive_cert_amicus_briefs(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    corpus_sha256: str = "",
    max_changes: int | None = None,
) -> CertAmicusRederiveResult:
    """Fill ``cert_amicus_briefs`` from each cert-form live-slice row's latest snapshot.

    One pass per invocation: the plan reported is the write set, so a dry run and
    the apply inside one call cannot describe different work. ``max_changes`` is
    the blast-radius bound over :attr:`CertAmicusRederiveResult.total_changes`;
    above it nothing is written and ``refused`` comes back true. ``None`` is
    unbounded, and a dry run never consults it. See the module docstring for the
    population, the count, and why the write keeps the max latch.
    """
    result = CertAmicusRederiveResult(applied=apply, corpus_sha256=corpus_sha256)
    # Materialized before any snapshot read: `iter_rows` is a cursor on `conn`,
    # and stepping it while the prefetch's workers read would put two readers on
    # one connection.
    rows = [
        row for row in corpus.iter_rows(conn, court="scotus", live_slice=True) if is_cert_form(row)
    ]
    result.eligible = len(rows)
    updates: list[tuple[str, int]] = []
    distribution: dict[int, int] = defaultdict(int)
    # Pooled over the content store under the corpus-split mode, serial on the
    # local connection otherwise; the loop body runs on this thread either way,
    # so both schedules classify identically.
    with prefetch_by_case(
        [row.case_id for row in rows],
        lambda case_id: corpus.latest_live_snapshot(conn, case_id),
        thread_name_prefix="cert-amicus-rederive",
    ) as fetched:
        for row, (_, found) in zip(rows, fetched, strict=True):
            if found is None or not snapshot_carries_proceedings(found[1]):
                result.unobservable += 1
                continue
            entries = proceedings_entries(found[1])
            result.read += 1
            if not any(match_disposition_signal(text) is not None for text, _ in entries):
                result.open_petitions += 1
            recount = cert_amicus_briefs(entries)
            stored = row.cert_amicus_briefs
            if stored is None:
                result.filled += 1
                distribution[recount] += 1
                updates.append((row.case_id, recount))
            elif recount > stored:
                result.raised += 1
                result.raised_moves.append(
                    CertAmicusMove(case_id=row.case_id, was=stored, now=recount)
                )
                updates.append((row.case_id, recount))
            elif recount < stored:
                result.latch_held += 1
                result.latch_held_moves.append(
                    CertAmicusMove(case_id=row.case_id, was=stored, now=recount)
                )
            else:
                result.unchanged += 1
    result.filled_distribution = dict(sorted(distribution.items()))

    if not apply:
        return result
    if max_changes is not None and result.total_changes > max_changes:
        result.refused = True
        return result
    written = corpus.raise_cert_amicus_briefs(conn, updates)
    if written != len(updates):
        # Every planned write is a NULL fill or a raise, which the latch admits,
        # so a shortfall means the stored rows moved between the read and the
        # write, or a planned row no longer exists. In the writer lane the step
        # runs under `set -euo pipefail`, so this stops the job before
        # `corpus-push` and the runner's blob is discarded with it.
        raise RuntimeError(
            f"planned {len(updates)} cert amicus write(s) but the UPDATE touched "
            f"{written} row(s) — the plan and the corpus disagree"
        )
    return result
