"""The bounded document back-fill for queued cases holding no primary document.

A case reaches prediction with the document that opens it — the ``petition`` on
a cert-form docket, the ``application`` on an interim one — because
:func:`~fedcourtsai.pipeline.live.provision_documents` runs at the transition
that queues it. A case whose provisioning ran *before* the selector had an arm
for its filing type kept nothing: the fetch was attempted, selection came back
empty, and the row was queued with no primary document. Nothing in the fetching
lanes repairs that. The live poller re-fetches a kind only when its link
changes, and a kind that was never stored has no link to change; the case is
also decided or settled by now on most of the class, so the rotation has left
it. This is the pass that applies the current selector to the cases already past
their trigger.

- **Population.** Live-slice SCOTUS rows that are *predict-relevant* — queued
  for prediction or salience-selected — and hold no stored document of **their
  own docket form's** primary kind: an application-form row is measured against
  its ``application``, a cert-form row against its ``petition``. Form-keyed
  rather than petition-keyed because an application docket structurally never
  holds a petition, and a petition-keyed predicate would strand every
  application retrospectively. Predict-relevant rather than the whole
  distributed stock, which is overwhelmingly pre-2022 rows carrying no document
  links at all: this pass costs paced upstream round trips per case, and the
  cases that can mint a cell are the ones worth spending them on.
- **Route.** The provisioning path, re-keyed off the corpus row rather than off
  a live poll: parse the stored docket number to the ``(term, serial)`` the
  upstream endpoint addresses, fetch that docket's JSON **fresh**, and run the
  same :func:`~fedcourtsai.pipeline.documents.select_documents` and
  :func:`~fedcourtsai.pipeline.documents.fetch_case_documents` the poller runs.
  Fresh rather than from the stored snapshot because the question is whether the
  link is served *now* — a stored payload can name a URL upstream has since
  withdrawn, and a stored payload predating the filing names none at all.
- **Two floors, reported as floors.** A candidate whose docket carries the
  opening entry but posts no PDF behind it is a Rule 34.6 paper filing
  (``no_link``): the Court served nothing, so there is nothing to fetch, and no
  repair reaches it. A candidate whose docket carries no such entry at all
  (``no_entry``) is a legacy docket whose proceedings list holds no document
  links. Neither is a failure and neither drains. ``no_entry`` on a **modern**
  docket is the exception and the alarm: a docket whose filing the selector has
  an arm for reads as a selector regression, so those cases are named rather
  than counted.
- **Bounded twice.** ``max_cases`` is the *spend* cap — how many candidates one
  dispatch pays paced round trips for — and it is required on an apply. What
  keeps the run inside its caller's wall-clock cap is a slice-level deadline
  checked before each candidate, so a declined candidate is *unreached* rather
  than failed: untouched, unwritten, and at the head of the next slice. The dry
  run is bounded on both counts too, because it fetches the docket JSON — one
  paced GET per candidate is the whole diagnostic, and over a population in the
  thousands it is an hour of them.
- **Written per case.** Each case's documents are upserted as they are made, not
  batched at the end, so a step that hits its cap has banked what it recovered:
  under the corpus split the per-case content-store write is itself the durable
  one.

Additive by construction. :func:`fetch_case_documents` is idempotent against the
stored ``(kind, url)`` mapping, so a case that already holds a document at the
selected URL is not re-fetched, and a case this pass cannot recover keeps
exactly what it had and re-enters the next slice.
"""

from __future__ import annotations

import logging
import sqlite3
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .. import corpus
from ..supremecourt import (
    SupremeCourtClient,
    parse_scotus_application_number,
    parse_scotus_docket_number,
)
from .documents import (
    KIND_APPLICATION,
    KIND_PETITION,
    document_fetch_losses,
    fetch_case_documents,
    primary_entry_matched,
    reset_document_fetch_losses,
    select_documents,
)
from .prefetch import prefetch_by_case

logger = logging.getLogger(__name__)

