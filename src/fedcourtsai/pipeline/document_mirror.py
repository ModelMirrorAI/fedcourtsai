"""The store mirror for cases whose document text reached the blob and not the store.

Under the corpus split the per-case content store is the system of record for
documents: :func:`~fedcourtsai.corpus.upsert_documents` writes the batch to the
store and leaves the blob's ``documents`` table empty, and every production read
(:func:`~fedcourtsai.corpus.documents_for_case`) is served from the store. So a
case whose text exists only in the blob's table serves *nothing* to a cell's
provisioning, to the questions-presented derivations, or to the QP-topic
labeling pack, however intact the stored text is.

- **Population.** The distinct ``case_id``s in the blob's own ``documents``
  table, read by direct SQL. That inverts the reading every other document pass
  takes — they walk ``documents_for_case`` precisely *because* the split blob's
  table is empty — and it is correct here for the one reason this pass exists:
  the blob in hand is the pre-split-era full one, whose table still carries the
  text that was written before the store did, and the routed read would answer
  from the store, which is exactly the side known to be missing. A blob written
  entirely under the split holds no rows at all, and the caller refuses on that
  rather than reporting a converged class.
- **The class.** For each such case, whether the store would serve it any
  document — :func:`~fedcourtsai.casestore.read_has_documents`, the *production*
  read, rather than a listing of the case's ``documents/`` prefix. The two
  disagree exactly where it matters, because
  :func:`~fedcourtsai.casestore.merge_documents` puts the text leaves before the
  manifest: a mirror whose leaf landed and whose manifest did not leaves keys
  under the prefix and serves nothing, and a listing would call that verified,
  drop the case from the class, and never retry it. The same reading puts a case
  carrying only an *empty* manifest in the class, which is right for the same
  reason — the blob holds its text and the store serves none of it, which is the
  defect however the store came to look that way.
- **Dry run (default).** The whole population is enumerated and nothing is
  written: the counts, and the absent cases named with what the blob holds for
  each (row count and text bytes), which is the ledger the apply's bound is read
  off. Unbounded by construction — a bound would report a class smaller than the
  one an apply then acts on.
- **Apply.** The first ``max_cases`` of the class in ``case_id`` order, mirrored
  through :func:`fedcourtsai.casestore.mirror_documents`, which is the split
  mode's own batch entry point: the blob is not read back through the routed
  read (it would answer empty), the in-hand batch is merged onto whatever
  manifest the case has. That writer is **best-effort** — it swallows every
  transport failure so no mirror can break an ingestion write — so each mirrored
  case is **re-probed** and reported ``verified`` or ``unverified``. The re-probe
  is what makes a best-effort writer honest in a repair ledger: without it a run
  whose credentials, store address or pointer override withheld every write
  reports the same clean slice as one that landed.

Additive and self-advancing. A verified case leaves the class, so the next
dispatch's slice starts where this one's ran out; an unverified one keeps
exactly what it had — the blob's rows are never touched — and is retried at the
head of the next slice.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from .. import casestore, corpus

logger = logging.getLogger(__name__)


class BlobDocuments(BaseModel):
    """What the blob's ``documents`` table holds for one case in the class."""

    model_config = ConfigDict(extra="forbid")

    rows: int = Field(ge=0, description="Rows the blob's `documents` table holds for the case")
    text_bytes: int = Field(
        ge=0,
        description="Total UTF-8 size of those rows' extracted text. The size of "
        "what the mirror would upload, and the reading that separates a case "
        "holding real filings from one holding a row of empty text",
    )


