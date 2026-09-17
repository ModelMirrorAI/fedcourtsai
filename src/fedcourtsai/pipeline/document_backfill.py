"""The bounded document back-fill for queued cases holding a document gap.

A case reaches prediction with the document that opens it — the ``petition`` on
a cert-form docket, the ``application`` on an interim one — because
:func:`~fedcourtsai.pipeline.live.provision_documents` runs at the transition
that queues it, and a granted case reaches its merits moments with both sides'
merits advocacy because the selection sweep re-provisions it while a merits
event is open. A case whose provisioning ran *before* the selector had an arm
for its filing type kept nothing: the fetch was attempted, selection came back
empty, and the row was queued with no primary document. Nothing in the fetching
lanes repairs that. The live poller re-fetches a kind only when its link
changes, and a kind that was never stored has no link to change; the case is
also decided or settled by now on most of the class, so the rotation has left
it. This is the pass that applies the current selector to the cases already past
their trigger.

- **Population.** Live-slice SCOTUS rows that are *predict-relevant* — queued
  for prediction or salience-selected. Predict-relevant rather than the whole
  distributed stock, which is overwhelmingly pre-2022 rows carrying no document
  links at all: this pass costs paced upstream round trips per case, and the
  cases that can mint a cell are the ones worth spending them on.
- **The gap, in two arms.** A row is in the class for each kind it is missing
  that this route can reach.

  The **primary** arm measures every row against **its own docket form's**
  opening filing: an application-form row against its ``application``, a
  cert-form row against its ``petition``. Form-keyed rather than petition-keyed
  because an application docket structurally never holds a petition, and a
  petition-keyed predicate would strand every application retrospectively.

  The **merits** arm measures a *granted, briefed* row against
  :data:`MERITS_GAP_KINDS`, the per-side briefs on the merits. Granted-and-
  briefed rather than granted alone, and the second half is what makes the arm
  drain: ``merits_brief_filed`` is the date the respondent's merits brief
  reached the docket, so a row carrying it has both sides' opening briefs filed
  and there is something to fetch, while a granted row without it is either not
  yet briefed — a live case the selection sweep provisions at its next pass —
  or briefed in a shape no arm reads, which a fetch cannot fix either. A row can
  be in both arms at once, and is then one candidate missing up to three kinds.

  The **replies** are deliberately *not* gap kinds. Not every granted case is
  replied to, so a missing reply is the ordinary state of the docket rather than
  a gap, and keying the class on one would park every un-replied case in it
  forever. A reply is fetched all the same wherever the docket carries one,
  because the apply runs the whole selector over the candidate's payload.
- **Route.** The provisioning path, re-keyed off the corpus row rather than off
  a live poll: parse the stored docket number to the ``(term, serial)`` the
  upstream endpoint addresses, fetch that docket's JSON **fresh**, and run the
  same :func:`~fedcourtsai.pipeline.documents.select_documents` and
  :func:`~fedcourtsai.pipeline.documents.fetch_case_documents` the poller runs.
  Fresh rather than from the stored snapshot because the question is whether the
  link is served *now* — a stored payload can name a URL upstream has since
  withdrawn, and a stored payload predating the filing names none at all.
- **Two floors, reported as floors.** A candidate whose docket carries the entry
  for a kind it is missing but posts no fetchable PDF behind it is at the
  ``no_link`` floor: a Rule 34.6 paper filing the Court served nothing for, or —
  on a merits kind — a docket whose grant this reader cannot date, so the
  selector's stage bound can place no entry on the merits side of it. Either
  way there is nothing this route can fetch. A candidate whose docket carries no
  such entry for **any** missing kind (``no_entry``) is a legacy docket whose
  proceedings list holds no document links. Neither is a failure and neither
  drains, and the two counts partition the floored candidates.

  Because neither drains, neither is re-walked. An apply **stamps** the
  candidate it read at a floor — ``document_floor_probed_at`` on the corpus row
  — and the class holds a stamped candidate out while that stamp is no older
  than ``last_live_polled``, the live channel's own record of when it last read
  that same docket. A floor is then paid for once per docket version rather
  than once per dispatch, which is what lets a bounded slice reach the tail of
  the class at all: once the recoverable head has drained, the floors ahead of
  the tail are otherwise a paced docket GET each, every dispatch, forever. The
  stamp releases when the docket is next polled: a docket the live rotation
  still serves returns its candidate within a cycle, and one that has left the
  rotation — decided, or below its Term floor — does not, which is the terminal
  reading for a closed docket the Court served no PDF on. It is never silent
  either: ``standing_floors`` reports the held-out balance beside
  ``candidates``, so the whole class this route can address is readable off one
  ledger (``unaddressable`` sits outside both, as it always has).

  Two floors are **not** stamped. A candidate that raised the modern-docket
  alarm is one this pass may itself be the cause of — a filing shape the
  selector has no arm for — so recording it against the docket would bank an
  exclusion over a defect on our side, and it is exactly the shape an upstream
  payload that changed or degraded would produce across a whole slice. Widening
  the selector is then enough to recover those candidates; they never left.
  And only an **apply** stamps at all: a dry run writes nothing the lane pushes,
  so a stamp it wrote would be thrown away with the runner and the two modes
  would disagree about the class.

  The **alarm** cuts across both counts, because it is per *kind*: a missing kind
  the selector found no entry for, on a docket modern enough that its proceedings
  list should carry links, is a filing shape the selector has no arm for — the
  class this pass exists to stop producing rather than absorb. Those cases are
  named (``no_entry_modern_cases``) whichever floor they were counted at, so a
  granted case whose merits entries are on the docket and whose opening filing
  the selector cannot read is still named.
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
  one. The floor stamps are the other way round — index columns, durable only
  once the lane pushes the blob — so a slice cut short at its cap keeps its
  documents and loses its exclusions, which is the safe direction: the floors
  are simply re-read next dispatch.

Additive by construction. :func:`fetch_case_documents` is idempotent against the
stored ``(kind, url)`` mapping, so a case that already holds a document at the
selected URL is not re-fetched, and no case this pass touches loses anything it
had. What it re-enters the next slice with depends on why it did not recover: a
candidate whose docket or filing the fetch did not return keeps its place at the
head of the class, while an applied floor is stamped out of it until its docket
is polled again.
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
    KIND_MERITS_BRIEF_PETITIONER,
    KIND_MERITS_BRIEF_RESPONDENT,
    KIND_PETITION,
    document_fetch_losses,
    fetch_case_documents,
    merits_entry_matched,
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
# How many documents an apply is charged for per candidate. A high estimate of
# the ordinary candidate rather than a ceiling, and it reads the same for either
# arm of the class because `fetch_case_documents` is idempotent against the
# stored `(kind, url)` mapping — a candidate is charged only for what it is
# actually missing.
#
# A **primary**-arm candidate pays for the opening filing plus headroom for what
# `select_documents` returns beside it: the opposition briefs, one per
# respondent on a multi-respondent case. A **merits**-arm candidate already
# holds its petition, its opposition and its derived questions at unchanged
# URLs, so none of them is re-fetched; it pays for the two merits briefs, plus a
# reply per side where the docket carries one — at the estimate, or a filing or
# two past it.
#
# The candidate that **overruns** is the one in both arms at once: it pays for
# its opening filing, an opposition brief per respondent, and the merits stage on
# top, which runs to five or seven fetches against a charge of three. That is no
# longer the rarity it was — roughly one candidate in seven on the class as it
# stands. It is still left uncharged, because the deadline is a start gate and
# only the last-admitted candidate can run past it: the caller's own cap is the
# backstop, and sizing every ordinary candidate for the outlier would cost the
# slice far more than the overrun does.
#
# Left an estimate of the ordinary case deliberately, because the deadline is
# only what stops the slice taking *new* work and the caller's own cap is the
# backstop for a candidate that runs past it; sizing for the outlier would cost
# every ordinary candidate the difference.
ESTIMATED_DOCUMENTS_PER_CASE = 3
# The Term from which a docket's proceedings list reliably carries document
# links, and so the line above which `no_entry` stops being a floor and starts
# being a selector regression. Below it the Clerk's JSON posts no links at all
# on most dockets and no selector arm can reach them; at or above it, a docket
# whose opening filing matched no entry is a filing shape the selector does not
# recognize, which is the alarm this pass exists to raise rather than absorb.
MODERN_LINK_TERM = 2022
# The kinds the merits arm of the gap class is keyed on: each side's **opening**
# brief on the merits, and neither reply. A granted case that has been briefed
# has both of these on its docket by construction, so a missing one is a gap
# that a fetch can close; a reply exists only where the side chose to file one,
# so keying the class on a reply would hold every un-replied case in it forever.
# The replies still ride the apply, which runs the whole selector.
MERITS_GAP_KINDS: tuple[str, ...] = (
    KIND_MERITS_BRIEF_PETITIONER,
    KIND_MERITS_BRIEF_RESPONDENT,
)


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
        "population this route can act on now. Net of `standing_floors`: a "
        "candidate a previous apply read at a floor is held out until its docket "
        "is polled again, so `candidates + standing_floors` is the whole gap "
        "class this route can address — `unaddressable` sits outside both — and "
        "this is the part of it a slice would spend on",
    )
    standing_floors: int = Field(
        ge=0,
        default=0,
        description="Rows holding a document gap that a standing floor probe kept "
        "out of `candidates`: an apply already fetched that docket, found nothing "
        "fetchable behind any kind the row is missing, and stamped it, and the "
        "live channel has not re-read the docket since. Held out rather than "
        "re-walked because re-fetching an unchanged docket spends a paced round "
        "trip to learn the same thing, and a class that re-pays its floors every "
        "dispatch never reaches its own tail. A standing balance and not a "
        "backlog — the next poll of a docket returns its candidate to "
        "`candidates`",
    )
    merits_candidates: int = Field(
        ge=0,
        default=0,
        description="Of `candidates`, the ones missing at least one merits brief "
        "— a granted, respondent-briefed row whose per-side briefs on the merits "
        "were never fetched. Reported apart because the two arms of the class "
        "cost and drain differently and a single total hides which one a dispatch "
        "would be spending on: a merits candidate already holds its cert-stage "
        "documents and pays only for what the merits stage added, while a primary "
        "candidate pays for the filing that opens the docket and everything "
        "selection returns beside it. A candidate in both arms is counted here "
        "and in `candidates` once",
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
        "could not recover and did not stamp — the class the next slice would "
        "face. Net of `floors_stamped` as well as `recovered`, because a stamped "
        "floor leaves `candidates` exactly as a recovered case does; that is what "
        "keeps this equal to the walk-only re-read the lane makes its witness",
    )
    floors_stamped: int = Field(
        ge=0,
        default=0,
        description="Candidates this slice read at a floor and stamped, so the "
        "next scan holds them out (apply only — a dry run writes nothing). Short "
        "of `no_link + no_entry` by the floors the modern-docket alarm fired on, "
        "which are never stamped. It is what this slice **added** to the "
        "held-out balance, not part of the `standing_floors` printed beside it: "
        "that count is read off the scan this slice started from, so these show "
        "up in the next walk's",
    )
    stored: dict[str, int] = Field(
        default_factory=dict,
        description="Documents written by kind (apply only). Counts every kind "
        "`fetch_case_documents` produced for a recovered case, not only the ones "
        "whose absence put it in the class: the case was provisioned by the same "
        "call the poller makes, so the opposition briefs, the derived "
        "questions-presented row and any merits reply land with it",
    )
    recovered: int = Field(
        ge=0,
        default=0,
        description="Candidates that gained **every** kind they were missing and "
        "so left the class (apply only) — the count `remaining` is the complement "
        "of. Not `len(documents)`: a candidate whose petition link was selected "
        "and then did not serve can still store the opposition briefs beside it, "
        "and one that gained a single merits brief of the two still owes the "
        "other; both are writes and neither is a recovery, and reporting them "
        "together would headline a slice as having recovered cases it left "
        "exactly where they were",
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
        description="Candidates whose docket carries an entry for at least one "
        "kind they are missing with nothing fetchable behind it — a Rule 34.6 "
        "paper filing the Court posted no PDF for, or, on a merits kind, a grant "
        "this reader cannot date, so the selector's stage bound places no entry "
        "on the merits side of it. A **floor**, not a failure: there is nothing "
        "this route can fetch, so no repair reaches these and the class does not "
        "drain past them",
    )
    no_entry: int = Field(
        ge=0,
        description="Candidates whose docket carries no entry the selector "
        "recognizes for **any** kind they are missing — a legacy docket whose "
        "proceedings list holds no document links. A **floor** on a pre-modern "
        "docket. The two counts partition the floored candidates, so a candidate "
        "carrying an entry for one missing kind and none for another is counted "
        "in `no_link` here and still named in `no_entry_modern_cases` below",
    )
    no_entry_modern_cases: list[str] = Field(
        default_factory=list,
        description="Candidates carrying a missing kind the selector found no "
        "entry for at all, on a docket modern enough that its proceedings list "
        "should carry links, in class order. Not a floor and not a count to "
        "accept: a filing shape the selector has no arm for, which is the class "
        "this pass exists to stop producing. Read per **kind**, not per "
        "candidate, so a case whose merits entries are on the docket and whose "
        "opening filing is unreadable is named here even though its count went "
        "to `no_link` — the alarm would otherwise be silenced by whichever kind "
        "did match",
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
    #: Every kind this row is missing that this route can reach, in provisioning
    #: order: its own docket form's opening document, and — on a granted, briefed
    #: row — each side's absent merits brief. The case leaves the class when it
    #: holds them all, so recovery is measured against the whole tuple.
    kinds: tuple[str, ...]
    #: The upstream address, or ``None`` where the stored docket number parses to
    #: neither form (an unaddressable row, which never enters a slice).
    address: tuple[int, int, Literal["cert", "application"]] | None
    #: The Term the docket number belongs to, or ``None`` where it carries no
    #: parseable one — what decides whether a `no_entry` reading is a floor.
    term_year: int | None

    @property
    def merits(self) -> bool:
        """Whether any of the missing kinds is a merits one."""
        return any(kind in MERITS_GAP_KINDS for kind in self.kinds)


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
    #: Rows holding a gap that a standing floor probe kept out of ``gaps``. The
    #: class is ``gaps`` plus these, and the split is what makes an excluding
    #: scan honest: a slice spends on ``gaps``, and this says how much of the
    #: class it is not looking at and why.
    standing_floors: int = 0


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


def is_merits_relevant(row: corpus.CorpusRow) -> bool:
    """Whether this row's merits briefs are a gap a fetch can close.

    Granted **and** briefed, both read off the corpus row rather than a payload,
    so the walk stays a row read plus a document read per case.

    ``date_cert_granted`` is the stage: nothing selects a merits filing before a
    cert grant, so an ungranted row has no merits gap to be in.
    ``merits_brief_filed`` — the date the respondent's brief on the merits
    reached the docket — is what makes the arm *drain*. A row carrying it has
    both sides' opening briefs filed, so a missing kind is a document waiting to
    be fetched. A granted row without it is one of two things, and a fetch helps
    neither: a case still being briefed, which the selection sweep provisions at
    its next pass while its merits event is open, or a case whose briefing is
    recorded in a shape :mod:`~fedcourtsai.pipeline.merits_signals` does not
    read — in which case the selector will not read it either and the row would
    sit at a floor in this class forever.
    """
    return row.date_cert_granted is not None and row.merits_brief_filed is not None


def is_predict_relevant(row: corpus.CorpusRow) -> bool:
    """Whether a document gap on this row can still cost a cell.

    Queued for prediction, or selected by the salience gate and not yet queued.
    The selected arm is not redundant: a reserve-selected application has no
    distribution transition to be queued at and reaches the predict path through
    the selection sweep, so a petition-queued-only predicate would drop exactly
    the rows the reserve funds.
    """
    return row.predict_queued_at is not None or row.salience_selected


def floor_probe_standing(row: corpus.CorpusRow) -> bool:
    """Whether this row's stored floor reading still speaks for its docket.

    The pass reads a floor off a docket it fetched *fresh*, so the reading is
    about one version of that docket: nothing on it is fetchable behind the
    kinds this row is missing. It stays true until the docket moves, and
    ``last_live_polled`` is the corpus's own record of when the live channel
    last read that same supremecourt.gov docket — so a stamp no older than it
    means no channel has looked at the docket since the probe, and re-fetching
    it would spend a paced round trip to reach the same verdict.

    ``last_live_polled`` rather than the stored snapshot's date. The same poll
    writes both, and the stamp additionally advances on the polls that retrieved
    nothing to store (a withdrawn docket, an unaddressable number), so it is an
    upper bound on when the docket could have moved — the safe side. The column
    is also already on the row this pass's walk hydrates, while under the corpus
    split a per-case snapshot read is a content-store round trip, one per
    candidate, on a walk that already pays one for the documents. And rather
    than ``last_pulled``, which is the CourtListener rotation's stamp: it is
    NULL on almost every live-minted row and says nothing about the Clerk's
    docket even where it is set.

    The comparison is deliberately the conservative one. ``last_live_polled``
    advances on *every* poll, change or not, so an unchanged docket that was
    re-polled costs one re-probe; the alternative — missing a change — costs a
    case its documents. Equal dates read as standing, so a poll landing after
    the probe on the probe's own day waits for the next poll; that is one
    deferred re-probe on a class whose rotation is measured in weeks.

    What the stamp accepts, said rather than hidden: the Court sometimes posts a
    filing's PDF after the entry that names it, so a ``no_link`` read a day early
    is a floor that was about to stop being one. On a docket the rotation still
    serves that costs nothing — the next poll releases it. On one that has left
    the rotation it is terminal, and the case keeps the gap. The trade is
    deliberate and it is the whole point: the floors are the thousand paced GETs
    standing between a bounded slice and the candidates behind them, and holding
    the cases that can still mint a cell out of reach costs more than a decided
    docket's late-posted filing does.

    How long a probe stands is therefore the live rotation's business, not this
    pass's. A docket the rotation still serves — undecided, with an open event,
    at or above its Term floor — comes back within a cycle. One that has left it
    never does, and the stamp stands until something re-polls the case. That is
    the right reading for the class this pass mostly holds, which is closed
    dockets the Court served no PDF on: nothing further will be filed and no
    number of re-probes will find a link. It is also the reading to remember
    when the selector gains an arm it lacked, because the candidates a previous
    slice floored on that arm would stay held out — which is why a floor the
    modern-docket alarm fired on is never stamped in the first place.

    A row with no live-poll stamp is not held out. It cannot arise in this
    pass's population (the walk is ``live_slice=True``, which *is* that column
    being set), and if it ever did, re-probing costs a GET where excluding
    forever costs the case.
    """
    probed = row.document_floor_probed_at
    if probed is None:
        return False
    return row.last_live_polled is not None and probed >= row.last_live_polled


def document_gaps(conn: corpus.ReadConnection) -> DocumentGapScan:
    """Every predict-relevant row holding a reachable document gap, in ``case_id`` order.

    Walked case by case rather than queried, because under the corpus-split mode
    the documents live in the per-case content store and the blob's own
    ``documents`` table holds none of them — a SQL predicate over that table
    would report an empty class against the corpus production reads.
    :func:`~fedcourtsai.corpus.documents_for_case` is the read that routes to
    whichever holds them.

    A row whose floor probe still stands (:func:`floor_probe_standing`) holds a
    gap but is **not** a candidate: it is counted in ``standing_floors`` and left
    out of ``gaps``. That is the second half of what makes a bounded slice
    self-advancing, and the load-bearing half once the recoverable cases are
    gone — a floor cannot be recovered, so without it the class would present
    the same paced docket GETs to every dispatch and a slice would never walk
    past them to the cases behind.

    Ordering is the row order (``case_id``), which is what makes a bounded slice
    self-advancing: a recovered case leaves the class, so the next dispatch's
    slice starts where this one's population ran out. The two arms are **not**
    ordered apart, and deliberately: sorting the class by arm would be a policy
    about which gap matters more, and neither does uniformly — a merits gap is on
    a case whose moment has passed, a primary gap on one that may still be minted
    over. Row order leaves the composition of a slice to the corpus rather than
    encoding a preference here, and the ledger's arm split is what reports it.
    """
    rows = [
        row
        for row in corpus.iter_rows(conn, court="scotus", live_slice=True)
        if is_predict_relevant(row)
    ]
    by_case = {row.case_id: row for row in rows}
    gaps: list[DocumentGap] = []
    cases_seen = cases_with_documents = standing_floors = 0
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
            stored = {document.kind for document in documents}
            primary = _primary_kind(row)
            missing: list[str] = []
            if primary not in stored:
                missing.append(primary)
            if is_merits_relevant(row):
                missing.extend(kind for kind in MERITS_GAP_KINDS if kind not in stored)
            if not missing:
                continue
            if floor_probe_standing(row):
                standing_floors += 1
                continue
            gaps.append(
                DocumentGap(
                    case_id=case_id,
                    kinds=tuple(missing),
                    address=_address(row),
                    term_year=_term_year(row),
                )
            )
    return DocumentGapScan(
        gaps=tuple(gaps),
        cases_seen=cases_seen,
        cases_with_documents=cases_with_documents,
        standing_floors=standing_floors,
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
    """Re-run provisioning over the queued cases that hold a document gap.

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

    Additive, and self-advancing on both halves of the class. A recovered case
    leaves it by holding every kind it was missing. A candidate at either floor
    leaves it by being **stamped** (:func:`_stamp_floor`) against the docket
    version its floor was read on, and re-enters when that docket is next polled
    — so a floor costs the class one paced docket GET per docket version rather
    than one per dispatch, and the candidates behind a thousand of them are
    reachable inside a bounded slice. A floor the modern-docket alarm fired on
    is the exception and keeps its place, because that reading is about this
    pass rather than about the docket. Only a candidate whose docket or filing
    the fetch did not return keeps exactly what it had and its place at the head
    of the next slice, which is what a transport failure should do. The ledger
    reports the floors apart from the losses, and the stamped ones apart again:
    a slice that clears its bound without draining the class is the expected
    reading once the recoverable half is gone, and the counts are what say so.
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
            ", ".join(gap.kinds),
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
        refs = [ref for ref in select_documents(payload) if ref.kind in gap.kinds]
        if not refs:
            alarmed = _record_floor(payload, gap, tally)
            # A floor the alarm fired on is not stamped. That reading is a
            # missing kind the selector matched no entry for on a docket modern
            # enough to carry links — which is this pass's own blind spot rather
            # than the docket's last word, and the class it exists to stop
            # producing. Stamping it would bank an exclusion over a defect on our
            # side, and the same shape is what an upstream payload that changed
            # or degraded would produce across a whole slice: the candidates a
            # selector regression floors stay in the class, so widening the
            # selector is all that is needed to recover them.
            if apply and not alarmed:
                _stamp_floor(conn, gap, today=today, tally=tally)
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
        standing_floors=scan.standing_floors,
        merits_candidates=sum(1 for gap in candidates if gap.merits),
        bound=max_cases,
        attempted=len(slice_) - len(unreached),
        unreached=unreached,
        recovered=len(tally.recovered),
        # Both subtractions are the same fact: a candidate that left the class.
        # A recovered one left by gaining every kind it was missing, a stamped
        # one by having its floor recorded against the docket version it was
        # read on, and the next scan will see neither. The lane's witness is a
        # walk-only re-read compared against this number, so a stamp missing
        # here would read as an apply that failed to converge.
        remaining=len(candidates) - len(tally.recovered) - tally.floors_stamped,
        floors_stamped=tally.floors_stamped,
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
    floors_stamped: int = 0
    docket_unserved: int = 0
    docket_errors: int = 0