# What one candidate is estimated to cost, which is what the slice deadline
# checks against what is left. The unit is the client's own politeness pacing
# (`SupremeCourtClient` throttles between requests and retries once on a
# transport failure), not compute: everything this pass does is a paced GET and
# a cheap parse.
#
# The docket JSON, fetched on every candidate in either mode.
ESTIMATED_DOCKET_SECONDS = 5.0
# One selected filing: the GET, the download, and the PDF text extraction.
ESTIMATED_DOCUMENT_SECONDS = 20.0
# How many documents an apply is charged for per candidate. The primary filing
# plus headroom for the opposition briefs `select_documents` returns beside it —
# a multi-respondent case draws one per respondent. A high estimate of the
# ordinary case rather than a ceiling: the deadline is what stops the slice
# taking new work, and the caller's own cap is the backstop for a candidate that
# runs past its estimate.
ESTIMATED_DOCUMENTS_PER_CASE = 3
# The Term from which a docket's proceedings list reliably carries document
# links, and so the line above which `no_entry` stops being a floor and starts
# being a selector regression. Below it the Clerk's JSON posts no links at all
# on most dockets and no selector arm can reach them; at or above it, a docket
# whose opening filing matched no entry is a filing shape the selector does not
# recognize, which is the alarm this pass exists to raise rather than absorb.
MODERN_LINK_TERM = 2022


class DocumentBackfillResult(BaseModel):
    """What one back-fill slice found, and wrote."""

    model_config = ConfigDict(extra="forbid")

    applied: bool = Field(description="Whether the pass wrote the documents or only counted them")
    cases_seen: int = Field(
        ge=0,
        description="Predict-relevant live-slice rows the walk read documents for "
        "at all — the denominator under `candidates`. Zero means the population "
        "could not be read rather than that the class is empty, so the caller "
        "refuses on it: a blob with no live slice, or a split-mode index pointed "
        "at no corpus at all, would otherwise report a clean pass over nothing",
    )
    cases_with_documents: int = Field(
        ge=0,
        description="Of `cases_seen`, the ones that served at least one stored "
        "document. The store-blind reading beside the denominator, and the "
        "opposite degradation: a split-mode index with no content store "
        "configured serves every case an empty document list, which makes every "
        "row in the population look like a gap. Zero against a non-zero "
        "`cases_seen` means the candidate list is an artifact of an unreadable "
        "store, not a class",
    )
    unaddressable: int = Field(
        ge=0,
        description="Rows in the gap class whose stored docket number no upstream "
        "endpoint can be asked about — a historical spelling (`A-9999`), a bare "
        "pre-1925 number. Counted apart from `candidates` and never admitted to a "
        "slice: this route cannot act on them, and one at the head would consume "
        "the bound of every dispatch forever",
    )
    candidates: int = Field(
        ge=0,
        description="Addressable rows in the gap class, in `case_id` order — the "
        "whole population this route can act on",
    )
    bound: int | None = Field(
        default=None,
        description="The per-dispatch slice size this run was bounded to. Set in "
        "both modes: a dry run writes nothing but still spends one paced docket "
        "GET per candidate, so it is bounded on the same terms",
    )
    attempted: int = Field(
        ge=0,
        description="Candidates this run fetched the docket JSON for — never more "
        "than `bound`, and short of it by the ones the slice deadline declined to start",
    )
    unreached: list[str] = Field(
        default_factory=list,
        description="Candidates inside the bound the slice deadline declined to "
        "start, in class order. Unreached, not failed: nothing was fetched or "
        "written for them, so they keep their place at the head of the class and "
        "head the next slice",
    )
    remaining: int = Field(
        ge=0,
        description="Candidates the run did not reach, plus those it reached and "
        "could not recover — the backlog the next slice would face",
    )
    stored: dict[str, int] = Field(
        default_factory=dict,
        description="Documents written by kind (apply only). Counts every kind "
        "`fetch_case_documents` produced for a recovered case, not only the "
        "primary one: the case was provisioned by the same call the poller makes, "
        "so the opposition briefs and the derived questions-presented row land with it",
    )
    recovered: int = Field(
        ge=0,
        default=0,
        description="Candidates that gained their **primary** document and so left "
        "the class (apply only) — the count `remaining` is the complement of. Not "
        "`len(documents)`: a candidate whose petition link was selected and then "
        "did not serve can still store the opposition briefs beside it, which is a "
        "write but not a recovery, and reporting those together would headline a "
        "slice as having recovered cases it left exactly where they were",
    )
    documents: dict[str, list[str]] = Field(
        default_factory=dict,
        description="case_id -> the kinds written for it, in `case_id` order "
        "(apply only): every case an applied slice stored anything for, which is a "
        "superset of the recovered ones",
    )
    selected: dict[str, list[str]] = Field(
        default_factory=dict,
        description="case_id -> the kinds selection nominated a link for (dry run "
        "only). The dry run's whole diagnostic: a case listed here is one the "
        "apply would fetch, and one absent from it is at a floor or a fetch loss",
    )
    no_link: int = Field(
        ge=0,
        description="Candidates whose docket carries the opening entry with no "
        "document link behind it — a Rule 34.6 paper filing the Court posted no "
        "PDF for. A **floor**, not a failure: there is nothing upstream to fetch, "
        "so no repair reaches these and the class does not drain past them",
    )
    no_entry: int = Field(
        ge=0,
        description="Candidates whose docket carries no opening entry the selector "
        "recognizes at all — a legacy docket whose proceedings list holds no "
        "document links. A **floor** on a pre-modern docket; on a modern one it is "
        "a selector regression, which `no_entry_modern_cases` names",
    )
    no_entry_modern_cases: list[str] = Field(
        default_factory=list,
        description="The `no_entry` candidates whose docket is modern enough that "
        "its proceedings list should carry links, in class order. Not a floor and "
        "not a count to accept: a filing shape the selector has no arm for, which "
        "is the class this pass exists to stop producing",
    )
    docket_unserved: int = Field(
        ge=0,
        description="Candidates whose docket JSON came back 404 — the row is "
        "addressable but upstream serves nothing there",
    )
    docket_errors: int = Field(
        ge=0,
        description="Candidates whose docket JSON fetch failed transport-side after "
        "the client's own retry. Apart from `docket_unserved` because the repairs "
        "differ: a transport failure is worth re-attempting, a 404 is not",
    )
    fetch_losses: dict[str, int] = Field(
        default_factory=dict,
        description="The document-fetch losses this pass recorded, by reason "
        "(`fedcourtsai.pipeline.documents.document_fetch_losses`), so a candidate "
        "that selected a link and still stored nothing is attributable. Zero-filled "
        "and always present, so an unlisted reason is never an omitted one",
    )
    refused: bool = Field(
        default=False,
        description="True when an apply was asked for with no slice bound. Nothing "
        "is fetched or written in that case, and the population is not even walked. "
        "The command refuses ahead of this, so the field is the API caller's copy of "
        "that refusal rather than a line a dispatch ledger carries",
    )