class DocumentMirrorResult(BaseModel):
    """What one mirror slice found, and wrote."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(
        description="Whether the pass mirrored the documents or only counted them"
    )
    cases_with_blob_documents: int = Field(
        ge=0,
        description="Distinct cases the blob's `documents` table holds rows for — "
        "the population and the denominator under `absent`. Zero means the wrong "
        "blob rather than a converged class (a blob written entirely under the "
        "corpus split holds no document rows at all), so the caller refuses on it",
    )
    present: int = Field(
        ge=0,
        description="Of the population, the cases the content store would already "
        "serve at least one document for — nothing to mirror",
    )
    absent: int = Field(
        ge=0,
        description="Of the population, the cases the content store would serve no "
        "document for: the class, in `case_id` order",
    )
    absent_cases: dict[str, BlobDocuments] = Field(
        default_factory=dict,
        description="case_id -> what the blob holds for it, for every case in the "
        "class and in class order. Written in BOTH modes and untruncated: it is the "
        "dry run's whole product, and on an apply it is the class as it stood when "
        "the slice was taken",
    )
    bound: int | None = Field(
        default=None,
        description="The per-dispatch slice size an apply was bounded to. Never set "
        "on a dry run, which enumerates the whole population — a bounded ledger would "
        "report a class smaller than the one the apply it is read off then acts on",
    )
    attempted: list[str] = Field(
        default_factory=list,
        description="The cases this run mirrored, in class order (apply only) — the "
        "first `bound` of the class",
    )
    verified: list[str] = Field(
        default_factory=list,
        description="Of `attempted`, the cases the store serves documents for on the "
        "re-probe: the write landed and the case has left the class",
    )
    unverified: list[str] = Field(
        default_factory=list,
        description="Of `attempted`, the cases the store still serves no document for. "
        "The mirror writer is best-effort and swallows transport failures, so this is "
        "the only place a withheld, failed or half-landed write is visible — an empty "
        "`verified` beside a full `attempted` is a store that took none of them (bad "
        "credentials, the wrong address, or the out-of-band pointer override withholding "
        "mirrors), not a class that would not drain",
    )
    unreached: int = Field(
        ge=0,
        default=0,
        description="Cases in the class beyond the slice bound (apply only). Untouched "
        "and unwritten, so they keep their place and head the next slice. Counted "
        "rather than named because `absent_cases` already names the whole class in the "
        "same order, and naming the tail again would double a ledger that is already "
        "one line per case",
    )
    remaining: int = Field(
        ge=0,
        description="The class the next slice would face — `absent` less the cases this "
        "run verified out of it. On an apply that is the unreached tail plus everything "
        "reached and not witnessed; on a dry run, which verifies nothing, it is the "
        "whole class",
    )
    store_unavailable: bool = Field(
        default=False,
        description="True when no content store transport could be built. Nothing is "
        "probed and nothing is written: with no store there is no prefix to read, and "
        "reporting every case as absent would name the whole population as a class this "
        "run could never repair. The command refuses on it",
    )
    refused: bool = Field(
        default=False,
        description="True when an apply was asked for with no slice bound. Nothing is "
        "probed and nothing is written, and the population is not even read. The command "
        "refuses ahead of this, so the field is the API caller's copy of that refusal",
    )


@dataclass(frozen=True)
class BlobDocumentCase:
    """One case's blob-side document holdings, as the population walk reads them."""

    case_id: str
    rows: int
    text_bytes: int


@dataclass
class _MirrorTally:
    """What one slice has recorded so far, accumulated across its cases."""

    attempted: list[str] = field(default_factory=list)
    verified: list[str] = field(default_factory=list)
    unverified: list[str] = field(default_factory=list)


def blob_document_cases(conn: sqlite3.Connection) -> tuple[BlobDocumentCase, ...]:
    """Every case the blob's ``documents`` table holds rows for, in ``case_id`` order.

    ``conn`` is a connection as :func:`~fedcourtsai.corpus.connect` returns it —
    the rows are subscripted by column name, so it owes a ``sqlite3.Row`` factory.

    A direct SQL read, not :func:`~fedcourtsai.corpus.documents_for_case`: under
    the corpus split that read is served by the content store, which is the side
    this pass exists because it is empty. The blob is the *pre-split-era* one
    here, and its table is the only place the text still is.

    ``LENGTH(CAST(text AS BLOB))`` is the byte count rather than
    ``LENGTH(text)``, which SQLite answers in characters on a TEXT value — the
    ledger states what the mirror would upload. A blob whose table predates the
    documents migration reads as an empty population rather than failing, the
    tolerance every corpus document read carries.
    """
    try:
        cur = conn.execute(
            "SELECT case_id, COUNT(*) AS rows, "
            "COALESCE(SUM(LENGTH(CAST(text AS BLOB))), 0) AS text_bytes "
            "FROM documents GROUP BY case_id ORDER BY case_id"
        )
    except Exception as exc:
        if "no such table" in str(exc).lower():
            return ()
        raise
    return tuple(
        BlobDocumentCase(
            case_id=str(record["case_id"]),
            rows=int(record["rows"]),
            text_bytes=int(record["text_bytes"]),
        )
        for record in cur
    )


def blob_documents_for_case(conn: sqlite3.Connection, case_id: str) -> list[corpus.CaseDocument]:
    """One case's documents read straight out of the blob's table, kind-ordered.

    ``conn`` is a :func:`~fedcourtsai.corpus.connect` connection, as above.
    The mirror's payload. Deliberately not the routed
    :func:`~fedcourtsai.corpus.documents_for_case`, for this module's whole
    reason: under the split that read answers from the content store, so
    mirroring what it returns would upload the emptiness this pass is repairing.
    """
    # `SELECT *`, not a bound column list, matching the corpus's own document
    # read: a blob predating a column must read as "no value" for that column
    # rather than failing the whole row.
    cur = conn.execute("SELECT * FROM documents WHERE case_id = ? ORDER BY kind", (case_id,))
    return [
        corpus.CaseDocument(
            case_id=record["case_id"],
            kind=record["kind"],
            url=record["url"],
            entry_date=record["entry_date"],
            fetched_at=date.fromisoformat(record["fetched_at"]),
            pages=int(record["pages"]),
            truncated=bool(record["truncated"]),
            # A blob packed before the marker existed holds only extractions, so
            # its absence reads as "not OCR" — the corpus read's own reading.
            ocr_derived=bool(_optional_flag(record, "ocr_derived")),
            text=record["text"],
        )
        for record in cur
    ]