def _entry_matched(payload: Mapping[str, Any], *, kind: str) -> bool:
    """Whether the docket carries this kind's entry at all, link or no link.

    The two readers behind it answer for their own halves of the class and
    nothing else (:func:`~fedcourtsai.pipeline.documents.primary_entry_matched`,
    :func:`~fedcourtsai.pipeline.documents.merits_entry_matched`), so an
    unrecognized kind reads ``False`` — the alarming side, which is right: a kind
    this pass put a case in the class for and cannot then measure is a defect
    worth surfacing, not one to absorb.
    """
    if kind in MERITS_GAP_KINDS:
        return merits_entry_matched(payload, kind=kind)
    return primary_entry_matched(payload, kind=kind)


def _record_floor(payload: Mapping[str, Any], gap: DocumentGap, tally: _SliceTally) -> bool:
    """Attribute a candidate selection nominated nothing for, to its own floor.

    Returns whether this candidate raised the modern-docket **alarm**, which the
    caller reads to decide whether the floor may be stamped: a floor this pass
    may be the cause of is not one to record against the docket.

    Told apart by the docket's own text: an entry the selector recognizes with no
    fetchable link behind it is a filing the Court posted no PDF for, while no
    entry at all is a docket carrying no document links to begin with. Neither
    drains — but only the second can also mean the selector is blind, which is
    why a modern docket landing there is named rather than counted.

    The two **counts** are per candidate, because they size a class: a candidate
    missing several kinds is one candidate and takes one floor, reading
    ``no_link`` if the docket carries an entry for **any** of them. Otherwise a
    granted case whose petition-era entry predates the link window and whose
    merits briefs are on the docket would be counted at both floors at once, and
    the class sizes would stop adding up against ``attempted``.

    The **alarm** is per *kind*, and deliberately not per candidate. A filing
    shape the selector cannot read on a modern docket is a regression whichever
    other kinds that docket happens to post, so a candidate whose merits entries
    are there and whose opening entry is not is named here even though its count
    went to ``no_link``. Folding the alarm into the count instead would hide
    exactly the case the alarm exists for behind the one kind that did match.
    """
    unmatched = [kind for kind in gap.kinds if not _entry_matched(payload, kind=kind)]
    if len(unmatched) < len(gap.kinds):
        tally.no_link += 1
    else:
        tally.no_entry += 1
    if unmatched and gap.term_year is not None and gap.term_year >= MODERN_LINK_TERM:
        tally.no_entry_modern.append(gap.case_id)
        logger.warning(
            "document-backfill: %s (OT%d) matched no %s entry — "
            "the selector has no arm for this filing type",
            gap.case_id,
            gap.term_year,
            ", ".join(unmatched),
        )
        return True
    return False