@dataclass(frozen=True)
class DocumentGap:
    """One case in the gap class, with what the route needs to address it."""

    case_id: str
    #: The kind this docket's form is measured against — the document that opens
    #: it, and the only one whose absence puts the row in this class.
    kind: str
    #: The upstream address, or ``None`` where the stored docket number parses to
    #: neither form (an unaddressable row, which never enters a slice).
    address: tuple[int, int, Literal["cert", "application"]] | None
    #: The Term the docket number belongs to, or ``None`` where it carries no
    #: parseable one — what decides whether a `no_entry` reading is a floor.
    term_year: int | None


@dataclass(frozen=True)
class DocumentGapScan:
    """What one walk of the predict-relevant population saw.

    ``cases_seen`` is the denominator and it is here for the reason the OCR
    recovery's is: zero candidates has two very different causes, a converged
    population and one this process cannot read. ``cases_with_documents`` is the
    inverted degradation — a store that serves no documents makes every row in
    the population look like a gap — and the caller reports both.
    """

    gaps: tuple[DocumentGap, ...]
    cases_seen: int
    cases_with_documents: int


def _primary_kind(row: corpus.CorpusRow) -> str:
    """The document that opens this docket, keyed on its form.

    The tolerant recognizer, matching the coverage report's own reading
    (:func:`~fedcourtsai.pipeline.documents.document_text_coverage`), so a case
    counted as a gap there and a case in this class are measured against the same
    kind. The *populations* are not identical and deliberately so: that report
    frames on the predict queue alone, while this pass adds the salience-selected
    arm, which is where a reserve-funded application reaches the predict path.
    The *strict* parser addresses the fetch (:func:`_address`); a row the tolerant
    recognizer calls an application and the strict one cannot address is
    unaddressable, not misclassified.
    """
    return (
        KIND_APPLICATION if corpus.is_scotus_application_form(row.docket_number) else KIND_PETITION
    )


def _address(row: corpus.CorpusRow) -> tuple[int, int, Literal["cert", "application"]] | None:
    """The ``(term, serial, form)`` the upstream JSON endpoint serves this row at.

    The selection sweep's own reading (:func:`~fedcourtsai.pipeline.live.sweep`):
    strip the display annotation once — it hides the docket from both parsers —
    then the cert parser, falling back to the application one. ``None`` where
    neither parses, which is a row this route cannot ask about at all.
    """
    addressable = corpus.strip_docket_annotation(row.docket_number)
    parsed = parse_scotus_docket_number(addressable)
    if parsed is not None:
        return parsed[0], parsed[1], "cert"
    parsed = parse_scotus_application_number(addressable)
    if parsed is not None:
        return parsed[0], parsed[1], "application"
    return None