def _optional_flag(record: sqlite3.Row, column: str) -> bool:
    """A boolean column an older blob may not carry at all, read as ``False``.

    The corpus's own reading of an optional column
    (:func:`fedcourtsai.corpus._optional_bool` and its siblings) is the rule of
    record, and this is the same route: a missing column raises out of the
    subscript rather than answering, and a row that predates it must read as
    "no value" instead of failing the whole document. Kept here rather than
    imported because the corpus's readers are private to that module and
    typed for its own row protocol.
    """
    try:
        value = record[column]
    except (KeyError, IndexError):
        return False
    return bool(value) if value is not None else False


def store_serves_documents(transport: casestore.ObjectTransport, case_id: str) -> bool:
    """Whether the content store would serve this case any document.

    The class predicate and, after a mirror, the verification — and deliberately
    the *production* read (:func:`~fedcourtsai.casestore.read_has_documents`,
    what :func:`~fedcourtsai.corpus.has_documents_for_case` answers from under
    the split) rather than a listing of the case's ``documents/`` prefix.

    The two disagree exactly where it matters. :func:`casestore.merge_documents`
    puts the text leaves before the manifest, so a mirror whose leaf PUT landed
    and whose manifest PUT did not leaves keys under the prefix and serves
    nothing: a listing would call that case verified, drop it from the class, and
    it would never be retried while production still read it as empty. The same
    reading also puts a case carrying only an *empty* manifest in the class,
    which is right for the same reason — the blob holds its text and the store
    serves none of it, which is the defect however the store came to look that
    way.
    """
    return casestore.read_has_documents(transport, case_id)


def mirror_stored_documents(
    conn: sqlite3.Connection,
    *,
    apply: bool,
    max_cases: int | None = None,
) -> DocumentMirrorResult:
    """Mirror the blob's document text for the cases the content store holds none of.

    The **dry run** probes every case the blob's ``documents`` table carries rows
    for and reports the class — unbounded, because the bound an apply is
    dispatched with is read off this ledger and a bounded one would describe a
    smaller class than the apply then acts on. It writes nothing.

    The **apply** takes the first ``max_cases`` of the class in ``case_id`` order
    and mirrors each case's blob rows through
    :func:`fedcourtsai.casestore.mirror_documents`. ``max_cases`` is required —
    an apply called without one is refused, nothing probed and nothing written —
    because a bound is the only thing standing between this pass and an
    unbounded upload of every case in the corpus.

    Each mirrored case is then **re-probed**. The mirror writer swallows every
    transport failure by design, so a run against a misaddressed store, expired
    credentials, or the out-of-band pointer override (which withholds mirrors
    outright) would otherwise report a clean slice having written nothing; the
    verified/unverified split is what makes the ledger answerable. An unverified
    case is not a failed repair, only an unwitnessed one: its blob rows are
    untouched, so it stays in the class and is retried at the head of the next
    slice.
    """
    if apply and max_cases is None:
        return DocumentMirrorResult(
            applied=False,
            cases_with_blob_documents=0,
            present=0,
            absent=0,
            remaining=0,
            refused=True,
        )
    population = blob_document_cases(conn)
    if not population:
        return DocumentMirrorResult(
            applied=apply, cases_with_blob_documents=0, present=0, absent=0, remaining=0
        )
    transport = casestore.active_transport()
    if transport is None:
        return DocumentMirrorResult(
            applied=apply,
            cases_with_blob_documents=len(population),
            present=0,
            absent=0,
            remaining=0,
            store_unavailable=True,
        )

    absent = [case for case in population if not store_serves_documents(transport, case.case_id)]
    slice_ = absent[:max_cases] if apply and max_cases is not None else []
    tally = _MirrorTally()
    for case in slice_:
        tally.attempted.append(case.case_id)
        documents = blob_documents_for_case(conn, case.case_id)
        # Best-effort by contract: this swallows a transport failure rather than
        # raising, so one unreachable case costs the maintainer that case and not
        # the whole slice. The re-probe below is what reports which it was.
        casestore.mirror_documents(documents)
        if store_serves_documents(transport, case.case_id):
            tally.verified.append(case.case_id)
        else:
            tally.unverified.append(case.case_id)
            logger.warning(
                "mirror-stored-documents: %s still lists no stored document after "
                "mirroring %d blob row(s) — the write was withheld or failed",
                case.case_id,
                len(documents),
            )
    unreached = len(absent) - len(slice_)
    return DocumentMirrorResult(
        applied=apply,
        cases_with_blob_documents=len(population),
        present=len(population) - len(absent),
        absent=len(absent),
        absent_cases={
            case.case_id: BlobDocuments(rows=case.rows, text_bytes=case.text_bytes)
            for case in absent
        },
        bound=max_cases if apply else None,
        attempted=tally.attempted,
        verified=tally.verified,
        unverified=tally.unverified,
        unreached=unreached,
        remaining=len(absent) - len(tally.verified),
    )