def _stamp_floor(
    conn: sqlite3.Connection,
    gap: DocumentGap,
    *,
    today: date,
    tally: _SliceTally,
) -> None:
    """Record that this candidate's docket was read at a floor today.

    A column write through :func:`~fedcourtsai.corpus.stamp_document_floor_probe`
    rather than a row upsert, and that is load-bearing under the corpus split
    rather than a style choice: the population is read off the payload-free
    index, so a row in hand carries no opinion body, and upserting it back would
    re-mirror a body-less ``case.json`` over the one the content store holds —
    deleting the body while ``has_opinion`` stays latched. The class is granted
    and decided cases, which is precisely where the enrichment lands bodies.

    Stamped per case as the floor is read rather than batched at the end of the
    slice, matching the per-case document writes: the step that runs this has a
    wall-clock cap, and a batched stamp turns a cap hit into a slice that walked
    a thousand floors and recorded none of them. The stamps are index columns,
    so the durable step for them is the lane's pointer push rather than the
    content-store write that banks the documents.

    Apply-only, decided by the caller. The stamp lives in the index, which the
    lane pushes only after an apply, so a dry run's would be discarded with the
    runner — and a dry run that quietly moved the class its own ledger reports
    would be worse than one that spends the round trips.
    """
    corpus.stamp_document_floor_probe(conn, gap.case_id, today)
    tally.floors_stamped += 1


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
    if set(gap.kinds) <= set(kinds):
        # Recovery is leaving the class, so it is measured against **every** kind
        # the candidate was missing: a case that gained only its opposition
        # briefs, or only one of its two merits briefs, is still in the class and
        # still at the head of the next slice. Nothing in `gap.kinds` can be
        # skipped as already-stored here — the scan put the case in the class
        # precisely because none of them was stored — so the fetched set is the
        # whole of what this candidate gained.
        tally.recovered.add(gap.case_id)


def _loss_counts() -> dict[str, int]:
    """This pass's document-fetch losses, zero-filled and in a stable order."""
    losses = document_fetch_losses()
    return {
        "http-error": losses.http_error,
        "unavailable": losses.unavailable,
        "off-host": losses.off_host,
        "bio-empty": losses.bio_empty,
        "not-selected": losses.not_selected,
    }