def _term_year(row: corpus.CorpusRow) -> int | None:
    """The docket's Term year under whichever form parses it."""
    return corpus.scotus_term_year(row.docket_number) or corpus.scotus_application_term_year(
        row.docket_number
    )


def is_predict_relevant(row: corpus.CorpusRow) -> bool:
    """Whether a missing primary document on this row can still cost a cell.

    Queued for prediction, or selected by the salience gate and not yet queued.
    The selected arm is not redundant: a reserve-selected application has no
    distribution transition to be queued at and reaches the predict path through
    the selection sweep, so a petition-queued-only predicate would drop exactly
    the rows the reserve funds.
    """
    return row.predict_queued_at is not None or row.salience_selected


def document_gaps(conn: corpus.ReadConnection) -> DocumentGapScan:
    """Every predict-relevant row holding no primary document, in ``case_id`` order.

    Walked case by case rather than queried, because under the corpus-split mode
    the documents live in the per-case content store and the blob's own
    ``documents`` table holds none of them — a SQL predicate over that table
    would report an empty class against the corpus production reads.
    :func:`~fedcourtsai.corpus.documents_for_case` is the read that routes to
    whichever holds them.

    Ordering is the row order (``case_id``), which is what makes a bounded slice
    self-advancing: a recovered case leaves the class, so the next dispatch's
    slice starts where this one's population ran out.
    """
    rows = [
        row
        for row in corpus.iter_rows(conn, court="scotus", live_slice=True)
        if is_predict_relevant(row)
    ]
    by_case = {row.case_id: row for row in rows}
    gaps: list[DocumentGap] = []
    cases_seen = cases_with_documents = 0
    with prefetch_by_case(
        list(by_case),
        lambda case_id: corpus.documents_for_case(conn, case_id),
        thread_name_prefix="document-backfill",
    ) as fetched:
        for case_id, documents in fetched:
            cases_seen += 1
            if documents:
                cases_with_documents += 1
            row = by_case[case_id]
            kind = _primary_kind(row)
            if any(document.kind == kind for document in documents):
                continue
            gaps.append(
                DocumentGap(
                    case_id=case_id,
                    kind=kind,
                    address=_address(row),
                    term_year=_term_year(row),
                )
            )
    return DocumentGapScan(
        gaps=tuple(gaps), cases_seen=cases_seen, cases_with_documents=cases_with_documents
    )


def estimated_candidate_seconds(*, apply: bool) -> float:
    """The wall clock the slice deadline admits one candidate on.

    A fixed estimate rather than a per-candidate one, because nothing the corpus
    holds about a case in this class predicts its cost: the row stores no
    document, so there is no page count or byte size to read, and what the
    candidate will cost is exactly what its docket JSON turns out to nominate.
    A dry run is charged for the docket GET alone — it fetches no filings — and
    an apply for the filings the docket is assumed to carry beside it.
    """
    if not apply:
        return ESTIMATED_DOCKET_SECONDS
    return ESTIMATED_DOCKET_SECONDS + ESTIMATED_DOCUMENTS_PER_CASE * ESTIMATED_DOCUMENT_SECONDS


def _fetch_docket(
    client: SupremeCourtClient, gap: DocumentGap
) -> tuple[Mapping[str, Any] | None, str | None]:
    """This candidate's docket JSON, or ``None`` and the reason there is none.

    Every way the fetch can fail is a *reported reason* rather than a raise, for
    the reason the OCR recovery's re-fetch is: a slice must cost the maintainer
    one candidate when a docket is unreachable, not the whole dispatch.
    """
    assert gap.address is not None  # unaddressable gaps never enter a slice
    term, serial, form = gap.address
    try:
        payload = client.get_docket(term, serial, form=form)
    except httpx.HTTPError as exc:
        logger.warning("document-backfill: docket fetch failed for %s: %s", gap.case_id, exc)
        return None, "docket-error"
    if payload is None:
        return None, "docket-unserved"
    return payload, None


def backfill_documents(
    conn: sqlite3.Connection,
    *,
    client: SupremeCourtClient,
    apply: bool,
    char_cap: int,
    today: date,
    max_cases: int | None = None,
    deadline: float | None = None,
    monotonic: Callable[[], float] = time.monotonic,
) -> DocumentBackfillResult:
    """Re-run provisioning over the queued cases that hold no primary document.

    Both modes take a slice and both spend paced upstream round trips, which is
    what separates this pass from the ones whose dry run is free. The **dry run**
    fetches each candidate's docket JSON and runs
    :func:`~fedcourtsai.pipeline.documents.select_documents` over it — that is
    the whole diagnostic, and it is what separates a case with a link waiting for
    it from one at the ``no_link`` or ``no_entry`` floor — and fetches no filings
    and writes nothing. The **apply** goes on to fetch what selection nominated,
    through :func:`~fedcourtsai.pipeline.documents.fetch_case_documents`: the
    same call the live poller makes, so a recovered case is provisioned on
    exactly the terms a case provisioned at its trigger was.

    ``max_cases`` is the slice size, required on an apply and honored on a dry
    run too. It is a *spend* cap rather than a refusal threshold: each candidate
    costs paced round trips against the Court's own host, and a population in the
    thousands is a day of them, so a backlog clears across dispatches rather than
    in one long job. An apply called without one is **refused** — nothing is
    fetched and nothing is written — because a bound is the only thing standing
    between this pass and an unbounded fetch campaign.

    ``deadline`` is the slice's wall clock: a :func:`time.monotonic` reading the
    run must not start new work past. Before each candidate,
    :func:`estimated_candidate_seconds` is checked against what is left, and the
    first one that does not fit ends the slice — it and every candidate behind it
    are reported ``unreached``, untouched and unwritten. Stopping at the first
    decline rather than skipping ahead is deliberate: the class is in ``case_id``
    order, so declining in order puts the declined candidates at the head of the
    next slice with its whole budget in front of them. A candidate already
    started is *finished*, never killed, so the deadline is the last moment work
    may begin rather than the moment it stops, and the caller sizes it to leave
    room for whatever must still fit inside its own cap once the pass stops
    taking work. ``None`` is no deadline.

    Written per case as each is fetched rather than batched at the end, because
    the step that runs this has a wall-clock cap: a batched write turns a cap hit
    into a slice that recovered a dozen cases and stored none of them. Under the
    corpus split the per-case content-store write is itself the durable one, so
    that banks the work; against a self-contained blob the durable step is the
    pointer push the workflow makes after the pass, and a cap hit loses the slice
    however it was written.

    Additive and self-advancing on the recoverable class only. A recovered case
    leaves the class; a candidate at either floor, or one whose docket or filing
    the fetch did not return, keeps exactly what it had, stays in the class and
    sits at the head of the next slice. That is why the ledger reports the floors
    apart from the losses: a slice that clears its bound without draining the
    class is the expected reading once the recoverable half is gone, and only the
    floor counts say so.
    """
    if apply and max_cases is None:
        return DocumentBackfillResult(
            applied=False,
            cases_seen=0,
            cases_with_documents=0,
            unaddressable=0,
            candidates=0,
            attempted=0,
            remaining=0,
            no_link=0,
            no_entry=0,
            docket_unserved=0,
            docket_errors=0,
            fetch_losses=_loss_counts(),
            refused=True,
        )
    scan = document_gaps(conn)
    unaddressable = [gap for gap in scan.gaps if gap.address is None]
    candidates = [gap for gap in scan.gaps if gap.address is not None]
    for gap in unaddressable:
        logger.warning(
            "document-backfill: %s holds no %s and no addressable docket number",
            gap.case_id,
            gap.kind,
        )
    slice_ = candidates if max_cases is None else candidates[:max_cases]
    # Read apart from whatever else this process recorded, so the ledger's
    # `fetch_losses` are this slice's rather than the run's.
    reset_document_fetch_losses()

    tally = _SliceTally()
    unreached: list[str] = []

    for index, gap in enumerate(slice_):
        if deadline is not None:
            estimate = estimated_candidate_seconds(apply=apply)
            left = deadline - monotonic()
            if estimate > left:
                # The whole tail, not this one candidate: the class is in
                # `case_id` order and every candidate costs the same estimate, so
                # skipping ahead would buy nothing and lose the ordering that
                # makes the next slice pick up where this one stopped.
                unreached = [c.case_id for c in slice_[index:]]
                logger.warning(
                    "document-backfill: slice deadline reached with %.0fs left; "
                    "%d candidate(s) not started, first %s (~%.0fs)",
                    left,
                    len(unreached),
                    gap.case_id,
                    estimate,
                )
                break
        payload, refused = _fetch_docket(client, gap)
        if payload is None:
            if refused == "docket-unserved":
                tally.docket_unserved += 1
            else:
                tally.docket_errors += 1
            continue
        refs = [ref for ref in select_documents(payload) if ref.kind == gap.kind]
        if not refs:
            _record_floor(payload, gap, tally)
        elif not apply:
            tally.selected[gap.case_id] = [ref.kind for ref in refs]
        else:
            _store_case(conn, client, gap, payload, char_cap=char_cap, today=today, tally=tally)

    return DocumentBackfillResult(
        applied=apply,
        cases_seen=scan.cases_seen,
        cases_with_documents=scan.cases_with_documents,
        unaddressable=len(unaddressable),
        candidates=len(candidates),
        bound=max_cases,
        attempted=len(slice_) - len(unreached),
        unreached=unreached,
        recovered=len(tally.recovered),
        remaining=len(candidates) - len(tally.recovered),
        stored=dict(sorted(tally.stored.items())),
        documents=dict(sorted(tally.documents.items())),
        selected=dict(sorted(tally.selected.items())),
        no_link=tally.no_link,
        no_entry=tally.no_entry,
        no_entry_modern_cases=tally.no_entry_modern,
        docket_unserved=tally.docket_unserved,
        docket_errors=tally.docket_errors,
        fetch_losses=_loss_counts(),
    )


@dataclass
class _SliceTally:
    """What one slice has recorded so far, accumulated across its candidates."""

    stored: dict[str, int] = field(default_factory=dict)
    documents: dict[str, list[str]] = field(default_factory=dict)
    selected: dict[str, list[str]] = field(default_factory=dict)
    no_entry_modern: list[str] = field(default_factory=list)
    recovered: set[str] = field(default_factory=set)
    no_link: int = 0
    no_entry: int = 0
    docket_unserved: int = 0
    docket_errors: int = 0


def _record_floor(payload: Mapping[str, Any], gap: DocumentGap, tally: _SliceTally) -> None:
    """Attribute a candidate selection nominated nothing for, to its own floor.

    Told apart by the docket's own text: an entry the selector recognizes with no
    link behind it is a paper filing the Court posted no PDF for, while no entry
    at all is a docket carrying no document links to begin with. Neither drains —
    but only the second can also mean the selector is blind, which is why a
    modern docket landing there is named rather than counted.
    """
    if primary_entry_matched(payload, kind=gap.kind):
        tally.no_link += 1
        return
    tally.no_entry += 1
    if gap.term_year is not None and gap.term_year >= MODERN_LINK_TERM:
        tally.no_entry_modern.append(gap.case_id)
        logger.warning(
            "document-backfill: %s (OT%d) matched no %s entry — "
            "the selector has no arm for this filing type",
            gap.case_id,
            gap.term_year,
            gap.kind,
        )


def _store_case(
    conn: sqlite3.Connection,
    client: SupremeCourtClient,
    gap: DocumentGap,
    payload: Mapping[str, Any],
    *,
    char_cap: int,
    today: date,
    tally: _SliceTally,
) -> None:
    """Fetch one candidate's documents through the poller's own path and store them.

    Written here, per case, rather than batched by the caller: under the corpus
    split the content-store write is the durable one, so a step that hits its cap
    keeps what this case recovered. A case whose selected filing the fetch did
    not return stores nothing and is a *loss* rather than a floor —
    ``fetch_losses`` carries which one, recorded fetch-side.
    """
    stored_urls = {d.kind: d.url for d in corpus.documents_for_case(conn, gap.case_id)}
    fetched = fetch_case_documents(
        client, gap.case_id, payload, stored_urls=stored_urls, char_cap=char_cap, today=today
    )
    if not fetched:
        return
    corpus.upsert_documents(conn, fetched)
    kinds = sorted(document.kind for document in fetched)
    tally.documents[gap.case_id] = kinds
    for kind in kinds:
        tally.stored[kind] = tally.stored.get(kind, 0) + 1
    if any(document.kind == gap.kind for document in fetched):
        # The class is keyed on the primary document alone: a case that gained
        # only its opposition briefs is still in it.
        tally.recovered.add(gap.case_id)


def _loss_counts() -> dict[str, int]:
    """This pass's document-fetch losses, zero-filled and in a stable order."""
    losses = document_fetch_losses()
    return {
        "http-error": losses.http_error,
        "unavailable": losses.unavailable,
        "bio-empty": losses.bio_empty,
        "not-selected": losses.not_selected,
    }
